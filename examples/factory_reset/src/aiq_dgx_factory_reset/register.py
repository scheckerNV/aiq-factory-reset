"""
DGX Factory Reset Agent Registration

This module registers all functions and agents for the DGX factory reset system.
"""

import logging
import os
import tempfile
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
    docs_path: str = Field(default="examples/factory_reset/src/aiq_dgx_factory_reset/docs/bcm_admin_manual/",
                           description="Path to BCM documentation directory")
    offline_mode: bool = Field(default=True, description="Run in offline mode for testing")


@register_function(config_type=BCMDocumentationRAGConfig)
async def bcm_documentation_rag(config: BCMDocumentationRAGConfig, builder: Builder):
    """
    Search the BCM admin manual for relevant information using RAG
    """

    async def _search_bcm_docs(query: str) -> str:
        """Search BCM documentation and return relevant information"""
        docs_path = config.docs_path

        if not os.path.exists(docs_path):
            return f"❌ BCM documentation not found at {docs_path}. Please check the path."

        try:
            # Import langchain dependencies only when function is called
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            from langchain_community.document_loaders import DirectoryLoader
            from langchain_community.document_loaders import TextLoader
            from langchain_community.vectorstores import Chroma
            from langchain_huggingface import HuggingFaceEmbeddings

            logger.info(f"Searching BCM docs for: {query}")

            # Load all markdown documentation files
            loader = DirectoryLoader(docs_path, glob="*.md", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
            documents = loader.load()

            if not documents:
                return f"❌ No BCM documentation files found in {docs_path}"

            logger.info(f"Loaded {len(documents)} BCM documentation files")

            # Split documents into chunks optimized for RAG
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,  # Optimal size for embeddings
                chunk_overlap=200,  # Prevent losing context at boundaries
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""]  # Split on logical boundaries
            )
            splits = text_splitter.split_documents(documents)

            logger.info(f"Split into {len(splits)} chunks for embedding")

            # Create embeddings using lightweight model
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2",
                                               model_kwargs={'device': 'cpu'},
                                               show_progress=True)

            # Create vector store in temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                vectorstore = Chroma.from_documents(splits, embeddings, persist_directory=temp_dir)

                # Search for relevant documentation chunks
                relevant_docs = vectorstore.similarity_search(query, k=6)

                if not relevant_docs:
                    return (f"❓ No relevant BCM documentation found for: {query}\n\n"
                            "Try rephrasing your question or being more specific about BCM operations.")

                # Format results with rich context
                result = "📖 **BCM Expert Documentation Search**\n"
                result += f"**Query:** {query}\n"
                result += f"**Found {len(relevant_docs)} relevant sections:**\n\n"

                for i, doc in enumerate(relevant_docs, 1):
                    content = doc.page_content.strip()
                    source_file = Path(doc.metadata.get('source', 'Unknown')).name

                    # Truncate very long content but preserve important details
                    if len(content) > 900:
                        # Try to find a good breaking point
                        truncate_point = content.rfind('.', 0, 900)
                        if truncate_point == -1:
                            truncate_point = 900
                        content = content[:truncate_point + 1] + "\n\n[...content continues in full manual...]"

                    result += f"**📋 Section {i}** (from {source_file}):\n\n"
                    result += f"{content}\n\n"
                    result += "---\n\n"

                # Add expert guidance
                result += "💡 **Expert Guidance:**\n"
                result += "- Use this information to understand BCM procedures and commands\n"
                result += "- Cross-reference multiple sections for complete procedures\n"
                result += "- Consider node states and cluster topology when implementing\n"
                result += "- Always verify commands in test environment first\n\n"

                result += ("🔧 **Next Steps:** Use the `bcm_power_control` or `bcm_enrollment` tools "
                           "to execute specific operations.")

                return result

        except Exception as e:
            logger.error(f"Error in BCM documentation search: {str(e)}")
            return (f"❌ Error searching BCM documentation: {str(e)}\n\n"
                    "Please check that all dependencies are installed and the documentation path is correct.")

    yield FunctionInfo.from_fn(_search_bcm_docs,
                               description="Search the BCM admin manual for relevant information using RAG")


print("✅ DGX Factory Reset BCM RAG function registered successfully")
