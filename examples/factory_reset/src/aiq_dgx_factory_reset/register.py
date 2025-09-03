"""
BCM Documentation RAG with LlamaIndex

This module provides accurate retrieval of BCM (Bright Cluster Manager) documentation
using LlamaIndex, LlamaParse, and NVIDIA embeddings for high-quality RAG responses.
"""

import asyncio
import glob
import logging
import os
import re
from pathlib import Path
from typing import TypedDict

import yaml
from pydantic import Field

from aiq.builder.builder import Builder
from aiq.builder.framework_enum import LLMFrameworkEnum
from aiq.builder.function_info import FunctionInfo
from aiq.cli.register_workflow import register_function
from aiq.data_models.function import FunctionBaseConfig

logger = logging.getLogger(__name__)

# ========================
# BCM Documentation RAG Tool
# ========================


class BCMDocumentationRAGConfig(FunctionBaseConfig, name="bcm_documentation_rag"):
    docs_path: str = Field(default="examples/factory_reset/src/aiq_dgx_factory_reset/docs/BCM_expert",
                           description="Path to BCM documentation directory")
    persist_dir: str = Field(default="examples/factory_reset/storage/bcm_index",
                             description="Directory to persist the vector index")
    similarity_top_k: int = Field(default=5, description="Number of top similar chunks to retrieve")
    response_mode: str = Field(default="tree_summarize", description="Response synthesis mode")
    nvidia_api_key: str = Field(default="", description="NVIDIA API key (or set NVIDIA_API_KEY env var)")
    llama_cloud_api_key: str = Field(default="", description="LlamaCloud API key (or set LLAMA_CLOUD_API_KEY env var)")


@register_function(config_type=BCMDocumentationRAGConfig)
async def bcm_documentation_rag(config: BCMDocumentationRAGConfig, _builder: Builder):
    """
    Search BCM documentation using accurate RAG retrieval
    """

    async def _search_bcm_docs(query: str) -> str:
        """Search BCM documentation with high-accuracy retrieval"""
        docs_path = config.docs_path
        persist_dir = config.persist_dir

        if not os.path.exists(docs_path):
            return f"❌ BCM documentation not found at {docs_path}"

        try:
            # Import LlamaIndex dependencies
            from llama_index.core import Document
            from llama_index.core import Settings
            from llama_index.core import StorageContext
            from llama_index.core import VectorStoreIndex
            from llama_index.core import load_index_from_storage
            from llama_index.embeddings.nvidia import NVIDIAEmbedding
            from llama_index.llms.nvidia import NVIDIA
            from llama_parse import LlamaParse

            # Set up API keys
            nvidia_api_key = config.nvidia_api_key or os.getenv("NVIDIA_API_KEY")
            llama_api_key = config.llama_cloud_api_key or os.getenv("LLAMA_CLOUD_API_KEY")

            if not nvidia_api_key:
                return ("❌ NVIDIA API key not provided. Set NVIDIA_API_KEY "
                        "environment variable or provide in config.")

            if not llama_api_key:
                return ("❌ LLAMA_CLOUD_API_KEY not provided. Set LLAMA_CLOUD_API_KEY "
                        "environment variable or provide in config.")

            os.environ["NVIDIA_API_KEY"] = nvidia_api_key
            os.environ["LLAMA_CLOUD_API_KEY"] = llama_api_key

            # Configure LlamaIndex with NVIDIA models for accuracy
            Settings.llm = NVIDIA(model="meta/llama-3.3-70b-instruct")
            Settings.embed_model = NVIDIAEmbedding(model="nvidia/llama-3.2-nv-embedqa-1b-v2", truncate="END")
            # Enable debug/tracing so reasoning signals are visible in logs (optional)
            try:
                from llama_index.core.callbacks import CallbackManager
                from llama_index.core.callbacks import LlamaDebugHandler
                from llama_index.core.callbacks import TokenCountingHandler
                Settings.callback_manager = CallbackManager(
                    [LlamaDebugHandler(print_trace_on_end=True), TokenCountingHandler()])
            except Exception:
                # Debug handlers are optional; ignore if unavailable
                pass

            logger.info("Processing BCM documentation from %s", docs_path)

            # Check for existing index
            docstore_path = os.path.join(persist_dir, "docstore.json")
            if os.path.exists(docstore_path):
                logger.info("Loading existing BCM index...")
                storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
                index = load_index_from_storage(storage_context)
            else:
                logger.info("Creating new BCM index with LlamaParse...")
                os.makedirs(persist_dir, exist_ok=True)

                documents = []
                docs_path_obj = Path(docs_path)

                # Process PDF files with LlamaParse for high-quality extraction
                pdf_files = list(docs_path_obj.glob("*.pdf"))
                if pdf_files and llama_api_key:
                    logger.info("Found %d PDF files, processing with LlamaParse...", len(pdf_files))

                    for pdf_file in pdf_files:
                        try:
                            logger.info("Processing %s individually...", pdf_file.name)

                            # Create a fresh parser instance for each file
                            file_parser = LlamaParse(verbose=True)
                            pdf_docs = file_parser.load_data(str(pdf_file))

                            for doc in pdf_docs:
                                doc.metadata["source"] = str(pdf_file)
                                doc.metadata["file_name"] = pdf_file.name

                            documents.extend(pdf_docs)
                            logger.info("Successfully processed %s (%d documents)", pdf_file.name, len(pdf_docs))

                            # Clean up
                            del file_parser

                        except Exception as e:
                            logger.warning("Failed to parse %s, skipping PDF processing: %s", pdf_file, e)
                            logger.info("Continuing with other document types...")
                            continue
                elif pdf_files and not llama_api_key:
                    logger.info("Found %d PDF files but no LlamaCloud API key provided, skipping PDF processing",
                                len(pdf_files))

                # Process markdown files if any
                md_files = list(docs_path_obj.glob("*.md"))
                if md_files:
                    logger.info("Found %d markdown files...", len(md_files))
                    for md_file in md_files:
                        try:
                            with open(md_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                            documents.append(
                                Document(text=content, metadata={
                                    "source": str(md_file), "file_name": md_file.name
                                }))
                            logger.info("Processed %s", md_file.name)
                        except Exception as e:
                            logger.warning("Failed to load %s: %s", md_file, e)

                if not documents:
                    return f"❌ No BCM documentation files found in {docs_path}"

                logger.info("Creating index from %d documents...", len(documents))
                index = VectorStoreIndex.from_documents(documents)
                index.storage_context.persist(persist_dir=persist_dir)
                logger.info("Index created and persisted successfully")

            # Create query engine optimized for accuracy
            query_engine = index.as_query_engine(similarity_top_k=config.similarity_top_k,
                                                 response_mode=config.response_mode,
                                                 verbose=True)

            logger.info("Executing query: %s", query)
            response = query_engine.query(query)

            # Format the response with source information
            result = "🤖 **BCM Documentation Expert**\n\n"
            result += f"**Query:** {query}\n\n"
            result += f"**Answer:**\n{str(response)}\n\n"

            # Add source information if available
            if hasattr(response, 'source_nodes') and response.source_nodes:
                result += "**Sources:**\n"
                for i, node in enumerate(response.source_nodes[:3], 1):  # Show top 3 sources
                    source = node.metadata.get('file_name', 'Unknown')
                    score = getattr(node, 'score', 'N/A')
                    result += f"{i}. {source} (relevance: {score:.3f})\n"
                result += "\n"
                # Show brief context snippets to reveal what informed the answer
                result += "**Top retrieved context (snippets):**\n"
                for i, node in enumerate(response.source_nodes[:3], 1):
                    source = node.metadata.get('file_name', 'Unknown')
                    text = getattr(node, 'text', '') or getattr(node, 'node', getattr(node, 'document', None))
                    snippet = ''
                    if isinstance(text, str):
                        snippet = text.strip().replace("\n", " ")[:500]
                    elif hasattr(node, 'get_text'):
                        try:
                            snippet = node.get_text().strip().replace("\n", " ")[:500]
                        except Exception:
                            snippet = ''
                    if snippet:
                        result += f"{i}. {source}: {snippet}…\n"

            result += "📋 **Source:** BCM Administration Manual\n\n"
            result += "⚠️  **Note:** Please verify commands in your specific BCM environment before execution."

            return result

        except Exception as e:
            logger.error("Error in BCM documentation search: %s", str(e))
            return f"❌ Error in BCM analysis: {str(e)}\n\nPlease check your API keys and network connection."

    yield FunctionInfo.from_fn(_search_bcm_docs,
                               description=("STEP 2: Generate BCM (Bright Cluster Manager) commands based on "
                                            "networking requirements from Step 1. Use ONLY after consulting "
                                            "networking_expert first."))


print("✅ BCM Documentation RAG function registered successfully")

# ========================
# Human-in-the-Loop (HITL) Approval and BCM Command Executor
# ========================


class HITLCodeApprovalConfig(FunctionBaseConfig, name="hitl_code_approval"):
    """HITL function to prompt the user for approval of BCM commands."""

    prompt: str = Field(..., description="Base prompt shown to the user before command list")


@register_function(config_type=HITLCodeApprovalConfig)
async def hitl_code_approval(config: HITLCodeApprovalConfig, _builder: Builder):
    """Prompt the user with the command list and return True if approved (yes), else False."""

    async def _approve(commands_text: str) -> bool:
        import re

        from aiq.builder.context import AIQContext
        from aiq.data_models.interactive import HumanPromptText
        from aiq.data_models.interactive import InteractionResponse

        aiq_context = AIQContext.get()
        user_input_manager = aiq_context.user_interaction_manager

        approval_prompt = (f"{config.prompt}\n\n"
                           f"The following BCM commands are proposed for execution:\n"
                           f"----------------------------------------\n"
                           f"{commands_text}\n"
                           f"----------------------------------------\n\n"
                           "Respond with 'yes' to approve or 'no' to cancel.")

        human_prompt_text = HumanPromptText(text=approval_prompt, required=True, placeholder="yes/no")
        response: InteractionResponse = await user_input_manager.prompt_user_input(human_prompt_text)
        response_str = (response.content.text or "").lower()  # type: ignore[attr-defined]
        return re.search(r"\byes\b", response_str) is not None

    yield FunctionInfo.from_fn(_approve, description="Prompt the user to approve BCM command execution (yes/no)")


print("✅ HITL Code Approval function registered successfully")


class CodeExecutionWithApprovalConfig(FunctionBaseConfig, name="code_execution_with_approval"):
    """Execute BCM commands with optional validation and human approval."""

    cluster_host: str = Field(...,
                              description="Target cluster hostname or IP for SSH execution. Use 'localhost' for local.")
    cluster_user: str = Field(..., description="SSH username for the target cluster")
    timeout: int = Field(default=600, description="Timeout (seconds) for command execution")
    dry_run: bool = Field(default=True, description="If true, validate/approve but do not execute")
    coder_llm_name: str | None = Field(default=None, description="Optional LLM name for command validation")
    hitl_approval_fn: str = Field(..., description="Registered HITL function name to call for approval")


@register_function(config_type=CodeExecutionWithApprovalConfig)
async def code_execution_with_approval(config: CodeExecutionWithApprovalConfig, builder: Builder):
    """Tool that accepts a multi-line string of cmsh commands and executes them after approval."""

    import asyncio

    async def _execute(bcm_commands: str) -> str:
        import tempfile

        if not bcm_commands or not bcm_commands.strip():
            return "❌ No BCM commands provided for execution"

        # Optional LLM validation step (best-effort)
        validation_notes = ""
        if config.coder_llm_name:
            try:
                from aiq.builder.framework_enum import LLMFrameworkEnum
                llm = await builder.get_llm(config.coder_llm_name, wrapper_type=LLMFrameworkEnum.LANGCHAIN)
                critique = await llm.ainvoke(
                    "Review the following Bright Cluster Manager cmsh commands for safety and correctness. "
                    "Respond briefly with potential risks or confirm they look safe to run.\n\n" + bcm_commands)
                validation_notes = f"\n🔎 Validation (coder): {str(critique)}\n"
            except Exception:
                validation_notes = "\n🔎 Validation (coder): skipped (LLM unavailable)\n"

        # Human approval via configured HITL function
        try:
            approval_fn = builder.get_function(config.hitl_approval_fn)
        except Exception:
            return ("❌ HITL approval function not found: " + config.hitl_approval_fn +
                    "\nPlease ensure it is registered and referenced correctly in the config.")

        approved: bool = await approval_fn.ainvoke(bcm_commands)
        if not approved:
            return ("❌ Execution cancelled by user.\n\n"
                    "No changes were made to the cluster. You can modify commands and try again."
                    f"{validation_notes}")

        if config.dry_run:
            return ("✅ Dry run approval complete. Commands validated and approved, but NOT executed.\n\n"
                    "Approved BCM commands:\n" + bcm_commands + validation_notes)

        # Live execution (local or remote via SSH)
        try:
            script_content = ("#!/bin/bash\n"
                              "set -e\n"
                              "set -x\n"
                              "echo 'Starting BCM command execution'\n"
                              "echo 'Timestamp:' $(date)\n"
                              "echo 'User:' $(whoami)\n"
                              "echo 'Host:' $(hostname)\n"
                              "echo '===================================='\n" + bcm_commands +
                              "\necho '===================================='\n"
                              "echo 'BCM command execution completed successfully'\n"
                              "echo 'Timestamp:' $(date)\n")

            with tempfile.NamedTemporaryFile(mode="w", suffix=".sh", delete=False) as f:
                f.write(script_content)
                script_path = f.name
            os.chmod(script_path, 0o755)

            if config.cluster_host == "localhost":
                cmd = [script_path]
                proc = await asyncio.create_subprocess_exec(*cmd,
                                                            stdout=asyncio.subprocess.PIPE,
                                                            stderr=asyncio.subprocess.PIPE)
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=config.timeout)
            else:
                scp_cmd = [
                    "scp",
                    script_path,
                    f"{config.cluster_user}@{config.cluster_host}:/tmp/bcm_execution.sh",
                ]
                scp_proc = await asyncio.create_subprocess_exec(*scp_cmd,
                                                                stdout=asyncio.subprocess.PIPE,
                                                                stderr=asyncio.subprocess.PIPE)
                await scp_proc.communicate()
                if scp_proc.returncode != 0:
                    return "❌ Failed to upload execution script to cluster"

                ssh_cmd = [
                    "ssh",
                    f"{config.cluster_user}@{config.cluster_host}",
                    "chmod +x /tmp/bcm_execution.sh && /tmp/bcm_execution.sh",
                ]
                proc = await asyncio.create_subprocess_exec(*ssh_cmd,
                                                            stdout=asyncio.subprocess.PIPE,
                                                            stderr=asyncio.subprocess.PIPE)
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=config.timeout)

            # Clean up local script
            try:
                os.unlink(script_path)
            except Exception:
                pass

            if proc.returncode == 0:
                return ("✅ Command execution successful.\n\n"
                        "Execution output (stdout):\n" + stdout.decode("utf-8") + validation_notes)
            return ("❌ Command execution failed.\n\n"
                    "STDERR:\n" + stderr.decode("utf-8") + "\nSTDOUT:\n" + stdout.decode("utf-8") + validation_notes)
        except asyncio.TimeoutError:
            return f"❌ Command execution timed out after {config.timeout} seconds"
        except Exception as e:  # noqa: BLE001
            return f"❌ Execution error: {str(e)}"

    yield FunctionInfo.from_fn(
        _execute,
        description=("Execute BCM (cmsh) commands after optional LLM validation and HITL approval. "
                     "Input must be a multi-line string of commands."),
    )


print("✅ BCM Code Execution with Approval tool registered successfully")

# Import networking and DGX modules to ensure all functions are registered
try:
    from . import dgx_register  # noqa: F401
    from . import network_register  # noqa: F401
    print("✅ Network and DGX tools registered successfully")
except Exception as e:
    print(f"⚠️ Additional tools not loaded: {e}")
