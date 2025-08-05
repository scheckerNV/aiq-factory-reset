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
                if pdf_files:
                    logger.info("Found %d PDF files, processing with LlamaParse...", len(pdf_files))
                    # new code
                    # In your register.py, around line 100, replace the PDF processing with:
                    parser = LlamaParse(verbose=True)
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
                            logger.warning("Failed to parse %s: %s", pdf_file, e)
                            # Add fallback here if needed

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
            from llama_parse import LlamaParse

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

                # Process PDF files with LlamaParse if LlamaCloud API key is available
                if llama_api_key:
                    os.environ["LLAMA_CLOUD_API_KEY"] = llama_api_key
                    pdf_files = list(docs_path_obj.glob("*.pdf"))
                    if pdf_files:
                        logger.info("Found %d PDF files, processing with LlamaParse...", len(pdf_files))
                        parser = LlamaParse(verbose=True)
                        for pdf_file in pdf_files:
                            try:
                                pdf_docs = parser.load_data(str(pdf_file))
                                for doc in pdf_docs:
                                    doc.metadata["source"] = str(pdf_file)
                                    doc.metadata["file_name"] = pdf_file.name
                                documents.extend(pdf_docs)
                                logger.info("Successfully processed %s", pdf_file.name)
                            except Exception as e:
                                logger.warning("Failed to parse %s: %s", pdf_file, e)

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


print("✅ BCM Documentation RAG function registered successfully")
print("✅ Generic Documentation RAG function registered successfully")
