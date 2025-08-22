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


def _extract_cmsh_commands(text: str) -> list[str]:
    cmds: list[str] = []
    for line in (text or "").splitlines():
        s = line.strip()
        if s.startswith('cmsh -c "') and s.endswith('"'):
            cmds.append(s)
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
                            f"📋 Assessment Output:\n{s_out.strip()}\n\n"
                            f"📁 Results saved in: {outdir}\n"
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
                            f"📋 Assessment Output:\n{s_out.strip()}\n\n"
                            f"📁 Results saved on cluster: {outdir}\n"
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
    results_directory: str = Field(description="Assessment results directory glob, e.g., /tmp/node_assessment_*")


@register_function(config_type=NodeResultsReaderConfig)
async def node_results_reader(config: NodeResultsReaderConfig, _builder: Builder):

    async def _read_results(query: str) -> str:
        try:
            if not query or query.strip() == "":
                query = "all"

            files_map = {
                "summary": ["00_SUMMARY.txt"],
                "devices": ["01_device_status.txt", "02_device_list.txt"],
                "bcm": ["16_bcm_version_info.txt", "17_pkg_cmdaemon.txt", "18_pkg_cluster_tools.txt"],
                "hardware": ["19_hardware_profiles.txt", "20_os_versions.txt", "21_bios_versions.txt"],
                "firmware": ["22_firmware_info.txt", "23_sample_bios_settings.txt"],
                "bmc": ["24_bmc_info.txt"],
                "overview": ["25_device_overview.txt", "26_burn_configs.txt"],
                "full": [
                    "00_SUMMARY.txt",
                    "01_device_status.txt",
                    "02_device_list.txt",
                    "16_bcm_version_info.txt",
                    "19_hardware_profiles.txt",
                    "20_os_versions.txt",
                    "24_bmc_info.txt",
                    "25_device_overview.txt"
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
                            results.append(f"📄 {f.name}:\n{_truncate_text(content)}\n{'='*50}\n")
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
                        remote_results.append(f"📄 {file_pattern}:\n{_truncate_text(content)}\n{'='*50}\n")
            return (f"📊 Node Assessment Results:\n\n{os.linesep.join(remote_results)}"
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

    async def assess_node(state: OrchestratorState):
        logger.info("🔍 assess_node: Starting node assessment...")
        if not node_assess:
            logger.warning("⚠️ assess_node: No node_assess tool available")
            return state

        try:
            logger.info("🚀 assess_node: Calling node_assess.ainvoke...")
            assess_out = await asyncio.wait_for(
                node_assess.ainvoke("Run DGX node assessment and save results"),
                timeout=state.get("timeout", None) or LOCAL_CMD_TIMEOUT,
            )
            logger.info("✅ assess_node: Node assessment completed successfully")
        except asyncio.TimeoutError:
            assess_out = f"❌ Node assessment timed out after {state.get('timeout', None) or LOCAL_CMD_TIMEOUT}s"
            logger.warning("⏰ assess_node: Node assessment timed out")
        except Exception as e:  # noqa: BLE001
            assess_out = f"❌ Node assessment error: {str(e)}"
            logger.error("❌ assess_node: Node assessment failed: %s", str(e))

        # Extract results directory from assessment output
        logger.info("📁 assess_node: Extracting results directory...")
        results_dir = ""
        if assess_out:
            m = re.search(r"(/tmp/node_assessment_[0-9_]+)", assess_out)
            if m:
                results_dir = m.group(1)
                logger.info("📁 assess_node: Found results directory: %s", results_dir)

        # Get the appropriate results query (set in analyze_and_decide)
        results_query = state.get("results_query", "overview")  # default to overview for better detail

        # Include directory in query if we found one
        if results_dir:
            results_query_with_dir = f"{results_query} {results_dir}"
        else:
            results_query_with_dir = results_query

        # Refresh results after assessment to include detailed results
        logger.info("📖 assess_node: Reading assessment results with query: %s", results_query_with_dir)
        refreshed = ""
        if node_reader:
            try:
                refreshed = await asyncio.wait_for(node_reader.ainvoke(results_query_with_dir),
                                                   timeout=LOCAL_CMD_TIMEOUT)
                logger.info("✅ assess_node: Results read successfully")
            except Exception as e:
                logger.warning("⚠️ assess_node: Failed to read results: %s", str(e))
                refreshed = ""
        else:
            logger.warning("⚠️ assess_node: No node_reader tool available")

        combined_analysis = (state.get("analysis", "") or "")
        if refreshed:
            combined_analysis = (combined_analysis + "\n\n" + refreshed).strip()

        logger.info("🏁 assess_node: Completed, returning state")
        return {**state, "assessment": assess_out, "analysis": combined_analysis, "results_directory": results_dir}

    async def analyze_and_decide(state: OrchestratorState):
        """
        Two-pass analysis:
        - Pass 1: neutral LLM classification (JSON).
        - Pass 2: conditional RAG enrichment (only if action indicates commands/reset).
        Adds deterministic keyword overrides to ensure reset requests are labeled correctly.
        """
        logger.info("🧠 analyze_and_decide: Starting analysis...")
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

        reset_regex = re.compile(
            r"(\bfactory\s*-?\s*reset\b|\bre-?image\b|\bre-?install\b|\bre-?flash\b|\bwipe\b|\bclean\sinstall\b)"
            r".*\b(node|nodes|cluster|superpod|dgx)\b|"
            r"\b(node|nodes|cluster|superpod|dgx)\b.*"
            r"(\bfactory\s*-?\s*reset\b|\bre-?image\b|\bre-?install\b|\bre-?flash\b|\bwipe\b|\bclean\sinstall\b)",
            re.IGNORECASE,
        )
        generate_cmds_regex = re.compile(
            r"(\bgenerate|\bcreate|\bproduce|\bwrite|\boutput)\b.*\b(commands?|cmsh)\b|"
            r"\b(commands?|cmsh)\b.*(\bgenerate|\bcreate|\bproduce|\bwrite|\boutput)\b",
            re.IGNORECASE,
        )

        override_applied = False
        if reset_regex.search(user_input):
            if action_type != "reset_nodes":
                logger.info("Orchestrator override: detected reset intent in user input -> action_type='reset_nodes'")
                action_type = "reset_nodes"
                override_applied = True

        if (not override_applied and action_type == "diagnostics_only" and generate_cmds_regex.search(user_input)):
            logger.info("Orchestrator override: generate-commands intent -> action_type='generate_bcm_commands'")
            action_type = "generate_bcm_commands"
            override_applied = True

        # Explicit diagnostics intent clamp
        diagnostics_intent_regex = re.compile(
            r"\b(state|status|health|condition|what.?s\s+the\s+(current\s+)?state|overview|summary|list|show)\b",
            re.IGNORECASE,
        )
        if diagnostics_intent_regex.search(user_input) and action_type != "diagnostics_only":
            logger.info("Orchestrator clamp: explicit diagnostics intent -> action_type='diagnostics_only'")
            action_type = "diagnostics_only"

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
        return {**state, "analysis": analysis_report, "action_type": action_type, "decision_json": decision_json_out}

    # ReAct agent removed in minimal workflow

    async def generate_commands(state: OrchestratorState):
        if not bcm_rag:
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

        # 3) Extract only safe cmsh lines
        extracted = _extract_cmsh_commands(llm_out)
        if not extracted:
            return {**state, "bcm_commands": "❌ No valid cmsh commands extracted. Skipping execution."}

        commands_payload = "\n".join(extracted)
        return {**state, "bcm_commands": commands_payload}

    async def execute_commands(state: OrchestratorState):
        if not executor:
            return {**state, "execution_result": "ℹ️ No executor configured; skipping execution."}
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
        final = ("# 🧭 DGX Orchestration\n\n"
                 "## Reasoning and Decision\n" + (state.get("analysis", "") or "") + "\n\n"
                 "## ReAct Agent Plan and Steps\n" + (state.get("react_agent_output", "") or "") + "\n\n"
                 "## Generated BCM Commands\n" + (state.get("bcm_commands", "") or "") + "\n\n"
                 "## Execution Result\n" + (state.get("execution_result", "") or "") + "\n")
        return {**state, "final_output": final}

    async def synthesize_diagnostics_only(state: OrchestratorState):
        """Synthesize results for diagnostics-only requests (no command generation/execution)"""
        logger.info("📝 synthesize_diagnostics_only: Starting synthesis...")

        # Extract the detailed results from the analysis
        analysis = state.get("analysis", "") or ""
        assessment_log = state.get("assessment", "") or ""

        # Split analysis into reasoning part and detailed results part
        reasoning_part = ""
        detailed_results = ""

        if analysis:
            # The analysis contains reasoning + detailed file contents
            # Look for the file contents section (starts with 📄)
            analysis_lines = analysis.split("\n")
            reasoning_lines = []
            results_lines = []
            in_results_section = False

            for line in analysis_lines:
                if line.strip().startswith("📄") or in_results_section:
                    in_results_section = True
                    results_lines.append(line)
                else:
                    reasoning_lines.append(line)

            reasoning_part = "\n".join(reasoning_lines).strip()
            detailed_results = "\n".join(results_lines).strip()

        # Build comprehensive output
        final = ("# 🧭 DGX Orchestration (Diagnostics Only)\n\n"
                 "## Reasoning and Decision\n" + reasoning_part + "\n\n"
                 "## Assessment Script Log\n" + assessment_log + "\n\n")

        if detailed_results:
            final += "## Detailed Assessment Results\n" + detailed_results + "\n\n"

        final += ("## Recommendation\n"
                  "Based on the analysis above, see the diagnostic findings. "
                  f"Results directory: {state.get('results_directory', 'N/A')}.\n"
                  "No BCM commands were generated or executed.\n")

        logger.info("✅ synthesize_diagnostics_only: Synthesis completed")
        return {**state, "final_output": final}

    # Always assess first, then branch
    def route_after_analysis(state: OrchestratorState):
        # Always assess first, branch afterwards
        action_type = state.get("action_type", "diagnostics_only")
        logger.info("🔀 route_after_analysis: %s -> assess", action_type)
        return "assess"

    def route_after_assess(state: OrchestratorState):
        action_type = state.get("action_type", "diagnostics_only")
        if action_type in ("generate_bcm_commands", "reset_nodes"):
            logger.info("🔀 route_after_assess: %s -> generate", action_type)
            return "generate"
        logger.info("🔀 route_after_assess: %s -> synthesize_diagnostics_only", action_type)
        return "synthesize_diagnostics_only"

    # No post-agent routing in minimal orchestrator

    # Build LangGraph with conditional routing
    graph = StateGraph(OrchestratorState)
    graph.add_node("assess", assess_node)
    graph.add_node("analyze", analyze_and_decide)
    graph.add_node("generate", generate_commands)
    graph.add_node("execute", execute_commands)
    graph.add_node("synthesize", synthesize)
    graph.add_node("synthesize_diagnostics_only", synthesize_diagnostics_only)

    graph.set_entry_point("analyze")

    # Always route to assess first
    graph.add_conditional_edges("analyze", route_after_analysis, {"assess": "assess"})

    # After assessment, branch to generate or synthesize_diagnostics_only
    graph.add_conditional_edges("assess",
                                route_after_assess, {
                                    "generate": "generate",
                                    "synthesize_diagnostics_only": "synthesize_diagnostics_only",
                                })

    graph.add_edge("generate", "execute")
    graph.add_edge("execute", "synthesize")
    graph.add_edge("synthesize", END)
    graph.add_edge("synthesize_diagnostics_only", END)

    app = graph.compile()

    async def _run(input_text: str) -> str:  # noqa: ARG001 - required by framework signature
        logger.info("🚀 DGX Orchestrator: Starting workflow with input: %s", input_text[:100])
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
        logger.info("📊 DGX Orchestrator: Invoking LangGraph app...")
        result = await app.ainvoke(state)
        logger.info("🏁 DGX Orchestrator: Workflow completed")
        return result.get("final_output", "❌ DGX orchestrator produced no output")

    yield FunctionInfo.from_fn(
        _run,
        description=("Analyze DGX cluster state, decide actions, generate BCM node commands, "
                     "execute with approval, and return final reasoning and results."),
    )


print("✅ DGX Orchestrator registered successfully")
