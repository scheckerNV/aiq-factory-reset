"""
BCM Expert Tools for DGX Factory Reset
Includes RAG-powered documentation search and BCM operations
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
# RAG Documentation Tool
# ========================


class BCMDocumentationRAGConfig(FunctionBaseConfig, name="bcm_documentation_rag"):
    query: str = Field(description="Question about BCM operations, procedures, commands, or troubleshooting")
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
            from langchain_community.embeddings import HuggingFaceEmbeddings
            from langchain_community.vectorstores import Chroma

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
                    return f"❓ No relevant BCM documentation found for: {query}\n\nTry rephrasing your question or being more specific about BCM operations."

                # Format results with rich context
                result = f"📖 **BCM Expert Documentation Search**\n"
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

                result += "🔧 **Next Steps:** Use the `bcm_power_control` or `bcm_enrollment` tools to execute specific operations."

                return result

        except Exception as e:
            logger.error(f"Error in BCM documentation search: {str(e)}")
            return f"❌ Error searching BCM documentation: {str(e)}\n\nPlease check that all dependencies are installed and the documentation path is correct."

    yield FunctionInfo.from_fn(_search_bcm_docs,
                               description="Search the BCM admin manual for relevant information using RAG")


# ========================
# BCM Power Control Tool
# ========================


class BCMPowerControlConfig(FunctionBaseConfig, name="bcm_power_control"):
    command: str = Field(description="Power command: 'status', 'on', 'off', 'cycle', or 'soft-shutdown'")
    node_list: list[str] = Field(default=[], description="List of node names (empty for all nodes)")
    bcm_host: str = Field(default="bcm.cluster.local", description="BCM hostname or IP")
    username: str = Field(default="admin", description="BCM username")
    offline_mode: bool = Field(default=True, description="Run in simulation mode for testing")


@register_function(config_type=BCMPowerControlConfig)
async def bcm_power_control(config: BCMPowerControlConfig, builder: Builder):
    """
    Control DGX node power through BCM
    """

    async def _bcm_power_control(command: str, node_list: list[str] | None = None) -> str:
        """Execute BCM power control commands"""

        if config.offline_mode:
            # Simulation mode for testing
            nodes = node_list or ["dgx-01", "dgx-02", "dgx-03"]
            result = f"🔌 **BCM Power Control Simulation**\n"
            result += f"**Command:** {command}\n"
            result += f"**Target Nodes:** {', '.join(nodes)}\n"
            result += f"**BCM Host:** {config.bcm_host}\n\n"

            if command == "status":
                result += "**Power Status:**\n"
                for node in nodes:
                    status = "ON" if hash(node) % 2 else "OFF"
                    result += f"- {node}: {status}\n"
            elif command in ["on", "off", "cycle", "soft-shutdown"]:
                result += f"**Executing {command.upper()} command...**\n"
                for node in nodes:
                    result += f"✅ {node}: Command {command} executed successfully\n"
            else:
                result += f"❌ Unknown command: {command}\n"
                result += "Valid commands: status, on, off, cycle, soft-shutdown"

            result += f"\n💡 **Note:** Running in simulation mode. No actual power operations performed."
            return result

        # Real implementation would go here
        return f"🚫 Real BCM operations not implemented yet. Use offline_mode: true for testing."

    yield FunctionInfo.from_fn(_bcm_power_control, description="Control DGX node power through BCM")


# ========================
# BCM Node Enrollment Tool
# ========================


class BCMEnrollmentConfig(FunctionBaseConfig, name="bcm_enrollment"):
    action: str = Field(description="Enrollment action: 'enroll', 'unenroll', 'status', or 'reset-enrollment'")
    node_list: list[str] = Field(default=[], description="List of node names to enroll")
    bcm_host: str = Field(default="bcm.cluster.local", description="BCM hostname or IP")
    username: str = Field(default="admin", description="BCM username")
    offline_mode: bool = Field(default=True, description="Run in simulation mode for testing")


@register_function(config_type=BCMEnrollmentConfig)
async def bcm_enrollment(config: BCMEnrollmentConfig, builder: Builder):
    """
    Manage DGX node enrollment in BCM
    """

    async def _bcm_enrollment(action: str, node_list: list[str] | None = None) -> str:
        """Execute BCM enrollment operations"""

        if config.offline_mode:
            # Simulation mode for testing
            nodes = node_list or ["dgx-01", "dgx-02", "dgx-03"]
            result = f"📝 **BCM Node Enrollment Simulation**\n"
            result += f"**Action:** {action}\n"
            result += f"**Target Nodes:** {', '.join(nodes)}\n"
            result += f"**BCM Host:** {config.bcm_host}\n\n"

            if action == "status":
                result += "**Enrollment Status:**\n"
                for node in nodes:
                    status = "ENROLLED" if hash(node) % 3 != 0 else "NOT_ENROLLED"
                    result += f"- {node}: {status}\n"
            elif action == "enroll":
                result += "**Enrolling nodes...**\n"
                for node in nodes:
                    result += f"✅ {node}: Successfully enrolled in BCM\n"
            elif action == "unenroll":
                result += "**Unenrolling nodes...**\n"
                for node in nodes:
                    result += f"✅ {node}: Successfully unenrolled from BCM\n"
            elif action == "reset-enrollment":
                result += "**Resetting enrollment...**\n"
                for node in nodes:
                    result += f"✅ {node}: Enrollment reset completed\n"
            else:
                result += f"❌ Unknown action: {action}\n"
                result += "Valid actions: enroll, unenroll, status, reset-enrollment"

            result += f"\n💡 **Note:** Running in simulation mode. No actual enrollment operations performed."
            return result

        # Real implementation would go here
        return f"🚫 Real BCM enrollment operations not implemented yet. Use offline_mode: true for testing."

    yield FunctionInfo.from_fn(_bcm_enrollment, description="Manage DGX node enrollment in BCM")
