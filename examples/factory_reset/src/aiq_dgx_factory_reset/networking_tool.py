# examples/factory_reset/src/aiq_dgx_factory_reset/networking_tool.py

import logging
import os
from pathlib import Path

from pydantic import Field

from aiq.builder.builder import Builder
from aiq.builder.function_info import FunctionInfo
from aiq.cli.register_workflow import register_function
from aiq.data_models.function import FunctionBaseConfig

logger = logging.getLogger(__name__)


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
    Search networking documentation using accurate RAG retrieval
    """

    async def _search_networking_docs(query: str) -> str:
        """Search networking documentation with high-accuracy retrieval"""
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

            # Set up API keys
            nvidia_api_key = config.nvidia_api_key or os.getenv("NVIDIA_API_KEY")

            if not nvidia_api_key:
                return ("❌ NVIDIA API key not provided. Set NVIDIA_API_KEY "
                        "environment variable or provide in config.")

            os.environ["NVIDIA_API_KEY"] = nvidia_api_key

            # Configure LlamaIndex with NVIDIA models for accuracy
            Settings.llm = NVIDIA(model="meta/llama-3.3-70b-instruct")
            Settings.embed_model = NVIDIAEmbedding(model="nvidia/llama-3.2-nv-embedqa-1b-v2", truncate="END")

            logger.info("🔧 Processing networking documentation from %s", docs_path)

            # Check for existing index
            docstore_path = os.path.join(persist_dir, "docstore.json")
            if os.path.exists(docstore_path):
                logger.info("📂 Loading existing networking documentation index...")
                storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
                index = load_index_from_storage(storage_context)
            else:
                logger.info("🔨 Creating new networking documentation index...")
                os.makedirs(persist_dir, exist_ok=True)

                documents = []
                docs_path_obj = Path(docs_path)

                # Process YAML files (your primary docs)
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

                # Process markdown and text files
                for pattern, file_type in [("*.md", "markdown"), ("*.txt", "text")]:
                    files = list(docs_path_obj.glob(pattern))
                    if files:
                        logger.info("📄 Found %d %s files...", len(files), file_type)
                        for file_path in files:
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                documents.append(
                                    Document(text=content,
                                             metadata={
                                                 "source": str(file_path),
                                                 "file_name": file_path.name,
                                                 "file_type": file_type
                                             }))
                                logger.info("✅ Processed %s", file_path.name)
                            except Exception as e:
                                logger.warning("⚠️ Failed to load %s: %s", file_path, e)

                if not documents:
                    return f"❌ No networking documentation files found in {docs_path}"

                logger.info("🚀 Creating index from %d documents...", len(documents))
                index = VectorStoreIndex.from_documents(documents)
                index.storage_context.persist(persist_dir=persist_dir)
                logger.info("💾 Index created and persisted successfully")

            # Create query engine optimized for accuracy
            query_engine = index.as_query_engine(similarity_top_k=config.similarity_top_k,
                                                 response_mode=config.response_mode,
                                                 verbose=True)

            logger.info("🔍 Executing networking query: %s", query)
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
                    score = getattr(node, 'score', 'N/A')
                    result += f"{i}. {file_name} (Score: {score:.3f})\n"

            result += "\n⚠️  **Note:** Please verify networking configuration in your specific environment before implementation."

            return result

        except ImportError as e:
            logger.error("❌ Missing LlamaIndex dependencies: %s", str(e))
            return (f"❌ Missing LlamaIndex dependencies: {str(e)}\n\n"
                    f"Please install with: uv pip install -e '.[llama-index]'")
        except Exception as e:
            logger.error("❌ Error in networking documentation search: %s", str(e))
            return (f"❌ Error in {config.expert_type} analysis: {str(e)}\n\n"
                    f"Please check your API keys and network connection.")

    yield FunctionInfo.from_fn(_search_networking_docs,
                               description=("STEP 1: Analyze networking configuration requirements from documentation. "
                                            "Use this FIRST to understand network topology and requirements."))


print("✅ Networking Expert RAG tool registered successfully")
