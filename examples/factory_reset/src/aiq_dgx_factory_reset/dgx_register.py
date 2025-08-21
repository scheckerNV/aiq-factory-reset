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

from filelock import FileLock
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
async def dgx_expert_rag(config: DGXExpertRAGConfig, _builder: Builder):

    async def _search_dgx_docs(query: str) -> str:
        if not os.path.exists(config.docs_path):
            return f"❌ DGX documentation not found at {config.docs_path}"

        prev_api: str | None = None
        try:
            from llama_index.core import Document
            from llama_index.core import ServiceContext
            from llama_index.core import StorageContext
            from llama_index.core import VectorStoreIndex
            from llama_index.core import load_index_from_storage
            from llama_index.embeddings.nvidia import NVIDIAEmbedding
            from llama_index.llms.nvidia import NVIDIA

            nvidia_api_key = config.nvidia_api_key or os.getenv("NVIDIA_API_KEY")
            if not nvidia_api_key:
                return ("❌ NVIDIA API key not provided. Set NVIDIA_API_KEY environment variable or provide in config.")
            prev_api = os.environ.get("NVIDIA_API_KEY")
            os.environ["NVIDIA_API_KEY"] = nvidia_api_key

            llm = NVIDIA(model="meta/llama-3.3-70b-instruct")
            embed = NVIDIAEmbedding(model="nvidia/llama-3.2-nv-embedqa-1b-v2", truncate="END")
            service_context = ServiceContext.from_defaults(llm=llm, embed_model=embed)

            docs_path_obj = Path(config.docs_path)
            docstore_path = os.path.join(config.persist_dir, "docstore.json")
            lock_path = Path(config.persist_dir) / ".index.lock"
            os.makedirs(config.persist_dir, exist_ok=True)
            with FileLock(str(lock_path)):
                if os.path.exists(docstore_path):
                    storage_context = StorageContext.from_defaults(persist_dir=config.persist_dir)
                    index = await asyncio.to_thread(load_index_from_storage, storage_context)
                else:
                    documents: list[Document] = []
                    for md_file in docs_path_obj.rglob("*.md"):
                        try:
                            # Read files off the event loop
                            content = await asyncio.to_thread(md_file.read_text, encoding="utf-8")
                            documents.append(
                                Document(
                                    text=content,
                                    metadata={
                                        "source": str(md_file), "file_name": md_file.name
                                    },
                                ))
                        except Exception as e:  # noqa: BLE001
                            logger.warning("Failed to read %s: %s", md_file, e)

                    if not documents:
                        return f"❌ No DGX documentation files found in {config.docs_path}"

                    index = await asyncio.to_thread(
                        lambda: VectorStoreIndex.from_documents(documents, service_context=service_context))
                    await asyncio.to_thread(index.storage_context.persist, config.persist_dir)

            query_engine = index.as_query_engine(similarity_top_k=config.similarity_top_k,
                                                 response_mode=config.response_mode,
                                                 verbose=True)
            response = await asyncio.to_thread(query_engine.query, query)

            result = "🤖 DGX Documentation Expert\n\n"
            result += f"Query: {query}\n\n"
            result += f"Answer:\n{str(response)}\n\n"

            if hasattr(response, "source_nodes") and response.source_nodes:
                result += "Sources:\n"
                for i, node in enumerate(response.source_nodes[:3], 1):
                    source = node.metadata.get("file_name", "Unknown")
                    score = getattr(node, "score", None)
                    score_str = f" ({score:.3f})" if isinstance(score, float) else ""
                    result += f"{i}. {source}{score_str}\n"
            return result
        except Exception as e:  # noqa: BLE001
            logger.error("Error in DGX documentation search: %s", e)
            return f"❌ Error in DGX analysis: {str(e)}"
        finally:
            # Restore prior API key if it existed
            try:
                if 'prev_api' in locals():
                    if prev_api is None:
                        os.environ.pop("NVIDIA_API_KEY", None)
                    else:
                        os.environ["NVIDIA_API_KEY"] = prev_api
            except Exception:
                pass

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

    async def _run_node_assessment(input_text: str) -> str:
        """Upload and execute the dedicated node_assessment.sh script; return results dir."""
        try:
            script_path_on_disk = str(Path(__file__).resolve().parents[2] / "scripts" / "node_assessment.sh")
            if not os.path.exists(script_path_on_disk):
                return f"❌ node_assessment.sh not found at {script_path_on_disk}"

            # Local run
            if config.cluster_host == "localhost":
                # Ensure script is executable and run via bash to avoid exec perms issues
                try:
                    os.chmod(script_path_on_disk, 0o755)
                except Exception:
                    pass
                proc = await asyncio.create_subprocess_exec(
                    "/bin/bash",
                    script_path_on_disk,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=config.timeout)
                if proc.returncode != 0:
                    # Include stdout as well since some tools write errors to stdout
                    return ("❌ Local assessment failed:\n" + (stderr.decode('utf-8') or '').strip() + "\n" +
                            (stdout.decode('utf-8') or '').strip())
                outdir = stdout.decode("utf-8").strip().splitlines()[-1]
                return f"✅ Node assessment complete. Results in: {outdir}"

            # Remote upload and run
            scp_cmd = [
                "scp",
                script_path_on_disk,
                f"{config.cluster_user}@{config.cluster_host}:/tmp/node_assessment.sh",
            ]
            scp_proc = await asyncio.create_subprocess_exec(*scp_cmd,
                                                            stdout=asyncio.subprocess.PIPE,
                                                            stderr=asyncio.subprocess.PIPE)
            try:
                await asyncio.wait_for(scp_proc.communicate(), timeout=config.timeout)
            except asyncio.TimeoutError:
                scp_proc.kill()
                return "❌ Upload timed out"
            if scp_proc.returncode != 0:
                return "❌ Failed to upload node assessment script to cluster"

            ssh_cmd = [
                "ssh",
                f"{config.cluster_user}@{config.cluster_host}",
                "chmod +x /tmp/node_assessment.sh && /tmp/node_assessment.sh",
            ]
            proc = await asyncio.create_subprocess_exec(*ssh_cmd,
                                                        stdout=asyncio.subprocess.PIPE,
                                                        stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=config.timeout)
            if proc.returncode != 0:
                return ("❌ Remote assessment failed:\n" + (stderr.decode('utf-8') or '').strip() + "\n" +
                        (stdout.decode('utf-8') or '').strip())
            outdir = stdout.decode("utf-8").strip().splitlines()[-1]
            return ("✅ Node assessment completed successfully!\n\n"
                    f"📁 Results saved on cluster: {outdir}\n"
                    "Use the node_results_reader tool to analyze the results.")
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
                f"{config.cluster_user}@{config.cluster_host}",
                f"bash -lc 'ls -td -- {remote_glob} 2>/dev/null | head -1'",
            ]
            latest_proc = await asyncio.create_subprocess_exec(*latest_dir_cmd,
                                                               stdout=asyncio.subprocess.PIPE,
                                                               stderr=asyncio.subprocess.PIPE)
            latest_stdout, _ = await asyncio.wait_for(latest_proc.communicate(), timeout=REMOTE_CMD_TIMEOUT)
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
                    f"{config.cluster_user}@{config.cluster_host}",
                    find_cmd,
                ]
                proc = await asyncio.create_subprocess_exec(*ssh_cmd,
                                                            stdout=asyncio.subprocess.PIPE,
                                                            stderr=asyncio.subprocess.PIPE)
                stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=REMOTE_CMD_TIMEOUT)
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
    from langchain_core.runnables import RunnablePassthrough
    from langgraph.graph import END
    from langgraph.graph import StateGraph

    # Acquire handles lazily so registration order doesn't matter
    reasoning_llm = await builder.get_llm(config.reasoning_llm_name, wrapper_type=LLMFrameworkEnum.LANGCHAIN)

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

    # Prompts
    decide_prompt = PromptTemplate.from_template("""
        You are the DGX Orchestrator. Analyze the current request and the node assessment data.

        Request: {request}

        Assessment Summary (may be empty):
        {assessment}

        Decide what action is needed. Choose action_type based on request intent:
        - "none": Request is informational only, no analysis needed
        - "diagnostics_only": Request asks for STATUS/STATE analysis
          (e.g., "current state", "health check", "what's wrong")
        - "generate_bcm_commands": Request asks to PERFORM actions
          (e.g., "reset nodes", "reimage", "fix issues")
        - "reset_nodes": Request specifically asks for factory reset

        STRICT FORMAT INSTRUCTIONS:
        - Return ONLY a single JSON object with the following keys exactly:
          {"rationale": ["...", "..."], "action_needed": true/false,
           "action_type": "one_of: none|diagnostics_only|generate_bcm_commands|reset_nodes",
           "focus": "short string"}
        - Do not include any markdown, code fences, or extra commentary. JSON only.
        """)

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

    async def assess_node(state: OrchestratorState):
        if not node_assess:
            return state
        try:
            assess_out = await node_assess.ainvoke("Run DGX node assessment and save results")
        except Exception as e:  # noqa: BLE001
            assess_out = f"❌ Node assessment error: {str(e)}"
        return {**state, "assessment": assess_out}

    async def analyze_and_decide(state: OrchestratorState):
        """
        Two-pass analysis:
        - Pass 1: neutral LLM classification (JSON).
        - Pass 2: conditional RAG enrichment (only if action indicates commands/reset).
        Adds deterministic keyword overrides to ensure reset requests are labeled correctly.
        """
        import json as _json
        import logging

        logger = logging.getLogger(__name__)

        # Assessment / summary from node_reader
        reader_out = ""
        if node_reader:
            try:
                reader_out = await node_reader.ainvoke("summary")
            except Exception:
                reader_out = ""

        # === PASS 1: Initial classification with a neutral query ===
        chain_initial = ({
            "request": RunnablePassthrough(),
            "assessment": lambda _: reader_out or state.get("assessment", ""),
        } | decide_prompt | reasoning_llm | StrOutputParser())

        try:
            decision_json = await chain_initial.ainvoke(state.get("input", ""))
        except Exception:
            decision_json = ("{\"rationale\": [\"LLM error\"], \"action_needed\": false, "
                             "\"action_type\": \"diagnostics_only\", \"focus\": \"\"}")

        # Parse JSON (robust)
        extracted_json = decision_json
        action_type = "diagnostics_only"
        decision_obj = None
        try:
            decision_obj = _json.loads(decision_json)
            action_type = decision_obj.get("action_type", action_type)
        except Exception:
            # Attempt to extract JSON substring
            try:
                start_idx = decision_json.find('{"')
                if start_idx == -1:
                    start_idx = decision_json.find("{'")
                if start_idx != -1:
                    brace_count = 0
                    end_idx = None
                    for i, ch in enumerate(decision_json[start_idx:], start_idx):
                        if ch == '{':
                            brace_count += 1
                        elif ch == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_idx = i + 1
                                break
                    if end_idx:
                        extracted_json = decision_json[start_idx:end_idx]
                        decision_obj = _json.loads(extracted_json.replace("'", '"'))
                        action_type = decision_obj.get("action_type", action_type)
            except Exception:
                # leave action_type as default
                pass

        # === Deterministic overrides (user input only with tighter regex) ===
        user_input = (state.get("input", "") or "")

        reset_regex = re.compile(
            r"(\bfactory\s*-?\s*reset\b|\bre-?image\b|\bwipe\b).*\b(node|nodes|cluster|superpod|dgx)\b|"
            r"\b(node|nodes|cluster|superpod|dgx)\b.*(\bfactory\s*-?\s*reset\b|\bre-?image\b|\bwipe\b)",
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

        # === PASS 2: Conditional RAG enrichment ===
        dgx_guidance = ""
        if action_type in ("generate_bcm_commands", "reset_nodes") and dgx_rag:
            try:
                dgx_guidance = await dgx_rag.ainvoke(
                    "DGX node reset prerequisites and best practices for H100-based SuperPOD.")
            except Exception:
                dgx_guidance = ""

        # Compose analysis report (store extracted decision JSON if possible)
        analysis_report = ("### Reasoning\n" + (extracted_json or decision_json) + "\n\n" +
                           (reader_out[:1500] if reader_out else "") + "\n\n" + dgx_guidance)

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

        # Ensure reported action_type matches any overrides
        decision_obj["action_type"] = action_type
        decision_json_out = _json.dumps(decision_obj)

        return {**state, "analysis": analysis_report, "action_type": action_type, "decision_json": decision_json_out}

    async def run_react_agent(state: OrchestratorState):
        """
        Run the DGX ReAct agent with context tailored to the action_type.
        - For reset_nodes: include full reasoning analysis.
        - For other cases: provide neutral, task-appropriate context without
        factory reset framing to avoid bias.
        """
        try:
            react_agent_tool = builder.get_tool(fn_name=config.react_agent_fn, wrapper_type=LLMFrameworkEnum.LANGCHAIN)
        except Exception as e:
            return {**state, "react_agent_output": f"❌ DGX ReAct agent not found: {str(e)}"}

        action_type = state.get("action_type", "diagnostics_only")

        # ==== Context selection based on action type ====
        if action_type == "reset_nodes":
            # Keep full detailed reasoning & reset guidance
            react_input = (f"Original request: {state.get('input', '')}\n\n"
                           f"{state.get('analysis', '')}\n\n"
                           "You are the DGX ReAct Agent. This is a FACTORY RESET request. "
                           "Call tools as needed (DGX/BCM RAG, assessment reader) to determine the exact steps "
                           "and produce a precise, safe execution plan.")
        else:
            # Neutral diagnostic/action planning without reset framing
            react_input = (f"Original request: {state.get('input', '')}\n\n"
                           "You are the DGX ReAct Agent. Focus on diagnosing the current DGX/SuperPOD state, "
                           "summarizing results, and providing action recommendations ONLY if clearly requested. "
                           "Avoid assuming a factory reset unless explicitly stated in the request.")

            # Optionally add first 1.5k chars of assessment/summary if available
            if state.get("assessment"):
                react_input += "\n\nNode Assessment Summary:\n" + state.get("assessment", "")[:1500]

        # ==== Invoke the agent ====
        try:
            out = await react_agent_tool.ainvoke(react_input)
        except Exception as e:
            out = f"❌ DGX ReAct agent error: {str(e)}"

        return {**state, "react_agent_output": out}

    async def generate_commands(state: OrchestratorState):
        if not bcm_rag:
            return state
        context = ("ASSESSMENT:\n" + (state.get("assessment", "") or "") + "\n\n" + "REACT_AGENT_PLAN:\n" +
                   (state.get("react_agent_output", "") or ""))
        try:
            chain_for_cmds = commands_prompt | reasoning_llm | StrOutputParser()
            bcm_query = await chain_for_cmds.ainvoke({"context": context})
        except Exception:
            bcm_query = f"CONTEXT:\n{context}"
        try:
            commands_text = await bcm_rag.ainvoke(bcm_query)
        except Exception as e:  # noqa: BLE001
            commands_text = f"❌ Command generation error: {str(e)}"
        # Extract only exact cmsh commands for execution safety; if none, set message and skip execution later
        extracted = _extract_cmsh_commands(commands_text)
        if not extracted:
            safe_msg = "❌ No valid cmsh commands extracted. Skipping execution."
            return {**state, "bcm_commands": safe_msg}
        commands_payload = "\n".join(extracted)
        return {**state, "bcm_commands": commands_payload}

    async def execute_commands(state: OrchestratorState):
        if not executor:
            return {**state, "execution_result": "ℹ️ No executor configured; skipping execution."}
        cmds = state.get("bcm_commands", "")
        if not cmds.strip() or not all(line.strip().startswith('cmsh -c "') for line in cmds.splitlines()):
            return {**state, "execution_result": "❌ No executable cmsh commands. Skipping execution."}
        try:
            exec_out = await executor.ainvoke(cmds)
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
        final = ("# 🧭 DGX Orchestration (Diagnostics Only)\n\n"
                 "## Reasoning and Decision\n" + (state.get("analysis", "") or "") + "\n\n"
                 "## ReAct Agent Analysis\n" + (state.get("react_agent_output", "") or "") + "\n\n"
                 "## Recommendation\n"
                 "Based on the analysis above, see the ReAct agent's diagnostic findings and recommendations. "
                 "No BCM commands were generated or executed as this was a diagnostics-only request.\n")
        return {**state, "final_output": final}

    # Smart routing based on LLM decision analysis
    def route_after_analysis(state: OrchestratorState):
        """Route based on LLM decision from analysis phase"""
        # Prefer the parsed/stored action_type with a safe default
        action_type = state.get("action_type", "diagnostics_only")

        # Route based on LLM decision
        routing_map = {
            "none": "synthesize",  # Skip all action steps
            "diagnostics_only": "react_agent",  # Run agent but skip execution
            "generate_bcm_commands": "react_agent",  # Normal flow
            "reset_nodes": "react_agent"  # Normal flow (could add special handling)
        }

        route = routing_map.get(action_type, "react_agent")
        logger.info("Orchestrator routing decision: %s -> %s", action_type, route)
        return route

    def route_after_react_agent(state: OrchestratorState):
        """Route after react agent based on original LLM decision"""
        action_type = state.get("action_type", "diagnostics_only")

        if action_type == "diagnostics_only":
            logger.info("Post-agent routing: %s -> synthesize_diagnostics_only", action_type)
            return "synthesize_diagnostics_only"
        else:
            logger.info("Post-agent routing: %s -> generate", action_type)
            return "generate"  # Continue to command generation

    # Build LangGraph with conditional routing
    graph = StateGraph(OrchestratorState)
    graph.add_node("assess", assess_node)
    graph.add_node("analyze", analyze_and_decide)
    graph.add_node("react_agent", run_react_agent)
    graph.add_node("generate", generate_commands)
    graph.add_node("execute", execute_commands)
    graph.add_node("synthesize", synthesize)
    graph.add_node("synthesize_diagnostics_only", synthesize_diagnostics_only)

    graph.set_entry_point("assess")
    graph.add_edge("assess", "analyze")

    # Key change: Multiple routing options from analyze
    graph.add_conditional_edges(
        "analyze",
        route_after_analysis,
        {
            "react_agent": "react_agent",  # Normal flow or diagnostics
            "synthesize": "synthesize"  # Skip all actions (action_type="none")
        })

    # Add conditional routing after react_agent based on original decision
    graph.add_conditional_edges(
        "react_agent",
        route_after_react_agent,
        {
            "generate": "generate",  # Normal flow
            "synthesize_diagnostics_only": "synthesize_diagnostics_only"  # Diagnostics only
        })

    graph.add_edge("generate", "execute")
    graph.add_edge("execute", "synthesize")
    graph.add_edge("synthesize", END)
    graph.add_edge("synthesize_diagnostics_only", END)

    app = graph.compile()

    async def _run(input_text: str) -> str:  # noqa: ARG001 - required by framework signature
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
        result = await app.ainvoke(state)
        return result.get("final_output", "❌ DGX orchestrator produced no output")

    yield FunctionInfo.from_fn(
        _run,
        description=("Analyze DGX cluster state, decide actions, generate BCM node commands, "
                     "execute with approval, and return final reasoning and results."),
    )


print("✅ DGX Orchestrator registered successfully")
