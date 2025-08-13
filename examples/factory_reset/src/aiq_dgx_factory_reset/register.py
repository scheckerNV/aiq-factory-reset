"""
BCM Documentation RAG with LlamaIndex

This module provides accurate retrieval of BCM (Bright Cluster Manager) documentation
using LlamaIndex, LlamaParse, and NVIDIA embeddings for high-quality RAG responses.
"""

import logging
import os
from pathlib import Path

from pydantic import Field

from aiq.builder.builder import Builder
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
                # pdf_files = list(docs_path_obj.glob("*.pdf"))
                # if pdf_files and llama_api_key:
                #     logger.info("Found %d PDF files, processing with LlamaParse...", len(pdf_files))

                #     for pdf_file in pdf_files:
                #         try:
                #             logger.info("Processing %s individually...", pdf_file.name)

                #             # Create a fresh parser instance for each file
                #             file_parser = LlamaParse(verbose=True)
                #             pdf_docs = file_parser.load_data(str(pdf_file))

                #             for doc in pdf_docs:
                #                 doc.metadata["source"] = str(pdf_file)
                #                 doc.metadata["file_name"] = pdf_file.name

                #             documents.extend(pdf_docs)
                #             logger.info("Successfully processed %s (%d documents)", pdf_file.name, len(pdf_docs))

                #             # Clean up
                #             del file_parser

                #         except Exception as e:
                #             logger.warning("Failed to parse %s, skipping PDF processing: %s", pdf_file, e)
                #             logger.info("Continuing with other document types...")
                #             continue
                # elif pdf_files and not llama_api_key:
                #     logger.info("Found %d PDF files but no LlamaCloud API key provided, skipping PDF processing",
                #                 len(pdf_files))

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
# Generic Documentation RAG Tool
# ========================


class DocumentationRAGConfig(FunctionBaseConfig, name="documentation_rag"):
    docs_path: str = Field(description="Path to documentation directory")
    persist_dir: str = Field(description="Directory to persist the vector index")
    similarity_top_k: int = Field(default=5, description="Number of top similar chunks to retrieve")
    response_mode: str = Field(default="tree_summarize", description="Response synthesis mode")
    expert_type: str = Field(default="Documentation", description="Type of expert (e.g., 'Networking', 'BCM')")

    llama_cloud_api_key: str = Field(default="", description="LlamaCloud API key (or set LLAMA_CLOUD_API_KEY env var)")
    nvidia_api_key: str = Field(default="", description="NVIDIA API key (or set NVIDIA_API_KEY env var)")


@register_function(config_type=DocumentationRAGConfig)
async def documentation_rag(config: DocumentationRAGConfig, _builder: Builder):
    """
    Search documentation using accurate RAG retrieval (supports PDF, Markdown, YAML, and text files)
    """

    async def _search_docs(query: str) -> str:
        """Search documentation with high-accuracy retrieval"""
        docs_path = config.docs_path
        persist_dir = config.persist_dir

        if not os.path.exists(docs_path):
            return f"❌ Documentation not found at {docs_path}"

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

            os.environ["NVIDIA_API_KEY"] = nvidia_api_key

            # Configure LlamaIndex with NVIDIA models for accuracy
            Settings.llm = NVIDIA(model="meta/llama-3.3-70b-instruct")
            Settings.embed_model = NVIDIAEmbedding(model="nvidia/llama-3.2-nv-embedqa-1b-v2", truncate="END")

            logger.info("Processing documentation from %s", docs_path)

            # Check for existing index
            docstore_path = os.path.join(persist_dir, "docstore.json")
            if os.path.exists(docstore_path):
                logger.info("Loading existing documentation index...")
                storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
                index = load_index_from_storage(storage_context)
            else:
                logger.info("Creating new documentation index...")
                os.makedirs(persist_dir, exist_ok=True)

                documents = []
                docs_path_obj = Path(docs_path)

                # # Process PDF files with LlamaParse if LlamaCloud API key is available
                # if llama_api_key:
                #     os.environ["LLAMA_CLOUD_API_KEY"] = llama_api_key
                #     pdf_files = list(docs_path_obj.glob("*.pdf"))
                #     if pdf_files:
                #         logger.info("Found %d PDF files, processing with LlamaParse...", len(pdf_files))
                #         parser = LlamaParse(verbose=True)
                #         for pdf_file in pdf_files:
                #             try:
                #                 pdf_docs = parser.load_data(str(pdf_file))
                #                 for doc in pdf_docs:
                #                     doc.metadata["source"] = str(pdf_file)
                #                     doc.metadata["file_name"] = pdf_file.name
                #                 documents.extend(pdf_docs)
                #                 logger.info("Successfully processed %s", pdf_file.name)
                #             except Exception as e:
                #                 logger.warning("Failed to parse %s: %s", pdf_file, e)

                pdf_files = list(docs_path_obj.glob("*.pdf"))
                # if pdf_files:
                #     logger.info("Found %d PDF files, processing with LlamaParse...", len(pdf_files))
                #     # new code
                #     parser = LlamaParse(verbose=True)
                #     for pdf_file in pdf_files:
                #         try:
                #             logger.info("Processing %s individually...", pdf_file.name)

                #             # Create a fresh parser instance for each file
                #             file_parser = LlamaParse(verbose=True)
                #             pdf_docs = file_parser.load_data(str(pdf_file))

                #             for doc in pdf_docs:
                #                 doc.metadata["source"] = str(pdf_file)
                #                 doc.metadata["file_name"] = pdf_file.name

                #             documents.extend(pdf_docs)
                #             logger.info("Successfully processed %s (%d documents)", pdf_file.name, len(pdf_docs))

                #             # Clean up
                #             del file_parser

                #         except Exception as e:
                #             logger.warning("Failed to parse %s: %s", pdf_file, e)
                #             # Add fallback here if needed
                # Process YAML files
                yaml_files = list(docs_path_obj.glob("*.yaml")) + list(docs_path_obj.glob("*.yml"))
                if yaml_files:
                    logger.info("Found %d YAML files...", len(yaml_files))
                    for yaml_file in yaml_files:
                        try:
                            with open(yaml_file, 'r', encoding='utf-8') as f:
                                content = f.read()

                            # Also parse as YAML to extract structured info for metadata
                            try:
                                yaml_data = yaml.safe_load(content)
                                metadata = {"source": str(yaml_file), "file_name": yaml_file.name, "file_type": "yaml"}
                                # Add some structured metadata if available
                                if isinstance(yaml_data, dict):
                                    if "metadata" in yaml_data:
                                        metadata.update(yaml_data["metadata"])
                                    if "cluster" in yaml_data:
                                        metadata["cluster_name"] = yaml_data.get("cluster", {}).get("name", "unknown")
                            except Exception:
                                metadata = {"source": str(yaml_file), "file_name": yaml_file.name, "file_type": "yaml"}

                            documents.append(Document(text=content, metadata=metadata))
                            logger.info("Processed %s", yaml_file.name)
                        except Exception as e:
                            logger.warning("Failed to load %s: %s", yaml_file, e)

                # Process markdown files
                md_files = list(docs_path_obj.glob("*.md"))
                if md_files:
                    logger.info("Found %d markdown files...", len(md_files))
                    for md_file in md_files:
                        try:
                            with open(md_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                            documents.append(
                                Document(text=content,
                                         metadata={
                                             "source": str(md_file), "file_name": md_file.name, "file_type": "markdown"
                                         }))
                            logger.info("Processed %s", md_file.name)
                        except Exception as e:
                            logger.warning("Failed to load %s: %s", md_file, e)

                # Process text files
                txt_files = list(docs_path_obj.glob("*.txt"))
                if txt_files:
                    logger.info("Found %d text files...", len(txt_files))
                    for txt_file in txt_files:
                        try:
                            with open(txt_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                            documents.append(
                                Document(text=content,
                                         metadata={
                                             "source": str(txt_file), "file_name": txt_file.name, "file_type": "text"
                                         }))
                            logger.info("Processed %s", txt_file.name)
                        except Exception as e:
                            logger.warning("Failed to load %s: %s", txt_file, e)

                if not documents:
                    return f"❌ No documentation files found in {docs_path}"

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
            result = f"🤖 **{config.expert_type} Documentation Expert**\n\n"
            result += f"**Query:** {query}\n\n"
            result += f"**Answer:**\n{str(response)}\n\n"

            # Add source information if available
            if hasattr(response, 'source_nodes') and response.source_nodes:
                result += "**Sources:**\n"
                for i, node in enumerate(response.source_nodes[:3], 1):
                    file_name = node.metadata.get('file_name', 'Unknown')
                    result += f"{i}. {file_name} (Score: {node.score:.3f})\n"

            return result

        except Exception as e:
            logger.error("Error in documentation search: %s", str(e))
            return (f"❌ Error in {config.expert_type} analysis: {str(e)}\n\n"
                    f"Please check your API keys and network connection.")

    yield FunctionInfo.from_fn(_search_docs,
                               description=(f"STEP 1: Analyze {config.expert_type} desired state configuration "
                                            f"and requirements. Call this FIRST before any BCM operations."))


print("✅ Generic Documentation RAG function registered successfully")

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
            result = "🤖 **Networking Documentation Expert**\n\n"
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

            # Copy script to cluster
            scp_cmd = ["scp", script_path, f"{config.cluster_user}@{config.cluster_host}:/tmp/network_assessment.sh"]

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

            # Clean up local script
            os.unlink(script_path)

            if ssh_process.returncode == 0:
                return f"""✅ Network assessment completed successfully!

📋 Assessment Output:
{stdout.decode('utf-8')}

📁 Results saved on cluster in timestamped directory.
Use the network_results_reader tool to analyze the results.

🔍 Next steps:
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
            else:
                files_to_read = ["00_SUMMARY.txt"]

            results = []

            # First, find the LATEST assessment directory
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
                logger.info(f"Reading from latest assessment directory: {latest_dir}")

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
# LangGraph Orchestrator
# ========================


class NetworkWorkflowOrchestratorConfig(FunctionBaseConfig, name="network_workflow_orchestrator"):
    max_retries: int = Field(default=1, description="Maximum retry attempts")  # Reduced from 3 to 1
    quality_threshold: float = Field(default=0.3, description="Minimum quality score for commands")  # Lowered threshold


@register_function(config_type=NetworkWorkflowOrchestratorConfig)
async def network_workflow_orchestrator(config: NetworkWorkflowOrchestratorConfig, builder: Builder):
    """LangGraph orchestrator that uses your existing tools"""

    import re
    from typing import TypedDict

    from langgraph.graph import END
    from langgraph.graph import StateGraph

    def extract_user_input(inp: str | dict) -> str:
        """Extract raw user question from Reasoning Agent plan or pass-through dict."""
        if isinstance(inp, dict):
            if "input_text" in inp:
                return str(inp["input_text"]).strip()
            for v in inp.values():
                if isinstance(v, str) and v.strip():
                    return v.strip()
            return str(inp)
        if isinstance(inp, str):
            m = re.search(r'ORIGINAL REQUEST:\s*\{.*?"content":\s*"([^"]+)"', inp, re.S)
            return m.group(1).strip() if m else inp.strip()
        return str(inp).strip()

    # NOTE:
    # Do NOT fetch tools at build time. The AIQ builder may construct this
    # function before its dependencies, causing lookup failures.
    # Instead, fetch tool handles lazily inside each node when executed.

    class WorkflowState(TypedDict):
        input: str
        assessment_complete: bool
        commands_generated: bool
        quality_score: float
        retry_count: int
        final_output: str

    async def assessment_node(state: WorkflowState):
        """Use your existing assessment tool"""
        logger.info("LangGraph: running assessment_node")
        assessment_tool = builder.get_function("network_assessment_tool")
        task = extract_user_input(state["input"])
        result = await assessment_tool.ainvoke(task)
        return {**state, "assessment_complete": True, "assessment_data": result}

    async def analysis_node(state: WorkflowState):
        """Use your existing results reader"""
        results_reader = builder.get_function("network_results_reader")
        # Trigger a summary read of latest assessment results; input string is not used meaningfully
        result = await results_reader.ainvoke("")
        return {**state, "analysis_complete": True, "analysis_data": result}

    async def research_node(state: WorkflowState):
        """Use your existing networking expert tool"""
        # Ask for concrete, actionable guidance tailored to producing cmsh commands
        task = extract_user_input(state["input"])
        query = ("DGX SuperPOD networking reset. "
                 f"Task: {task}. "
                 "Return concise, actionable steps that directly lead to BCM cmsh commands. "
                 "Avoid high-level prose.")
        networking_rag_tool = builder.get_function("networking_expert_rag")
        result = await networking_rag_tool.ainvoke(query)
        return {**state, "research_complete": True, "research_data": result}

    async def command_generation_node(state: WorkflowState):
        """Use your existing BCM RAG tool"""
        bcm_rag_tool = builder.get_function("bcm_documentation_rag")
        task = extract_user_input(state["input"])
        context = ("Assessment Summary:\n" + (state.get('assessment_data', '') or '').strip() + "\n\n" +
                   "Analysis Summary:\n" + (state.get('analysis_data', '') or '').strip() + "\n\n" +
                   "Research Summary:\n" + (state.get('research_data', '') or '').strip() + "\n\n" + "Instruction:\n" +
                   f"Generate the EXACT Bright Cluster Manager commands, using cmsh -c, for task: {task}.\n" +
                   "Revert the cluster networking to a known good state.\n" + "Requirements:\n" +
                   "- Output ONLY commands, one per line, no explanations.\n" +
                   "- Each line MUST start with: cmsh -c \"\n" +
                   "- Include necessary device/network/category contexts and commit where required.\n")
        result = await bcm_rag_tool.ainvoke(context)

        # Improved quality: count lines that start with exact cmsh command prefix
        cmsh_lines = []
        for line in result.splitlines():
            stripped = line.strip()
            if stripped.startswith('cmsh -c "'):
                cmsh_lines.append(stripped)
        quality = min(1.0, len(cmsh_lines) / 5.0)

        return {
            **state,
            "commands_generated": True,
            "commands": result,
            "quality_score": quality,
            "retry_count": state.get("retry_count", 0) + 1
        }

    def should_retry(state: WorkflowState):
        """Conditional logic: retry if quality is low"""
        if (state["quality_score"] < config.quality_threshold and state["retry_count"] < config.max_retries):
            return "generate_commands"  # Fixed: was "retry_commands"
        return "finalize"

    async def finalize_node(state: WorkflowState):
        return {**state, "final_output": state.get("commands", "No commands generated")}

    # Build the LangGraph workflow
    workflow = StateGraph(WorkflowState)

    # Add nodes (using your existing tools)
    workflow.add_node("assess", assessment_node)
    workflow.add_node("analyze", analysis_node)
    workflow.add_node("research", research_node)
    workflow.add_node("generate_commands", command_generation_node)
    workflow.add_node("finalize", finalize_node)

    # Define the flow
    workflow.set_entry_point("assess")
    workflow.add_edge("assess", "analyze")
    workflow.add_edge("analyze", "research")
    workflow.add_edge("research", "generate_commands")

    # Conditional edge with retry loop
    workflow.add_conditional_edges(
        "generate_commands",
        should_retry,
        {
            "generate_commands": "generate_commands",  # Loop back - Fixed mapping
            "finalize": "finalize"  # Exit
        })

    workflow.add_edge("finalize", END)

    app = workflow.compile()

    async def _orchestrated_workflow(input_text: str) -> str:
        """Execute the LangGraph workflow using your existing tools"""
        initial_state: WorkflowState = {
            "input": input_text,
            "assessment_complete": False,
            "commands_generated": False,
            "quality_score": 0.0,
            "retry_count": 0,
            "final_output": ""
        }
        result = await app.ainvoke(initial_state)
        return result.get("final_output", "Workflow failed")

    yield FunctionInfo.from_fn(_orchestrated_workflow,
                               description="LangGraph orchestrator using existing network tools")


print("✅ LangGraph Network Workflow Orchestrator registered successfully")

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
# Deterministic Orchestrator (no LangGraph)
# ========================


class NetworkFactoryResetOrchestratorConfig(FunctionBaseConfig, name="network_factory_reset_orchestrator"):
    """Orchestrate assessment → docs → BCM commands → approval/execution → optional validation."""

    perform_post_validation: bool = Field(default=True, description="Re-run results reader after execution")


@register_function(config_type=NetworkFactoryResetOrchestratorConfig)
async def network_factory_reset_orchestrator(config: NetworkFactoryResetOrchestratorConfig, builder: Builder):
    """Enforce tool call ordering independent of LLM plan."""

    def _extract_cmsh_commands(text: str) -> str:
        # Prefer strict line-based extraction
        lines = []
        for raw in text.splitlines():
            s = raw.strip()
            if s.startswith('cmsh -c "') or s.startswith("cmsh -c '"):
                # remove trailing semicolons if present
                lines.append(s.rstrip(';'))
        if lines:
            return "\n".join(lines)

        # Fallback: split on semicolons if single-line
        parts = [p.strip() for p in text.split(';')]
        lines = [p for p in parts if p.startswith('cmsh -c "') or p.startswith("cmsh -c '")]
        return "\n".join(lines)

    def _filter_placeholders(cmds: list[str]) -> list[str]:
        forbidden_substrings = ["NODE_NAME", "INTERFACE", "HEAD_NODE", "ROUTE_NAME"]
        filtered: list[str] = []
        for c in cmds:
            if any(tok in c for tok in forbidden_substrings):
                continue
            filtered.append(c)
        return filtered

    async def _run(input_text: str) -> str:
        logger.info("Starting network factory reset orchestrator")

        # 1) Assessment first - always run fresh assessment
        logger.info("Running fresh network assessment")
        assess = builder.get_function("network_assessment_tool")
        assess_out = await assess.ainvoke("Run comprehensive network assessment and save results")

        # 2) Read results summary
        reader = builder.get_function("network_results_reader")
        summary_out = await reader.ainvoke("summary")

        # 3) Truncate summary to prevent context overflow
        def truncate_summary(summary: str, max_chars: int = 2000) -> str:
            if len(summary) <= max_chars:
                return summary
            lines = summary.split('\n')
            truncated = ""
            for line in lines:
                if len(truncated + line + '\n') > max_chars:
                    break
                truncated += line + '\n'
            return truncated + "\n[...truncated for context size...]"

        summary_truncated = truncate_summary(summary_out)
        logger.info("Assessment summary truncated to %d characters", len(summary_truncated))

        # 4) Research concrete steps (context-aware but with truncated data)
        net_rag = builder.get_function("networking_expert_rag")
        research_query = ("DGX SuperPOD networking reset guidance. "
                          "Return concise, actionable steps that lead to exact cmsh commands. "
                          "Use the following context from assessment to ground hostnames and networks.\n\n"
                          f"Assessment Summary:\n{summary_truncated}\n\n"
                          f"Original request: {input_text}")

        logger.info("🔍 CONTEXT DEBUG - Research Query Length: %d chars", len(research_query))
        logger.info("🔍 CONTEXT DEBUG - Assessment Summary Preview: %s...", summary_truncated[:200])

        research_out = await net_rag.ainvoke(research_query)
        logger.info("🔍 CONTEXT DEBUG - Research Output Length: %d chars", len(research_out))
        logger.info("🔍 CONTEXT DEBUG - Research Output Preview: %s...", research_out[:300])

        # 5) Extract specific cluster details for BCM context
        def extract_cluster_specifics(summary: str) -> str:
            """Extract key cluster details for BCM commands"""
            lines = summary.split('\n')
            cluster_details = []

            # Look for key information
            for line in lines:
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in [
                        'hostname:', 'node00', 'schecker-testcluster', 'internal', 'external', 'ens3', '10.141',
                        '192.168.200'
                ]):
                    cluster_details.append(line.strip())

            # Add the most recent assessment info
            if cluster_details:
                cluster_details.insert(0, "CURRENT CLUSTER STATE:")
                cluster_details.append("\nKEY POINTS:")
                cluster_details.append("- Cluster: schecker-testcluster")
                cluster_details.append("- Nodes: node001 through node010 (10 nodes)")
                cluster_details.append("- Interface: ens3 (not ib0/ib1/eth0)")
                cluster_details.append("- Internal network: internalnet 10.141.0.0/16 gw 10.141.255.254")
                cluster_details.append("- External network: externalnet 192.168.200.0/24 gw 192.168.200.254")
                cluster_details.append("- NO ibnet/managementnet/computenet/storagenet networks")

            return '\n'.join(cluster_details)

        cluster_context = extract_cluster_specifics(summary_out)  # Use full summary, not truncated
        logger.info("🔍 CONTEXT DEBUG - Cluster Context: %s", cluster_context)

        # 6) Generate exact BCM commands with specific cluster context
        bcm_rag = builder.get_function("bcm_documentation_rag")

        bcm_query = ("Generate the EXACT Bright Cluster Manager commands (cmsh -c) to revert THIS cluster to a known "
                     "good network state.\n"
                     "STRICT REQUIREMENTS:\n"
                     "- Output ONLY commands, one per line, no explanations.\n"
                     "- Each line MUST start with: cmsh -c \"\n"
                     "- Use ONLY the actual cluster details provided below.\n"
                     "- DO NOT use demeter/ibnet/managementnet/computenet/storagenet networks.\n"
                     "- DO NOT use ib0/ib1/eth0 interfaces - use ens3.\n"
                     "- Include device/network/category contexts and commit where required.\n\n"
                     f"CLUSTER SPECIFIC CONTEXT:\n{cluster_context}\n\n"
                     f"DESIRED STATE GUIDANCE:\n{research_out[:500]}")

        logger.info("🔍 CONTEXT DEBUG - BCM Query Length: %d chars", len(bcm_query))
        logger.info("🔍 CONTEXT DEBUG - Cluster Context: %s", cluster_context[:300])

        commands_text = await bcm_rag.ainvoke(bcm_query)
        logger.info("🔍 CONTEXT DEBUG - BCM Commands Generated: %s...", commands_text[:500])
        extracted = _extract_cmsh_commands(commands_text)
        cmds_list = [c for c in extracted.splitlines() if c.strip()]
        cmds_list = _filter_placeholders(cmds_list)

        # Retry once with stricter instruction if we filtered everything out
        if not cmds_list:
            stricter_query = ("Generate safe BCM diagnostic commands for cluster reset.\n"
                              "Output format: cmsh -c \"command\"\n"
                              "If uncertain, default to safe read-ONLY diagnostic cmsh commands.")
            commands_text_2 = await bcm_rag.ainvoke(stricter_query)
            extracted_2 = _extract_cmsh_commands(commands_text_2)
            cmds_list = _filter_placeholders([c for c in extracted_2.splitlines() if c.strip()])

        commands_only = "\n".join(cmds_list) if cmds_list else extracted.strip() or commands_text.strip()

        # 7) Execute with approval
        executor = builder.get_function("bcm_executor")
        exec_out = await executor.ainvoke(commands_only)

        # 8) Optional post validation (read results again)
        post_check = ""
        if config.perform_post_validation:
            try:
                post_check = await reader.ainvoke("summary")
                post_check = truncate_summary(post_check, 1000)  # Truncate post-validation too
            except Exception as e:
                post_check = f"Post-validation read failed: {str(e)}"

        # Assemble final output
        sections = [
            "✅ Network assessment:\n" + assess_out,
            "📊 Assessment summary:\n" + summary_truncated,
            "📚 Research guidance:\n" + research_out,
            "🧰 Generated commands:\n" + commands_only,
            "🚀 Execution result:\n" + exec_out,
        ]
        if post_check:
            sections.append("🔎 Post-execution summary:\n" + post_check)

        logger.info("Network factory reset orchestrator completed")
        return "\n\n".join(sections)

    yield FunctionInfo.from_fn(_run, description="Deterministic network factory-reset orchestrator")


print("✅ Network Factory Reset Orchestrator registered successfully")
