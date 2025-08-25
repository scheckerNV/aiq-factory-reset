"""
DGX AI Factory Analysis: LangGraph-based tools and orchestrator

Implements DGX-specific RAG tools, node assessment/readers, and a
LangGraph orchestrator that wraps a ReAct agent to: analyze state →
decide actions → produce BCM commands → execute with approval →
return final result with reasoning steps.
"""

import asyncio
import logging
import os
import re
import shlex
from pathlib import Path
from typing import TypedDict

from pydantic import Field

from aiq.builder.builder import Builder
from aiq.builder.framework_enum import LLMFrameworkEnum
from aiq.builder.function_info import FunctionInfo
from aiq.cli.register_workflow import register_function
from aiq.data_models.function import FunctionBaseConfig

logger = logging.getLogger(__name__)

# Default timeouts and limits
REMOTE_CMD_TIMEOUT = 120
LOCAL_CMD_TIMEOUT = 300
LLM_STEP_TIMEOUT = 90
MAX_FILE_READ_CHARS = 262_144  # 256 KiB approx


def _truncate_text(text: str, limit: int = MAX_FILE_READ_CHARS) -> str:
    if not isinstance(text, str):
        return text
    if len(text) <= limit:
        return text
    return text[:limit] + "\n...[truncated]...\n"


# ANSI escape sequence pattern for cleaning terminal output
ANSI_ESCAPE = re.compile(r'\x1B[[0-?][ -/][@-~]')


def _strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text"""
    if not text:
        return text
    return ANSI_ESCAPE.sub('', text)


def _extract_cmsh_commands(text: str) -> list[str]:
    import re
    cmds: list[str] = []
    in_code_block = False

    # Log the raw LLM output for debugging
    logger.info("🔍 Raw LLM output for command extraction:")
    logger.info("=" * 50)
    logger.info("%s", text[:1000] + ("..." if len(text) > 1000 else ""))
    logger.info("=" * 50)

    for line in (text or "").splitlines():
        original_line = line
        line = line.strip()

        # Handle code blocks
        if line.startswith("```") or line.startswith("~~~"):
            in_code_block = not in_code_block
            continue

        # Skip empty lines
        if not line:
            continue

        # Remove bullet points, numbering, and common prefixes
        line = re.sub(r'^(?:[-*•]\s*|\d+[.)]\s*|[a-zA-Z][.)]\s*)', '', line)

        # Remove backticks
        if line.startswith('`') and line.endswith('`') and len(line) > 2:
            line = line[1:-1].strip()

        # Normalize quotes (smart quotes to regular quotes)
        line = line.replace('"', '"').replace('"', '"').replace("'", "'").replace("'", "'")

        # More flexible cmsh pattern matching
        cmsh_pattern = re.compile(r'^cmsh\s+-c\s+["\']([^"\']+)["\']', re.IGNORECASE)
        match = cmsh_pattern.match(line)

        if match:
            # Standardize to double quotes
            cmd = f'cmsh -c "{match.group(1)}"'
            cmds.append(cmd)
            logger.info("✅ Extracted command: %s", cmd)
        elif line.lower().startswith('cmsh'):
            logger.info("⚠️  Found cmsh line but couldn't parse: %s", original_line)

    logger.info("🎯 Total commands extracted: %d", len(cmds))
    return cmds


# ========================
# DGX Documentation RAG Tool
# ========================


class DGXExpertRAGConfig(FunctionBaseConfig, name="dgx_expert_rag"):
    """Search DGX documentation using accurate RAG retrieval"""

    docs_path: str = Field(
        default="examples/factory_reset/src/aiq_dgx_factory_reset/docs/dgx_expert",
        description="Path to DGX documentation directory",
    )
    persist_dir: str = Field(
        default="examples/factory_reset/storage/dgx_index",
        description="Directory to persist the vector index",
    )
    similarity_top_k: int = Field(default=5, description="Top-K chunks to retrieve")
    response_mode: str = Field(default="tree_summarize", description="Response synthesis mode")
    nvidia_api_key: str = Field(default="", description="NVIDIA API key (or set NVIDIA_API_KEY env var)")
    llama_cloud_api_key: str = Field(default="", description="LlamaCloud API key for PDF parsing (optional)")


@register_function(config_type=DGXExpertRAGConfig)
async def dgx_expert_rag(config: DGXExpertRAGConfig, _builder: Builder):  # noqa: ARG001

    async def _search_dgx_docs(query: str) -> str:
        # Minimal mode: disable heavy RAG to avoid blocking and complexity during bring-up
        return ("DGX Documentation RAG disabled (minimal workflow mode).\n"
                f"Query: {query}")

    yield FunctionInfo.from_fn(_search_dgx_docs,
                               description="DGX hardware operational guidance and procedures (RAG over DGX docs)")


print("✅ DGX Expert RAG tool registered successfully")

# ========================
# DGX Node Assessment Tool
# ========================


class NodeAssessmentToolConfig(FunctionBaseConfig, name="node_assessment_tool"):
    cluster_host: str = Field(description="Cluster head hostname/IP for SSH (or localhost)")
    cluster_user: str = Field(description="SSH username for cluster access")
    timeout: int = Field(default=300, description="Assessment timeout in seconds")


@register_function(config_type=NodeAssessmentToolConfig)
async def node_assessment_tool(config: NodeAssessmentToolConfig, _builder: Builder):

    async def _run_node_assessment(input_text: str) -> str:  # noqa: ARG001
        """Upload and execute the dedicated node_assessment.sh script; return results dir."""
        import asyncio
        import tempfile

        try:
            script_path_on_disk = str(Path(__file__).resolve().parents[2] / "scripts" / "node_assessment.sh")
            if not os.path.exists(script_path_on_disk):
                return f"❌ node_assessment.sh not found at {script_path_on_disk}"

            # Read the shell script content from the external file (same as network assessment)
            with open(script_path_on_disk, "r", encoding="utf-8") as f:
                script_content = f.read()

            # Use tempfile approach like network assessment tool
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(script_content)
                script_path = f.name

            # Make executable
            os.chmod(script_path, 0o755)

            if config.cluster_host == "localhost":
                # Execute locally using the tempfile (same pattern as network tool remote execution)
                cmd = ["/bin/bash", script_path]
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=config.timeout)

                # Clean up tempfile
                os.unlink(script_path)

                if proc.returncode == 0:
                    s_out = stdout.decode("utf-8", errors="replace")
                    lines = [ln for ln in s_out.strip().splitlines() if ln.strip()]
                    outdir = None
                    for ln in reversed(lines):
                        m = re.search(r"(/tmp/node_assessment_[0-9_]+)", ln)
                        if m:
                            outdir = m.group(1)
                            break
                    if not outdir and lines:
                        outdir = lines[-1].strip()
                    return (f"✅ Node assessment completed successfully!\n\n"
                            f"Assessment Output:\n{s_out.strip()}\n\n"
                            f"Results saved in: {outdir}\n"
                            f"Use node_results_reader to analyze the detailed results.")
                else:
                    s_err = stderr.decode("utf-8", errors="replace")
                    return f"❌ Local assessment failed:\n{s_err.strip()}"
            else:
                # Remote execution (same as network assessment)
                scp_cmd = ["scp", script_path, f"{config.cluster_user}@{config.cluster_host}:/tmp/node_assessment.sh"]

                scp_process = await asyncio.create_subprocess_exec(*scp_cmd,
                                                                   stdout=asyncio.subprocess.PIPE,
                                                                   stderr=asyncio.subprocess.PIPE)
                await scp_process.communicate()

                if scp_process.returncode != 0:
                    os.unlink(script_path)  # Clean up tempfile
                    return "❌ Failed to upload assessment script to cluster"

                # Execute script on cluster
                ssh_cmd = [
                    "ssh",
                    f"{config.cluster_user}@{config.cluster_host}",
                    "chmod +x /tmp/node_assessment.sh && /tmp/node_assessment.sh"
                ]

                ssh_process = await asyncio.create_subprocess_exec(*ssh_cmd,
                                                                   stdout=asyncio.subprocess.PIPE,
                                                                   stderr=asyncio.subprocess.PIPE)

                stdout, stderr = await asyncio.wait_for(ssh_process.communicate(), timeout=config.timeout)

                # Clean up local tempfile
                os.unlink(script_path)

                if ssh_process.returncode == 0:
                    s_out = stdout.decode("utf-8", errors="replace")
                    lines = [ln for ln in s_out.strip().splitlines() if ln.strip()]
                    outdir = None
                    for ln in reversed(lines):
                        m = re.search(r"(/tmp/node_assessment_[0-9_]+)", ln)
                        if m:
                            outdir = m.group(1)
                            break
                    if not outdir and lines:
                        outdir = lines[-1].strip()
                    return (f"✅ Node assessment completed successfully!\n\n"
                            f"Assessment Output:\n{s_out.strip()}\n\n"
                            f"Results saved on cluster: {outdir}\n"
                            "Use the node_results_reader tool to analyze the results.")
                else:
                    s_err = stderr.decode("utf-8", errors="replace")
                    return f"❌ Assessment script failed:\n{s_err.strip()}"

        except asyncio.TimeoutError:
            return f"❌ Assessment timed out after {config.timeout} seconds"
        except Exception as e:  # noqa: BLE001
            return f"❌ Assessment error: {str(e)}"

    yield FunctionInfo.from_fn(_run_node_assessment, description="Run DGX node assessment on the cluster")


print("✅ DGX Node Assessment tool registered successfully")

# ========================
# DGX Node Results Reader Tool
# ========================


class NodeResultsReaderConfig(FunctionBaseConfig, name="node_results_reader"):
    cluster_host: str = Field(description="Cluster head hostname/IP for SSH (or localhost)")
    cluster_user: str = Field(description="SSH username for cluster access")
    results_directory: str = Field(default="/tmp/node_assessment_*",
                                   description="Assessment results directory glob pattern")


@register_function(config_type=NodeResultsReaderConfig)
async def node_results_reader(config: NodeResultsReaderConfig, _builder: Builder):

    async def _read_results(query: str) -> str:
        try:
            if not query or query.strip() == "":
                query = "all"

            files_map = {
                "summary": ["00_SUMMARY.txt"],
                "devices": ["01_device_status.txt", "02_device_list.txt"],
                "connectivity": ["03_connectivity.txt"],
                "system": ["04_system_info.txt"],
                "gpu": ["05_gpu_info.txt"],
                "dcgm": ["06_dcgm_status.txt"],
                "network": ["07_network_interfaces.txt"],
                "storage": ["08_storage_info.txt"],
                "hardware": ["09_hardware_info.txt"],
                "overview": ["01_device_status.txt", "04_system_info.txt", "05_gpu_info.txt", "06_dcgm_status.txt"],
                "full": [
                    "00_SUMMARY.txt",
                    "01_device_status.txt",
                    "02_device_list.txt",
                    "03_connectivity.txt",
                    "04_system_info.txt",
                    "05_gpu_info.txt",
                    "06_dcgm_status.txt",
                    "07_network_interfaces.txt",
                    "08_storage_info.txt",
                    "09_hardware_info.txt"
                ],
                "all": ["*.txt"],
            }

            patterns = None
            # First try keyword matching
            for key, vals in files_map.items():
                if key in query.lower():
                    patterns = vals
                    break

            # If no keyword match, try specific filename matching
            if patterns is None:
                for key, vals in files_map.items():
                    for filename in vals:
                        if filename.lower() in query.lower():
                            patterns = vals
                            break
                    if patterns:
                        break

            # Default fallback
            if patterns is None:
                patterns = files_map["summary"]

            if config.cluster_host == "localhost":
                latest_dir = None
                # Allow explicit dir in query to override
                explicit = None
                for token in query.split():
                    if token.startswith("/tmp/node_assessment_") and Path(token).exists():
                        explicit = Path(token)
                        break
                if explicit and explicit.is_dir():
                    latest_dir = explicit
                else:
                    # Prefer stable symlink if present
                    symlink_path = Path("/tmp/node_assessment_latest")
                    if symlink_path.exists() and symlink_path.is_dir():
                        latest_dir = symlink_path
                    else:
                        # Find latest local directory matching glob (absolute glob)
                        matches = sorted(Path("/tmp").glob(Path(config.results_directory).name), reverse=True)
                        for p in matches:
                            if p.is_dir():
                                latest_dir = p
                                break
                if not latest_dir:
                    return ("❌ No local node assessment directory found. "
                            "Run node_assessment_tool first or provide explicit path in query.")
                results: list[str] = []
                for pat in patterns:
                    for f in latest_dir.glob(pat):
                        try:
                            content = await asyncio.to_thread(f.read_text)
                            results.append(f"{f.name}:\n{_truncate_text(content)}\n{'='*50}\n")
                        except Exception:
                            pass
                return "\n".join(results) if results else "❌ No results found."

            # Remote
            remote_glob = shlex.quote(config.results_directory)
            latest_dir_cmd = [
                "ssh",
                "-o",
                "BatchMode=yes",
                "-o",
                "StrictHostKeyChecking=accept-new",
                "-o",
                f"ConnectTimeout={min(30, REMOTE_CMD_TIMEOUT)}",
                f"{config.cluster_user}@{config.cluster_host}",
                f"bash -lc 'ls -td -- {remote_glob} 2>/dev/null | head -1'",
            ]
            latest_proc = await asyncio.create_subprocess_exec(*latest_dir_cmd,
                                                               stdout=asyncio.subprocess.PIPE,
                                                               stderr=asyncio.subprocess.PIPE)
            try:
                latest_stdout, _ = await asyncio.wait_for(latest_proc.communicate(), timeout=REMOTE_CMD_TIMEOUT)
            except asyncio.TimeoutError:
                try:
                    latest_proc.kill()
                except Exception:
                    pass
                return f"❌ Timed out locating latest directory ({REMOTE_CMD_TIMEOUT}s)"
            if latest_proc.returncode != 0 or not latest_stdout.strip():
                return f"❌ Could not find latest assessment directory matching {config.results_directory}"
            latest_dir = latest_stdout.decode("utf-8").strip()

            remote_results: list[str] = []
            for file_pattern in patterns:
                ld = shlex.quote(latest_dir)
                pat = shlex.quote(file_pattern)
                # Build a safe bash -lc command string with quoting and file labels
                find_cmd = ("bash -lc '"
                            f"find -- {ld} -name {pat} -print "
                            "-exec printf \"\\n--- %s ---\\n\" {} \\; "
                            "-exec cat {} \\;"
                            "'")
                ssh_cmd = [
                    "ssh",
                    "-o",
                    "BatchMode=yes",
                    "-o",
                    "StrictHostKeyChecking=accept-new",
                    "-o",
                    f"ConnectTimeout={min(30, REMOTE_CMD_TIMEOUT)}",
                    f"{config.cluster_user}@{config.cluster_host}",
                    find_cmd,
                ]
                proc = await asyncio.create_subprocess_exec(*ssh_cmd,
                                                            stdout=asyncio.subprocess.PIPE,
                                                            stderr=asyncio.subprocess.PIPE)
                try:
                    stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=REMOTE_CMD_TIMEOUT)
                except asyncio.TimeoutError:
                    try:
                        proc.kill()
                    except Exception:
                        pass
                    continue
                if proc.returncode == 0:
                    content = stdout.decode("utf-8")
                    if content.strip():
                        remote_results.append(f"{file_pattern}:\n{_truncate_text(content)}\n{'='*50}\n")
            return (f"Node Assessment Results:\n\n{os.linesep.join(remote_results)}"
                    if remote_results else "❌ No assessment results found. Run node_assessment_tool first.")
        except Exception as e:  # noqa: BLE001
            return f"❌ Error reading node assessment results: {str(e)}"

    yield FunctionInfo.from_fn(_read_results, description="Read and analyze DGX node assessment results")


print("✅ DGX Node Results Reader tool registered successfully")

# ========================
# DGX Orchestrator (LangGraph)
# ========================


class DGXOrchestratorConfig(FunctionBaseConfig, name="dgx_orchestrator"):
    """LangGraph orchestrator that wraps a DGX ReAct agent and tools."""

    reasoning_llm_name: str = Field(description="LLM used for reasoning and planning")
    react_agent_fn: str = Field(default="dgx_react_agent", description="Registered ReAct agent function name to wrap")
    executor_fn: str = Field(
        default="bcm_executor",
        description="Registered executor function name for BCM commands (code_execution_with_approval)",
    )


@register_function(config_type=DGXOrchestratorConfig, framework_wrappers=[LLMFrameworkEnum.LANGCHAIN])
async def dgx_orchestrator(config: DGXOrchestratorConfig, builder: Builder):
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import PromptTemplate
    from langgraph.graph import END
    from langgraph.graph import StateGraph

    # Acquire handles lazily so registration order doesn't matter
    # reasoning_llm will be acquired just-in-time in generate_commands
    # Optional tools used directly by the orchestrator
    try:
        node_assess = builder.get_function("node_assessment_tool")
        node_reader = builder.get_function("node_results_reader")
        dgx_rag = builder.get_function("dgx_expert_rag")
        bcm_rag = builder.get_function("bcm_documentation_rag")
    except Exception:
        node_assess = None
        node_reader = None
        dgx_rag = None
        bcm_rag = None

    try:
        executor = builder.get_function(config.executor_fn)
    except Exception:
        executor = None

    # No decision prompt in minimal mode; regex-based routing only

    commands_prompt = PromptTemplate.from_template("""
        You are a BCM expert. Based on the assessment and DGX guidance, generate exact Bright Cluster Manager commands
        to perform the required DGX node actions.

        Output two sections in this exact order:
        Rationale: 3-5 concise bullets referencing snippets from CONTEXT.
        Commands: each line MUST start with cmsh -c " and be one command per line.

        CONTEXT\n---\n{context}\n---
        """)

    summarization_prompt = PromptTemplate.from_template("""
        You are a DGX/BCM SRE. Summarize the node assessment for the user's question.

        Question: {question}

        Assessment Extract (selected files/overview):
        {results}

        Write a concise, actionable summary:
        - Current cluster state: counts of UP/DOWN/unreachable, notable health issues
        - Critical incidents or unreachable devices
        - Configuration/collection issues (if any) and what they imply
        - Recommended next steps (2-5 bullets), safe and non-destructive

        Keep it tight. Do not dump raw file contents.
        """)

    class OrchestratorState(TypedDict, total=False):
        input: str
        assessment: str
        analysis: str
        react_agent_output: str
        dgx_guidance: str
        bcm_commands: str
        execution_result: str
        final_output: str
        action_type: str
        decision_json: str
        results_query: str
        results_directory: str
        results_text: str
        results_dir: str

    async def assess_node(state: OrchestratorState):
        logger.info("assess_node: Starting node assessment...")
        if not node_assess:
            logger.warning("assess_node: No node_assess tool available")
            return state

        try:
            logger.info("assess_node: Calling node_assess.ainvoke...")
            assess_out = await asyncio.wait_for(
                node_assess.ainvoke("Run DGX node assessment and save results"),
                timeout=state.get("timeout", None) or LOCAL_CMD_TIMEOUT,
            )
            logger.info("✅ assess_node: Node assessment completed successfully")
        except asyncio.TimeoutError:
            assess_out = f"❌ Node assessment timed out after {state.get('timeout', None) or LOCAL_CMD_TIMEOUT}s"
            logger.warning("assess_node: Node assessment timed out")
        except Exception as e:  # noqa: BLE001
            assess_out = f"❌ Node assessment error: {str(e)}"
            logger.error("❌ assess_node: Node assessment failed: %s", str(e))

        # Extract results directory from assessment output
        logger.info("assess_node: Extracting results directory...")
        results_dir = ""
        if assess_out:
            m = re.search(r"(/tmp/node_assessment_[0-9_]+)", assess_out)
            if m:
                results_dir = m.group(1)
                logger.info("assess_node: Found results directory: %s", results_dir)

        # Get the appropriate results query (set in analyze_and_decide)
        results_query = state.get("results_query", "overview")  # default to overview for better detail

        # Include directory in query if we found one
        if results_dir:
            results_query_with_dir = f"{results_query} {results_dir}"
        else:
            results_query_with_dir = results_query

        # Read detailed results for LLM analysis (but don't dump in final output)
        logger.info("assess_node: Reading assessment results with query: %s", results_query_with_dir)
        results_text = ""
        if node_reader:
            try:
                raw_results = await asyncio.wait_for(node_reader.ainvoke(results_query_with_dir),
                                                     timeout=LOCAL_CMD_TIMEOUT)
                # Clean ANSI codes and store for LLM summarization
                results_text = _strip_ansi(raw_results)
                logger.info("✅ assess_node: Results read successfully")
            except Exception as e:
                logger.warning("assess_node: Failed to read results: %s", str(e))
                results_text = ""
        else:
            logger.warning("assess_node: No node_reader tool available")

        # Keep analysis clean (no raw file dumps)
        analysis = state.get("analysis", "") or ""

        logger.info("assess_node: Completed, returning state")
        return {
            **state,
            "assessment": assess_out,
            "analysis": analysis,
            "results_text": results_text,
            "results_dir": results_dir
        }

    async def analyze_and_decide(state: OrchestratorState):
        """
        Two-pass analysis:
        - Pass 1: neutral LLM classification (JSON).
        - Pass 2: conditional RAG enrichment (only if action indicates commands/reset).
        Adds deterministic keyword overrides to ensure reset requests are labeled correctly.
        """
        logger.info("analyze_and_decide: Starting analysis...")
        logger.info("User input being analyzed: '%s'", (state.get("input", "") or "")[:200])
        import json as _json

        # Skip reader call in analyze_and_decide to avoid duplicates
        # Assessment will be refreshed after node_assessment runs
        reader_out = ""

        # === Determine results detail level based on user input ===
        user_input = (state.get("input", "") or "").lower()
        results_query = "summary"  # default

        if any(term in user_input for term in ["full", "all", "detailed", "everything", "complete"]):
            results_query = "full"
        elif any(term in user_input for term in ["overview", "cluster health", "burn configs"]):
            results_query = "overview"
        elif any(term in user_input for term in ["state", "status", "current", "what", "show", "list"]):
            results_query = "overview"  # More detailed than summary for status queries

        # Store results query in state for use in assess_node
        state["results_query"] = results_query

        # === Minimal classification: regex-only ===
        extracted_json = "{}"
        action_type = "diagnostics_only"
        decision_obj = None

        # === Deterministic overrides (user input only with tighter regex) ===
        user_input = (state.get("input", "") or "")

        reset_actions = (r"(\bfactory\s*-?\s*)?\breset\b|\bre-?image\b|\bre-?install\b|\bre-?flash\b"
                         r"|\bre-?provision\b|\bwipe(?:d|s|ing)?\b|\bclean\s+install\b|\brevert\b")
        node_targets = r"node|nodes|cluster|superpod|dgx"
        reset_regex = re.compile(
            rf"({reset_actions}).*\b({node_targets})\b|"
            rf"\b({node_targets})\b.*({reset_actions})",
            re.IGNORECASE,
        )
        command_verbs = (r"\bgive\s+me\b|\bprovide\b|\bshow\s+me\b|\bgenerate\b|\bcreate\b"
                         r"|\bproduce\b|\bwrite\b|\boutput\b")
        command_nouns = r"cmsh|commands?"
        generate_cmds_regex = re.compile(
            rf"({command_verbs}).*\b({command_nouns})\b|"
            rf"\b({command_nouns})\b.*({command_verbs})|"
            rf"\bcmsh\b.*\bcommands?\b|\bcommands?\b.*\bcmsh\b",
            re.IGNORECASE,
        )

        override_applied = False
        if reset_regex.search(user_input):
            if action_type != "reset_nodes":
                logger.info("Orchestrator override: detected reset intent in user input -> action_type='reset_nodes'")
                logger.info("Reset regex matched: %s", reset_regex.pattern)
                action_type = "reset_nodes"
                override_applied = True

        if (not override_applied and action_type == "diagnostics_only" and generate_cmds_regex.search(user_input)):
            logger.info("Orchestrator override: generate-commands intent -> action_type='generate_bcm_commands'")
            logger.info("Generate commands regex matched: %s", generate_cmds_regex.pattern)
            action_type = "generate_bcm_commands"
            override_applied = True

        # Explicit diagnostics intent clamp (but don't override command/reset intent)
        diagnostics_intent_regex = re.compile(
            r"\b(state|status|health|condition|what.?s\s+the\s+(current\s+)?state|overview|summary|list|show)\b",
            re.IGNORECASE,
        )
        # Only apply diagnostics clamp if there's no explicit command/reset intent
        has_explicit_action_intent = re.search(
            r'\b(cmsh|commands?|reset|re-?image|re-?install|re-?flash|wipe(?:d|s|ing)?|revert)\b',
            user_input,
            re.IGNORECASE)
        if diagnostics_intent_regex.search(
                user_input) and action_type != "diagnostics_only" and not has_explicit_action_intent:
            logger.info(
                "Orchestrator clamp: explicit diagnostics intent (no action override) -> action_type='diagnostics_only'"
            )
            action_type = "diagnostics_only"
        elif diagnostics_intent_regex.search(user_input) and has_explicit_action_intent:
            logger.info(
                "Orchestrator: diagnostics intent detected but explicit action intent found, keeping action_type='%s'",
                action_type)

        # Safety floor: if LLM chose actions but user didn't explicitly request
        if action_type in ("generate_bcm_commands", "reset_nodes"):
            if not (reset_regex.search(user_input) or generate_cmds_regex.search(user_input)):
                logger.info("Orchestrator clamp: no explicit user action intent -> action_type='diagnostics_only'")
                action_type = "diagnostics_only"

        # === Conditional DGX RAG enrichment (reset-only) ===
        dgx_guidance = ""
        if action_type in ("generate_bcm_commands", "reset_nodes") and dgx_rag:
            try:
                dgx_guidance = await asyncio.wait_for(
                    dgx_rag.ainvoke("DGX node reset prerequisites and best practices for H100-based SuperPOD."),
                    timeout=LLM_STEP_TIMEOUT,
                )
            except asyncio.TimeoutError:
                dgx_guidance = "❌ DGX guidance RAG timed out"
            except Exception:
                dgx_guidance = ""

        # Compose analysis report (minimal)
        analysis_report = ("### Reasoning\n"
                           f"Detected action_type: {action_type}\n\n" + (reader_out[:1500] if reader_out else "") +
                           "\n\n" + dgx_guidance)

        # If LLM returned a parsed object, keep it; otherwise synthesize a short JSON for traceability
        if decision_obj is None:
            try:
                decision_obj = _json.loads(extracted_json.replace("'", '"'))
            except Exception:
                decision_obj = {
                    "rationale": ["LLM output not parseable"],
                    "action_needed": action_type != "diagnostics_only",
                    "action_type": action_type,
                    "focus": ""
                }

        # Minimal decision JSON
        decision_json_out = _json.dumps({
            "rationale": ["regex-based classification"],
            "action_needed": action_type != "diagnostics_only",
            "action_type": action_type,
            "focus": ""
        })

        logger.info("✅ analyze_and_decide: Analysis completed, action_type=%s", action_type)
        if action_type == "reset_nodes":
            logger.info("Routing decision: User requested node reset/reimage operations")
        elif action_type == "generate_bcm_commands":
            logger.info("Routing decision: User requested BCM command generation")
        else:
            logger.info("Routing decision: Treating as diagnostics-only request")
        return {**state, "analysis": analysis_report, "action_type": action_type, "decision_json": decision_json_out}

    async def summarize_results(state: OrchestratorState):
        """Use LLM to analyze assessment results and produce concise summary"""
        logger.info("summarize_results: Starting intelligent summarization...")

        try:
            reasoning_llm = await builder.get_llm(config.reasoning_llm_name, wrapper_type=LLMFrameworkEnum.LANGCHAIN)
        except Exception as e:
            logger.error("❌ summarize_results: Could not acquire LLM: %s", str(e))
            return {**state, "analysis": f"❌ Could not acquire LLM for summarization: {e}"}

        # Get the detailed results and user question
        results = _truncate_text(state.get("results_text", ""), 100_000)
        question = state.get("input", "")

        if not results.strip():
            logger.warning("summarize_results: No results text to summarize")
            return {**state, "analysis": "❌ No assessment results available for summarization"}

        # Use LLM to create intelligent summary
        chain = summarization_prompt | reasoning_llm | StrOutputParser()
        try:
            summary = await asyncio.wait_for(chain.ainvoke({
                "question": question, "results": results
            }),
                                             timeout=LLM_STEP_TIMEOUT)
            logger.info("✅ summarize_results: LLM summarization completed")
        except asyncio.TimeoutError:
            logger.warning("summarize_results: LLM summarization timed out")
            summary = f"❌ Summary unavailable (LLM timed out after {LLM_STEP_TIMEOUT}s)"
        except Exception as e:
            logger.error("❌ summarize_results: LLM error: %s", str(e))
            summary = f"❌ Summary unavailable (LLM error): {e}"

        return {**state, "analysis": summary}

    # ReAct agent removed in minimal workflow

    async def generate_commands(state: OrchestratorState):
        logger.info("generate_commands: Starting BCM command generation...")
        if not bcm_rag:
            logger.error("generate_commands: BCM RAG tool not available!")
            return {**state, "bcm_commands": "❌ BCM RAG tool not available"}
        # Reacquire LLM only when needed
        try:
            reasoning_llm = await builder.get_llm(config.reasoning_llm_name, wrapper_type=LLMFrameworkEnum.LANGCHAIN)
        except Exception as e:
            return {**state, "bcm_commands": f"❌ Could not acquire LLM: {str(e)}"}

        # 1) Retrieve BCM guidance (and use any DGX guidance already in state)
        try:
            bcm_docs = await asyncio.wait_for(
                bcm_rag.ainvoke("Provide BCM cmsh-based procedures for DGX node reset/reimage, including exact command "
                                "patterns for: drain/disable, reinstall OS/image, reset/power cycle, and verification. "
                                "Keep it concise."),
                timeout=LLM_STEP_TIMEOUT,
            )
        except asyncio.TimeoutError:
            bcm_docs = "❌ BCM guidance RAG timed out"
        except Exception as e:
            bcm_docs = f"❌ BCM guidance error: {str(e)}"

        dgx_guidance = state.get("dgx_guidance", "")
        assessment = state.get("assessment", "")
        analysis = state.get("analysis", "")
        context = ("ASSESSMENT:\n" + (assessment or "") + "\n\n"
                   "ANALYSIS:\n" + (analysis or "") + "\n\n"
                   "DGX GUIDANCE:\n" + (dgx_guidance or "") + "\n\n"
                   "BCM DOCS:\n" + (bcm_docs or ""))

        # 2) Ask LLM to produce rationale + commands
        try:
            chain_for_cmds = commands_prompt | reasoning_llm | StrOutputParser()
            llm_out = await asyncio.wait_for(chain_for_cmds.ainvoke({"context": context}), timeout=LLM_STEP_TIMEOUT)
        except asyncio.TimeoutError:
            llm_out = f"CONTEXT:\n{context}\n\n[Timed out generating BCM commands]"
        except Exception as e:
            llm_out = f"CONTEXT:\n{context}\n\n[Error: {str(e)}]"

        # Debug logging for LLM output
        logger.info("🔍 LLM generated BCM commands output:")
        logger.info("=" * 60)
        logger.info(llm_out)
        logger.info("=" * 60)

        # 3) Extract only safe cmsh lines
        extracted = _extract_cmsh_commands(llm_out)
        if not extracted:
            return {**state, "bcm_commands": "❌ No valid cmsh commands extracted. Skipping execution."}

        commands_payload = "\n".join(extracted)
        return {**state, "bcm_commands": commands_payload}

    async def execute_commands(state: OrchestratorState):
        if not executor:
            return {**state, "execution_result": "No executor configured; skipping execution."}
        cmds = state.get("bcm_commands", "")
        if not cmds.strip() or not all(line.strip().startswith('cmsh -c "') for line in cmds.splitlines()):
            return {**state, "execution_result": "❌ No executable cmsh commands. Skipping execution."}
        try:
            exec_out = await asyncio.wait_for(
                executor.ainvoke(cmds),
                timeout=state.get("timeout", None) or LOCAL_CMD_TIMEOUT,
            )
        except asyncio.TimeoutError:
            exec_out = f"❌ Execution timed out after {state.get('timeout', None) or LOCAL_CMD_TIMEOUT}s"
        except Exception as e:  # noqa: BLE001
            exec_out = f"❌ Execution error: {str(e)}"
        return {**state, "execution_result": exec_out}

    async def synthesize(state: OrchestratorState):
        final = ("# DGX Orchestration\n\n"
                 "## Reasoning and Decision\n" + (state.get("analysis", "") or "") + "\n\n"
                 "## ReAct Agent Plan and Steps\n" + (state.get("react_agent_output", "") or "") + "\n\n"
                 "## Generated BCM Commands\n" + (state.get("bcm_commands", "") or "") + "\n\n"
                 "## Execution Result\n" + (state.get("execution_result", "") or "") + "\n")
        return {**state, "final_output": final}

    async def synthesize_diagnostics_only(state: OrchestratorState):
        """Synthesize results for diagnostics-only requests (no command generation/execution)"""
        logger.info("synthesize_diagnostics_only: Starting synthesis...")

        # Get the LLM-generated summary from the analysis
        llm_summary = state.get("analysis", "") or ""
        results_dir = state.get("results_dir", "N/A")

        # Build clean output with just the intelligent summary
        final = ("# DGX Orchestration (Diagnostics Only)\n\n"
                 "## Assessment Summary\n" + llm_summary + "\n\n"
                 "## Notes\n"
                 f"Results directory: {results_dir}\n"
                 "No BCM commands were generated or executed.\n")

        logger.info("✅ synthesize_diagnostics_only: Synthesis completed")
        return {**state, "final_output": final}

    # Always assess first, then branch
    def route_after_analysis(state: OrchestratorState):
        # Always assess first, branch afterwards
        action_type = state.get("action_type", "diagnostics_only")
        logger.info("route_after_analysis: %s -> assess", action_type)
        return "assess"

    def route_after_assess(state: OrchestratorState):
        action_type = state.get("action_type", "diagnostics_only")
        if action_type in ("generate_bcm_commands", "reset_nodes"):
            logger.info("route_after_assess: %s -> generate", action_type)
            return "generate"
        logger.info("route_after_assess: %s -> summarize", action_type)
        return "summarize"

    # No post-agent routing in minimal orchestrator

    # Build LangGraph with conditional routing
    graph = StateGraph(OrchestratorState)
    graph.add_node("assess", assess_node)
    graph.add_node("analyze", analyze_and_decide)
    graph.add_node("summarize", summarize_results)
    graph.add_node("generate", generate_commands)
    graph.add_node("execute", execute_commands)
    graph.add_node("synthesize", synthesize)
    graph.add_node("synthesize_diagnostics_only", synthesize_diagnostics_only)

    graph.set_entry_point("analyze")

    # Always route to assess first
    graph.add_conditional_edges("analyze", route_after_analysis, {"assess": "assess"})

    # After assessment, branch to generate or summarize
    graph.add_conditional_edges("assess", route_after_assess, {
        "generate": "generate",
        "summarize": "summarize",
    })

    graph.add_edge("generate", "execute")
    graph.add_edge("execute", "synthesize")
    graph.add_edge("summarize", "synthesize_diagnostics_only")
    graph.add_edge("synthesize", END)
    graph.add_edge("synthesize_diagnostics_only", END)

    app = graph.compile()

    async def _run(input_text: str) -> str:  # noqa: ARG001 - required by framework signature
        logger.info("DGX Orchestrator: Starting workflow with input: %s", input_text[:100])
        state: OrchestratorState = {
            "input": input_text,
            "assessment": "",
            "analysis": "",
            "react_agent_output": "",
            "dgx_guidance": "",
            "bcm_commands": "",
            "execution_result": "",
            "final_output": "",
        }
        logger.info("DGX Orchestrator: Invoking LangGraph app...")
        result = await app.ainvoke(state)
        logger.info("DGX Orchestrator: Workflow completed")
        return result.get("final_output", "❌ DGX orchestrator produced no output")

    yield FunctionInfo.from_fn(
        _run,
        description=("Analyze DGX cluster state, decide actions, generate BCM node commands, "
                     "execute with approval, and return final reasoning and results."),
    )


print("✅ DGX Orchestrator registered successfully")
