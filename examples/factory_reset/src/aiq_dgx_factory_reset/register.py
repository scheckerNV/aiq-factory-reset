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
            result = "**BCM Documentation Expert**\n\n"
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

            result += "**Source:** BCM Administration Manual\n\n"
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
# Networking Expert RAG Tool
# ========================


class NetworkingExpertRAGConfig(FunctionBaseConfig, name="networking_expert_rag"):
    """Configuration for networking documentation RAG tool"""
    docs_path: str = Field(default="examples/factory_reset/src/aiq_dgx_factory_reset/docs/networking_expert",
                           description="Path to networking documentation directory")
    persist_dir: str = Field(default="examples/factory_reset/storage/networking_index",
                             description="Directory to persist the vector index")
    similarity_top_k: int = Field(default=5, description="Number of top similar chunks to retrieve")
    response_mode: str = Field(default="tree_summarize", description="Response synthesis mode")
    expert_type: str = Field(default="Networking", description="Type of expert")
    nvidia_api_key: str = Field(default="", description="NVIDIA API key (or set NVIDIA_API_KEY env var)")
    llama_cloud_api_key: str = Field(default="", description="LlamaCloud API key (or set LLAMA_CLOUD_API_KEY env var)")


@register_function(config_type=NetworkingExpertRAGConfig)
async def networking_expert_rag(config: NetworkingExpertRAGConfig, _builder: Builder):
    """
    Search Networking documentation using accurate RAG retrieval
    """

    async def _search_networking_docs(query: str) -> str:
        """Search Networking documentation with high-accuracy retrieval"""
        docs_path = config.docs_path
        persist_dir = config.persist_dir

        if not os.path.exists(docs_path):
            return f"❌ Networking documentation not found at {docs_path}"

        try:
            # Import LlamaIndex dependencies
            import yaml
            from llama_index.core import Document
            from llama_index.core import Settings
            from llama_index.core import StorageContext
            from llama_index.core import VectorStoreIndex
            from llama_index.core import load_index_from_storage
            from llama_index.embeddings.nvidia import NVIDIAEmbedding
            from llama_index.llms.nvidia import NVIDIA

            # from llama_parse import LlamaParse  # Not currently used
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
                pass

            logger.info("Processing Networking documentation from %s", docs_path)

            # Check for existing index
            docstore_path = os.path.join(persist_dir, "docstore.json")
            if os.path.exists(docstore_path):
                logger.info("Loading existing Networking index...")
                storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
                index = load_index_from_storage(storage_context)
            else:
                logger.info("Creating new Networking index with LlamaParse...")
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
                            logger.warning("PDF processing currently disabled - LlamaParse not imported")
                            continue
                            # # Create a fresh parser instance for each file
                            # file_parser = LlamaParse(verbose=True)
                            # pdf_docs = file_parser.load_data(str(pdf_file))

                            # for doc in pdf_docs:
                            #     doc.metadata["source"] = str(pdf_file)
                            #     doc.metadata["file_name"] = pdf_file.name

                            # documents.extend(pdf_docs)
                            # logger.info("Successfully processed %s (%d documents)", pdf_file.name, len(pdf_docs))

                            # # Clean up
                            # del file_parser

                        except Exception as e:
                            logger.warning("Failed to parse %s, skipping PDF processing: %s", pdf_file, e)
                            logger.info("Continuing with other document types...")
                            continue
                elif pdf_files and not llama_api_key:
                    logger.info("Found %d PDF files but no LlamaCloud API key provided, skipping PDF processing",
                                len(pdf_files))

                # Process YAML files (primary config files)
                yaml_files = list(docs_path_obj.glob("*.yaml")) + list(docs_path_obj.glob("*.yml"))
                if yaml_files:
                    logger.info("📄 Found %d YAML files...", len(yaml_files))
                    for yaml_file in yaml_files:
                        try:
                            with open(yaml_file, 'r', encoding='utf-8') as f:
                                content = f.read()

                            # Parse YAML for metadata
                            try:
                                yaml_data = yaml.safe_load(content)
                                metadata = {"source": str(yaml_file), "file_name": yaml_file.name, "file_type": "yaml"}
                                if isinstance(yaml_data, dict):
                                    if "metadata" in yaml_data:
                                        metadata.update(yaml_data["metadata"])
                                    if "cluster" in yaml_data:
                                        metadata["cluster_name"] = yaml_data.get("cluster", {}).get("name", "unknown")
                            except Exception:
                                metadata = {"source": str(yaml_file), "file_name": yaml_file.name, "file_type": "yaml"}

                            documents.append(Document(text=content, metadata=metadata))
                            logger.info("✅ Processed %s", yaml_file.name)
                        except Exception as e:
                            logger.warning("⚠️ Failed to load %s: %s", yaml_file, e)

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
                    return f"❌ No Networking documentation files found in {docs_path}"

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
            result = "**Networking Documentation Expert**\n\n"
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

            result += "⚠️  **Note:** Please verify commands in your specific Cluster environment before execution."

            return result

        except Exception as e:
            logger.error("Error in Networking documentation search: %s", str(e))
            return f"❌ Error in Networking analysis: {str(e)}\n\nPlease check your API keys and network connection."

    yield FunctionInfo.from_fn(_search_networking_docs,
                               description=("STEP 1: Assess the current state of the cluster and the desired state."))


print("✅ Networking Expert RAG tool registered successfully")

# ========================
# Networking Expert Assessment Tool
# ========================


class NetworkAssessmentToolConfig(FunctionBaseConfig, name="network_assessment_tool"):
    cluster_host: str = Field(description="Virtual cluster hostname/IP")
    cluster_user: str = Field(description="SSH username for cluster access")
    timeout: int = Field(default=300, description="Assessment timeout in seconds")


@register_function(config_type=NetworkAssessmentToolConfig)
async def network_assessment_tool(config: NetworkAssessmentToolConfig, _builder: Builder):
    """Comprehensive network assessment tool for BCM clusters"""

    async def _run_network_assessment(input_message: str) -> str:
        """Execute comprehensive network assessment"""
        import asyncio
        import tempfile

        # Create the assessment script
        # Read the shell script content from the external file
        script_path_on_disk = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                                           "scripts",
                                           "network_assessment.sh")
        with open(script_path_on_disk, "r", encoding="utf-8") as f:
            script_content = f.read()

        try:
            # Upload and execute the script
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(script_content)
                script_path = f.name

            # Make executable
            os.chmod(script_path, 0o755)

            if config.cluster_host == "localhost":
                # Execute locally
                cmd = [script_path]
                proc = await asyncio.create_subprocess_exec(*cmd,
                                                            stdout=asyncio.subprocess.PIPE,
                                                            stderr=asyncio.subprocess.PIPE)
                stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=config.timeout)
                returncode = proc.returncode
            else:
                # Copy script to cluster
                scp_cmd = [
                    "scp", script_path, f"{config.cluster_user}@{config.cluster_host}:/tmp/network_assessment.sh"
                ]

                scp_process = await asyncio.create_subprocess_exec(*scp_cmd,
                                                                   stdout=asyncio.subprocess.PIPE,
                                                                   stderr=asyncio.subprocess.PIPE)
                await scp_process.communicate()

                if scp_process.returncode != 0:
                    return "❌ Failed to upload assessment script to cluster"

                # Execute script on cluster
                ssh_cmd = [
                    "ssh",
                    f"{config.cluster_user}@{config.cluster_host}",
                    "chmod +x /tmp/network_assessment.sh && /tmp/network_assessment.sh"
                ]

                ssh_process = await asyncio.create_subprocess_exec(*ssh_cmd,
                                                                   stdout=asyncio.subprocess.PIPE,
                                                                   stderr=asyncio.subprocess.PIPE)

                stdout, stderr = await asyncio.wait_for(ssh_process.communicate(), timeout=config.timeout)
                returncode = ssh_process.returncode

            # Clean up local script
            os.unlink(script_path)

            if returncode == 0:
                location = "locally" if config.cluster_host == "localhost" else "on cluster"
                return f"""✅ Network assessment completed successfully!

Assessment Output:
{stdout.decode('utf-8')}

Results saved {location} in timestamped directory.
Use the network_results_reader tool to analyze the results.

Next steps:
1. Use network_results_reader to parse the assessment data
2. Compare current state with desired configuration
3. Generate remediation plan based on differences
"""
            else:
                return f"❌ Assessment script failed:\n{stderr.decode('utf-8')}"

        except asyncio.TimeoutError:
            return f"❌ Assessment timed out after {config.timeout} seconds"
        except Exception as e:
            return f"❌ Assessment error: {str(e)}"

    yield FunctionInfo.from_fn(_run_network_assessment, description="Run comprehensive BCM cluster network assessment")


print("✅ Networking Expert Network Assessment tool registered successfully")

# ========================
# Networking Expert Network Results Reader Tool
# ========================


class NetworkResultsReaderConfig(FunctionBaseConfig, name="network_results_reader"):
    cluster_host: str = Field(description="Virtual cluster hostname/IP")
    cluster_user: str = Field(description="SSH username for cluster access")
    results_directory: str = Field(description="Assessment results directory path")


@register_function(config_type=NetworkResultsReaderConfig)
async def network_results_reader(config: NetworkResultsReaderConfig, _builder: Builder):
    """Read and analyze network assessment results"""

    async def _read_assessment_results(query: str) -> str:
        """Read specific assessment results based on query"""
        import asyncio

        try:
            # Handle default query
            if not query or query.strip() == "":
                query = "summary"

            # Determine which files to read based on query
            if "summary" in query.lower():
                files_to_read = ["00_SUMMARY.txt"]
            elif "device" in query.lower():
                files_to_read = ["01_device_status.txt", "02_device_list.txt"]
            elif "connectivity" in query.lower():
                files_to_read = ["05_connectivity.txt", "06_connectivity_stats.txt"]
            elif "switch" in query.lower():
                files_to_read = ["10_switch_*", "11_switch_*", "12_switch_*"]
            elif "network" in query.lower():
                files_to_read = ["03_networks.txt", "04_interfaces.txt"]
            elif "full" in query.lower() or "all" in query.lower():
                # Return combined assessment data for orchestrator
                files_to_read = [
                    "00_SUMMARY.txt",
                    "03_networks.txt",
                    "02_device_list.txt",
                    "04_interfaces.txt",
                    "05_connectivity.txt"
                ]
            else:
                files_to_read = ["00_SUMMARY.txt"]

            results = []

            # Determine assessment directory (explicit path, stable symlink, or latest)
            latest_dir = None

            # 1. Check for explicit directory in query
            explicit = None
            for token in query.split():
                if token.startswith("/tmp/network_assessment_"):
                    explicit = token
                    break

            if explicit:
                # Use explicit directory path
                latest_dir = explicit
                logger.info(f"Using explicit directory from query: {latest_dir}")
            else:
                # 2. Try stable symlink first
                if config.cluster_host == "localhost":
                    import os
                    symlink_path = "/tmp/network_assessment_latest"
                    if os.path.exists(symlink_path) and os.path.isdir(symlink_path):
                        latest_dir = symlink_path
                        logger.info(f"Using stable symlink: {latest_dir}")
                else:
                    # Check remote symlink
                    symlink_cmd = [
                        "ssh",
                        f"{config.cluster_user}@{config.cluster_host}",
                        "test -d /tmp/network_assessment_latest && echo /tmp/network_assessment_latest"
                    ]
                    symlink_proc = await asyncio.create_subprocess_exec(*symlink_cmd,
                                                                        stdout=asyncio.subprocess.PIPE,
                                                                        stderr=asyncio.subprocess.PIPE)
                    symlink_stdout, _ = await symlink_proc.communicate()
                    if symlink_proc.returncode == 0 and symlink_stdout.strip():
                        latest_dir = symlink_stdout.decode('utf-8').strip()
                        logger.info(f"Using remote stable symlink: {latest_dir}")

                # 3. Fall back to finding latest directory by timestamp
                if not latest_dir:
                    latest_dir_cmd = [
                        "ssh",
                        f"{config.cluster_user}@{config.cluster_host}",
                        f"ls -td {config.results_directory} 2>/dev/null | head -1"
                    ]

                    latest_process = await asyncio.create_subprocess_exec(*latest_dir_cmd,
                                                                          stdout=asyncio.subprocess.PIPE,
                                                                          stderr=asyncio.subprocess.PIPE)

                    latest_stdout, latest_stderr = await latest_process.communicate()

                    if latest_process.returncode == 0 and latest_stdout.strip():
                        latest_dir = latest_stdout.decode('utf-8').strip()
                        logger.info(f"Found latest assessment directory: {latest_dir}")

            if latest_dir:

                for file_pattern in files_to_read:
                    ssh_cmd = [
                        "ssh",
                        f"{config.cluster_user}@{config.cluster_host}",
                        f"find {latest_dir} -name '{file_pattern}' -exec cat {{}} \\;"
                    ]

                    process = await asyncio.create_subprocess_exec(*ssh_cmd,
                                                                   stdout=asyncio.subprocess.PIPE,
                                                                   stderr=asyncio.subprocess.PIPE)

                    stdout, stderr = await process.communicate()

                    if process.returncode == 0:
                        content = stdout.decode('utf-8')
                        if content.strip():
                            results.append(f"📄 {file_pattern}:\n{content}\n{'='*50}\n")
            else:
                logger.error(f"Could not find latest assessment directory matching {config.results_directory}")

            if results:
                return f"""📊 Network Assessment Results:

{chr(10).join(results)}

💡 Analysis complete! Use this data to:
1. Compare with desired state configuration
2. Identify configuration gaps
3. Plan remediation steps
"""
            else:
                return "❌ No assessment results found. Run network_assessment_tool first."

        except Exception as e:
            return f"❌ Error reading assessment results: {str(e)}"

    yield FunctionInfo.from_fn(_read_assessment_results, description="Read and analyze network assessment results")


print("✅ Networking Expert Network Reader tool registered successfully")

# ========================
# Network Config YAML Extractor
# ========================


class NetworkConfigExtractorConfig(FunctionBaseConfig, name="network_config_extractor"):
    networking_docs_path: str = Field(default="examples/factory_reset/src/aiq_dgx_factory_reset/docs/networking_expert",
                                      description="Path to networking expert documentation directory")


@register_function(config_type=NetworkConfigExtractorConfig)
async def network_config_extractor(config: NetworkConfigExtractorConfig, _builder: Builder):
    """Extract network configuration directly from YAML config files"""

    async def _extract_network_config_from_yaml(query: str) -> str:
        """Extract network configuration directly from YAML config file"""
        try:
            # Use the config path, not the input parameter
            networking_docs_path = config.networking_docs_path

            # If it's already an absolute path to a file, use it directly
            if networking_docs_path.endswith('.yaml') and os.path.isfile(networking_docs_path):
                config_file = networking_docs_path
            else:
                # Otherwise, look for config files in the directory
                config_files = glob.glob(os.path.join(networking_docs_path, "*_config.yaml"))
                if not config_files:
                    return f"No network config YAML found in {networking_docs_path}/"
                config_file = config_files[0]

            logger.info(f"Reading network config from: {config_file}")

            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f)

            facts = []
            cluster_name = "unknown"

            # Extract cluster name
            if 'metadata' in config_data and 'cluster_name' in config_data['metadata']:
                cluster_name = config_data['metadata']['cluster_name']
            elif 'cluster' in config_data and 'name' in config_data['cluster']:
                cluster_name = config_data['cluster']['name']

            facts.append(f"CLUSTER: {cluster_name}")

            # Parse network fabrics (handles both schecker and demeter formats)
            if 'network_fabrics' in config_data:
                # Demeter format: network_fabrics.management.subnet
                for fabric_name, fabric_config in config_data['network_fabrics'].items():
                    name = fabric_config.get('name', fabric_name)
                    subnet = fabric_config.get('subnet')
                    gateway = fabric_config.get('gateway')
                    interface = fabric_config.get('interface')
                    fabric_type = fabric_config.get('fabric_type', 'ethernet')
                    if subnet:
                        interface_str = f" interface {interface}" if interface else ""
                        facts.append(
                            f"NETWORK: {name} uses {subnet} gateway {gateway} type {fabric_type}{interface_str}")

            elif 'networks' in config_data:
                # Schecker format: networks.internal.subnet
                for net_name, net_config in config_data['networks'].items():
                    name = net_config.get('name')
                    subnet = net_config.get('subnet')
                    gateway = net_config.get('gateway')
                    interface = net_config.get('interface')
                    if subnet and name:
                        interface_str = f" interface {interface}" if interface else ""
                        facts.append(f"NETWORK: {name} uses {subnet} gateway {gateway}{interface_str}")

            # Parse node definitions for head node and sample workers
            if 'nodes' in config_data:
                # Extract head node and first few worker nodes
                node_count = 0
                for node_name, node_config in config_data['nodes'].items():
                    if node_count >= 5:  # Limit to first 5 nodes
                        break
                    if 'networks' in node_config:
                        for net_type, net_info in node_config['networks'].items():
                            if isinstance(net_info, dict) and 'ip' in net_info:
                                facts.append(f"NODE: {node_name} on {net_type} = {net_info['ip']}")
                    elif 'hostname' in node_config:
                        # Handle simpler node format
                        hostname = node_config['hostname']
                        facts.append(f"NODE: {hostname}")
                    node_count += 1

            # Parse infrastructure nodes if present
            if 'infrastructure' in config_data:
                infra = config_data['infrastructure']
                if 'management_nodes' in infra:
                    for node_name, node_config in infra['management_nodes'].items():
                        if 'ip' in node_config:
                            facts.append(f"MGMT_NODE: {node_name} = {node_config['ip']}")

            # If no detailed network info was found, try to extract from other sections
            if len([f for f in facts if f.startswith('NETWORK:')]) == 0:
                facts.append("WARNING: No network configuration found in YAML")

            result = '\n'.join(facts)
            logger.info(f"Extracted {len(facts)} configuration facts from YAML")
            return result

        except Exception as e:
            error_msg = f"❌ Error reading YAML config: {str(e)}"
            logger.error(error_msg)
            return error_msg

    yield FunctionInfo.from_fn(_extract_network_config_from_yaml,
                               description="Extract network configuration from YAML files")


print("✅ Network Config Extractor tool registered successfully")

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

# ========================
# LangGraph Network Orchestrator
# ========================


def _net_truncate(text: str, limit: int = 200_000) -> str:
    return text if not text or len(text) <= limit else text[:limit] + "\n...[truncated]...\n"


def _net_extract_cmsh_commands(text: str) -> list[str]:
    cmds = []
    for line in (text or "").splitlines():
        s = line.strip()
        if s.startswith('cmsh -c "') or s.startswith("cmsh -c '") or s.lower().startswith("cmsh -c "):
            # normalize quotes to double
            if s.startswith("cmsh -c '"):
                s = 'cmsh -c "' + s[len("cmsh -c '"):-1] + '"'
            cmds.append(s)
    return cmds


def _net_filter_placeholders(cmds: list[str]) -> list[str]:
    forbidden = ["<", "PLACEHOLDER", "NODE_NAME", "INTERFACE", "ROUTE_NAME"]
    out = []
    for c in cmds:
        if any(tok in c for tok in forbidden):
            logger.info("Filtered (placeholder): %s", c)
            continue
        out.append(c.rstrip(";"))
    return out


def _net_extract_requested_nodes(s: str) -> list[str]:
    return sorted(set(re.findall(r'\bnode\d+\b', (s or "").lower())))


# Prompts
DEFAULT_NET_COMMANDS_PROMPT = """You are a Bright Cluster Manager (BCM) SRE. \
Using the CONTEXT, produce networking commands.

Output format (must match exactly):
- First print a section header: Rationale:
  - Then 3–5 concise bullets referencing snippets from CONTEXT (no raw dumps).
- Then print a section header: Commands:
  - Output only bare lines: cmsh -c "<command>"
  - ASCII double quotes, no bullets/numbering/code fences/comments.
  - One command per line.

Rules:
- Scope to ALLOWED_NODES and referenced interfaces/networks only; do not change head/mgmt nodes.
- Prefer safe, idempotent steps for diagnostics-only.
- If USER_REQUEST explicitly asks to reset/revert networking, generate the per-node corrective \
sequence for each node in ALLOWED_NODES, covering interface reconfig, network assignment, and commit. \
Include verification (show).
- Use actual names from CONTEXT; do not invent values. If unknown, emit a discovery command \
first (e.g., device; device use <node>; network; list).
- Avoid cluster-wide changes.

CONTEXT
---
{context}
---"""

NET_SUMMARY_PROMPT = """You are a BCM networking SRE. Summarize the network assessment for the user's question.

Question: {question}

Assessment Extract:
{results}

Write a concise, actionable summary:
- Current networking state: notable issues, unreachable nodes, misconfigs
- Critical incidents
- Collection gaps and implications
- Recommended next steps (2–5 bullets), safe and non-destructive
Keep it tight; no raw dumps.
"""


class NetworkOrchestratorConfig(FunctionBaseConfig, name="network_orchestrator"):
    reasoning_llm_name: str = Field(description="LLM used for reasoning and planning")
    executor_fn: str = Field(default="code_execution_with_approval", description="Executor tool to run cmsh commands")
    commands_prompt: str | None = Field(default=None, description="Override command-gen prompt text")
    commands_prompt_path: str | None = Field(default=None, description="Path to prompt file (optional)")
    include_llm_rationale: bool = Field(default=True, description="Include LLM rationale in final output")
    include_prompts_in_output: bool = Field(default=False, description="Include rendered prompts/outputs (debug)")


def _net_load_prompt(cfg: NetworkOrchestratorConfig) -> str:
    if cfg.commands_prompt:
        return cfg.commands_prompt
    if cfg.commands_prompt_path and os.path.exists(cfg.commands_prompt_path):
        return Path(cfg.commands_prompt_path).read_text(encoding="utf-8")
    return DEFAULT_NET_COMMANDS_PROMPT


@register_function(config_type=NetworkOrchestratorConfig, framework_wrappers=[LLMFrameworkEnum.LANGCHAIN])
async def network_orchestrator(config: NetworkOrchestratorConfig, builder: Builder):
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import PromptTemplate
    from langgraph.graph import END
    from langgraph.graph import StateGraph

    commands_prompt = PromptTemplate.from_template(_net_load_prompt(config))
    summary_prompt = PromptTemplate.from_template(NET_SUMMARY_PROMPT)

    class State(TypedDict, total=False):
        input: str
        action_type: str
        results_query: str
        requested_nodes: list[str]
        assessment: str
        results_text: str
        results_dir: str
        analysis: str
        assessment_summary: str
        bcm_commands: str
        bcm_rationale: str
        llm_cmds_raw: str
        summary_prompt: str
        execution_result: str
        final_output: str

    # Routing (regex-first)
    def classify(user_input: str) -> tuple[str, str, list[str]]:
        ui = user_input or ""
        ui_l = ui.lower()
        results_query = "summary"
        if any(t in ui_l for t in ["full", "all", "detailed", "complete"]):
            results_query = "full"
        elif any(t in ui_l for t in ["overview", "status", "state", "health", "show", "list"]):
            results_query = "overview"

        reset_actions = r"(reset|re-?image|re-?install|re-?provision|wipe|factory\s*reset|revert|restore)"
        cmd_verbs = r"(give me|provide|generate|produce|write|create|output)"
        cmd_nouns = r"(cmsh|commands?)"
        reset_regex = re.compile(rf"{reset_actions}", re.I)
        generate_cmds_regex = re.compile(rf"({cmd_verbs}).*({cmd_nouns})|({cmd_nouns}).*({cmd_verbs})", re.I)

        if reset_regex.search(ui):
            action = "reset_network"
        elif generate_cmds_regex.search(ui):
            action = "generate_network_commands"
        else:
            action = "diagnostics_only"

        nodes = _net_extract_requested_nodes(ui)
        return action, results_query, nodes

    async def analyze(state: State):
        user_input = state.get("input", "")
        logger.info("analyze: Starting regex-based classification for input: %s", user_input[:100])

        action, results_query, nodes = classify(user_input)

        logger.info("✅ analyze: Classification completed - action_type=%s, results_query=%s, nodes=%s",
                    action,
                    results_query,
                    nodes)

        analysis = "### Reasoning\n" + "\n".join([
            f"- Detected action_type: {action}",
            f"- Results query: {results_query}",
            f"- Requested nodes: {', '.join(nodes) if nodes else 'none'}",
        ])
        return {
            **state,
            "action_type": action,
            "results_query": results_query,
            "requested_nodes": nodes,
            "analysis": analysis
        }

    async def assess(state: State):
        logger.info("assess: Starting network assessment")

        # Run assessment
        try:
            assess_tool = builder.get_function("network_assessment_tool")
            logger.info("assess: Executing network_assessment_tool")
            assess_out = await asyncio.wait_for(assess_tool.ainvoke("Run comprehensive network assessment"),
                                                timeout=300)
            logger.info("✅ assess: Network assessment completed successfully")
        except Exception as e:
            logger.error("❌ assess: Network assessment failed: %s", e)
            assess_out = f"❌ Network assessment error: {e}"

        # Extract results directory from assessment output
        results_dir = ""
        if assess_out:
            m = re.search(r"(/tmp/network_assessment_[0-9_]+)", assess_out)
            if m:
                results_dir = m.group(1)
                logger.info("assess: Extracted results directory: %s", results_dir)
            else:
                logger.warning("assess: Could not extract results directory from assessment output")

        # Read results with explicit directory if available
        results_text = ""
        try:
            reader = builder.get_function("network_results_reader")
            rq = state.get("results_query", "overview") or "overview"
            # Include directory in query if we found one
            rq_with_dir = f"{rq} {results_dir}" if results_dir else rq
            if results_dir:
                logger.info("assess: Reading results with query '%s' from directory %s", rq, results_dir)
            else:
                logger.info("assess: Reading results with query '%s' (no specific directory)", rq)
            results_text = await asyncio.wait_for(reader.ainvoke(rq_with_dir), timeout=300)
            logger.info("✅ assess: Results reading completed successfully")
        except Exception as e:
            logger.error("❌ assess: Reading results failed: %s", e)
            results_text = f"❌ Reading results failed: {e}"

        return {**state, "assessment": assess_out, "results_text": results_text, "results_dir": results_dir}

    async def summarize(state: State):
        logger.info("summarize: Starting LLM-based assessment summarization")

        # Summarize assessment results
        try:
            llm = await builder.get_llm(config.reasoning_llm_name, wrapper_type=LLMFrameworkEnum.LANGCHAIN)
            logger.info("✅ summarize: LLM acquired successfully")
        except Exception as e:
            logger.error("❌ summarize: Could not acquire LLM: %s", e)
            return {**state, "assessment_summary": f"❌ Could not acquire LLM: {e}"}
        results = _net_truncate(state.get("results_text", ""), 100_000)
        question = state.get("input", "")
        logger.info("summarize: Processing %d chars of assessment data", len(results))

        chain = summary_prompt | llm | StrOutputParser()
        rendered = ""
        if config.include_prompts_in_output:
            try:
                try:
                    rendered = summary_prompt.format(question=question, results=results)
                except AttributeError:
                    rendered = summary_prompt.format_prompt(question=question, results=results).to_string()
            except Exception:
                rendered = "(failed to render prompt)"
        try:
            logger.info("summarize: Invoking LLM for assessment summary")
            summary = await asyncio.wait_for(chain.ainvoke({"question": question, "results": results}), timeout=90)
            logger.info("✅ summarize: LLM summary completed successfully")
        except Exception as e:
            logger.error("❌ summarize: LLM summary failed: %s", e)
            summary = f"❌ Summary unavailable: {e}"
        return {**state, "assessment_summary": summary, "summary_prompt": rendered}

    async def generate(state: State):
        logger.info("generate: Starting BCM command generation")

        # Build context and ask BCM RAG/LLM for commands
        try:
            llm = await builder.get_llm(config.reasoning_llm_name, wrapper_type=LLMFrameworkEnum.LANGCHAIN)
            logger.info("✅ generate: LLM acquired successfully")
        except Exception as e:
            logger.error("❌ generate: Could not acquire LLM: %s", e)
            return {**state, "bcm_commands": f"❌ Could not acquire LLM: {e}"}

        # Desired config from YAML
        logger.info("generate: Extracting desired configuration")
        desired = ""
        try:
            extractor = builder.get_function("network_config_extractor")
            desired = await asyncio.wait_for(extractor.ainvoke("extract network configuration"), timeout=60)
            logger.info("✅ generate: Desired config extracted successfully")
        except Exception as e:
            logger.warning("generate: Desired config extraction failed: %s", e)
            desired = f"(desired config unavailable: {e})"

        # Optional BCM docs RAG (kept simple; returns plain text guidance)
        logger.info("generate: Querying BCM documentation RAG")
        bcm_docs = ""
        try:
            bcm_rag = builder.get_function("bcm_documentation_rag")
            bcm_docs = await asyncio.wait_for(
                bcm_rag.ainvoke("Networking reset/remediation commands (cmsh) cheat sheet."), timeout=60)
            logger.info("✅ generate: BCM docs RAG completed successfully")
        except Exception as e:
            logger.warning("generate: BCM docs RAG failed: %s", e)
            bcm_docs = ""

        allowed_nodes = state.get("requested_nodes", [])
        allowed_nodes_str = ", ".join(allowed_nodes) if allowed_nodes else "(not specified)"
        logger.info("generate: Target nodes: %s", allowed_nodes_str)

        context = ("USER_REQUEST:\n" + (state.get("input", "") or "") + "\n\n" + "ACTION_TYPE:\n" +
                   (state.get("action_type", "") or "") + "\n\n" + "ALLOWED_NODES:\n" + allowed_nodes_str + "\n\n" +
                   "ASSESSMENT:\n" + (state.get("assessment", "") or "") + "\n\n" + "RESULTS (parsed):\n" +
                   (state.get("results_text", "") or "") + "\n\n" + "DESIRED CONFIG (YAML facts):\n" + (desired or "") +
                   "\n\n" + "BCM DOCS (RAG):\n" + (bcm_docs or ""))

        chain = commands_prompt | llm | StrOutputParser()
        try:
            logger.info("generate: Invoking LLM for command generation")
            llm_out = await asyncio.wait_for(chain.ainvoke({"context": context}), timeout=90)
            logger.info("✅ generate: LLM command generation completed")
        except Exception as e:
            logger.error("❌ generate: LLM command generation failed: %s", e)
            llm_out = f"[Error generating commands: {e}]"

        # Extract rationale
        m = re.search(r"Rationale:\s*(.+?)(?:\n\s*Commands:|\Z)", llm_out, flags=re.S | re.I)
        rationale = m.group(1).strip() if m else ""
        logger.info("generate: Extracted rationale: %s chars", len(rationale))

        # Extract and filter commands
        extracted = _net_extract_cmsh_commands(llm_out)
        filtered = _net_filter_placeholders(extracted)
        logger.info("generate: Extracted %d commands, filtered to %d valid commands", len(extracted), len(filtered))

        if state.get("action_type") == "reset_network" and allowed_nodes:
            # Soft coverage nudge: warn if no commands for some requested nodes
            present = set()
            for c in filtered:
                match = re.search(r'device use\s+(\S+)', c)
                if match:
                    present.add(match.group(1))
            missing = [n for n in allowed_nodes if n not in present]
            if missing:
                logger.warning("generate: Missing commands for nodes: %s", missing)
                rationale += ("\n- Warning: No commands generated for requested nodes: " + ", ".join(missing))
            else:
                logger.info("✅ generate: All requested nodes covered in generated commands")

        return {
            **state,
            "bcm_commands": "\n".join(filtered) if filtered else "❌ No valid cmsh commands extracted.",
            "bcm_rationale": rationale,
            "llm_cmds_raw": llm_out
        }

    async def execute(state: State):
        logger.info("execute: Starting command execution phase")

        try:
            executor = builder.get_function(config.executor_fn)
            logger.info("✅ execute: Executor function '%s' acquired successfully", config.executor_fn)
        except Exception as e:
            logger.warning("execute: No executor configured, skipping execution: %s", e)
            return {**state, "execution_result": "No executor configured; skipping execution."}

        cmds = state.get("bcm_commands", "") or ""
        cmd_lines = cmds.splitlines() if cmds.strip() else []
        logger.info("execute: Validating %d command lines", len(cmd_lines))

        if not cmds.strip() or not all(line.strip().startswith('cmsh -c "') for line in cmd_lines):
            logger.warning("❌ execute: No valid executable cmsh commands found")
            return {**state, "execution_result": "❌ No executable cmsh commands. Skipping execution."}

        logger.info("execute: Invoking executor with %d commands (timeout: 600s)", len(cmd_lines))
        try:
            out = await asyncio.wait_for(executor.ainvoke(cmds), timeout=600)
            logger.info("✅ execute: Command execution completed successfully")
        except Exception as e:
            logger.error("❌ execute: Command execution failed: %s", e)
            out = f"❌ Execution error: {e}"
        return {**state, "execution_result": out}

    async def synthesize(state: State):
        sections = ["# Network Orchestration\n"]
        if state.get("analysis"):
            sections.append("## Reasoning and Decision\n" + state.get("analysis", "") + "\n")
        if config.include_llm_rationale and state.get("bcm_rationale"):
            sections.append("## Command Rationale\n" + state.get("bcm_rationale", "") + "\n")
        if state.get("bcm_commands"):
            sections.append("## Generated BCM Commands\n" + state.get("bcm_commands", "") + "\n")
        if state.get("execution_result"):
            sections.append("## Execution Result\n" + state.get("execution_result", "") + "\n")
        if config.include_prompts_in_output and state.get("llm_cmds_raw"):
            sections.append("## LLM Prompts/Responses (Debug)\n" + _net_truncate(state.get("llm_cmds_raw", ""), 3000) +
                            "\n")
        return {**state, "final_output": "\n".join(sections)}

    async def synthesize_diag(state: State):
        sections = ["# Network Orchestration (Diagnostics Only)\n"]
        if state.get("analysis"):
            sections.append("## Reasoning and Decision\n" + state.get("analysis", "") + "\n")
        if state.get("assessment_summary"):
            sections.append("## Assessment Summary\n" + state.get("assessment_summary", "") + "\n")
        if config.include_prompts_in_output and state.get("summary_prompt"):
            sections.append("## LLM Prompts/Responses (Debug)\n" +
                            _net_truncate(state.get("summary_prompt", ""), 1200) + "\n")
        return {**state, "final_output": "\n".join(sections)}

    def route_after_analyze(state: State):
        return "assess"

    def route_after_assess(state: State):
        act = state.get("action_type", "diagnostics_only")
        return "generate" if act in ("generate_network_commands", "reset_network") else "summarize"

    # Build graph
    graph = StateGraph(State)
    graph.add_node("analyze", analyze)
    graph.add_node("assess", assess)
    graph.add_node("summarize", summarize)
    graph.add_node("generate", generate)
    graph.add_node("execute", execute)
    graph.add_node("synthesize", synthesize)
    graph.add_node("synthesize_diag", synthesize_diag)

    graph.set_entry_point("analyze")
    graph.add_conditional_edges("analyze", route_after_analyze, {"assess": "assess"})
    graph.add_conditional_edges("assess", route_after_assess, {"generate": "generate", "summarize": "summarize"})
    graph.add_edge("generate", "execute")
    graph.add_edge("execute", "synthesize")
    graph.add_edge("summarize", "synthesize_diag")
    graph.add_edge("synthesize", END)
    graph.add_edge("synthesize_diag", END)

    app = graph.compile()

    async def _run(input_text: str) -> str:
        state: State = {"input": input_text}
        result = await app.ainvoke(state)
        return result.get("final_output", "❌ Network orchestrator produced no output")

    yield FunctionInfo.from_fn(
        _run,
        description=("Analyze cluster networking, decide diagnostics vs reset, generate BCM cmsh commands, "
                     "execute with approval, and return reasoning/results."))


print("✅ LangGraph Network Orchestrator registered successfully")
