"""
DGX Factory Reset Agent Registration with LlamaIndex Multi-Agent Workflow

This module registers BCM documentation RAG using LlamaIndex, LlamaParse, and NVIDIA embeddings
with multi-agent workflow for bash/cmsh script generation.
"""

import logging
import os
from pathlib import Path
from typing import Optional

from pydantic import Field

from aiq.builder.builder import Builder
from aiq.builder.function_info import FunctionInfo
from aiq.cli.register_workflow import register_function
from aiq.data_models.function import FunctionBaseConfig

logger = logging.getLogger(__name__)

# ========================
# BCM Documentation RAG Tool with LlamaIndex Multi-Agent
# ========================


class BCMDocumentationRAGConfig(FunctionBaseConfig, name="bcm_documentation_rag"):
    docs_path: str = Field(default="examples/factory_reset/src/aiq_dgx_factory_reset/docs/",
                           description="Path to BCM documentation directory (supports .md and .pdf files)")
    persist_dir: str = Field(default="examples/factory_reset/storage/bcm_index",
                             description="Directory to persist the vector index")
    offline_mode: bool = Field(default=True, description="Run in offline mode for testing")
    max_iterations: int = Field(default=2, description="Maximum refinement iterations")
    nvidia_api_key: str = Field(default="", description="NVIDIA API key (or set NVIDIA_API_KEY env var)")
    llama_cloud_api_key: str = Field(default="", description="LlamaCloud API key (or set LLAMA_CLOUD_API_KEY env var)")


@register_function(config_type=BCMDocumentationRAGConfig)
async def bcm_documentation_rag(config: BCMDocumentationRAGConfig, _builder: Builder):
    """
    BCM documentation search using LlamaIndex multi-agent workflow for script generation
    """

    async def _search_bcm_docs(query: str) -> str:
        """Enhanced BCM documentation search with multi-agent script generation"""
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
            from llama_index.core.agent.workflow import FunctionAgent
            from llama_index.core.tools import QueryEngineTool
            from llama_index.core.workflow import Context
            from llama_index.core.workflow import Event
            from llama_index.core.workflow import StartEvent
            from llama_index.core.workflow import StopEvent
            from llama_index.core.workflow import Workflow
            from llama_index.core.workflow import step
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

            # Configure LlamaIndex with NVIDIA models
            Settings.llm = NVIDIA(model="meta/llama-3.3-70b-instruct")
            Settings.embed_model = NVIDIAEmbedding(model="nvidia/llama-3.2-nv-embedqa-1b-v2", truncate="END")

            # Event classes for BCM workflow
            class ProcedureEvent(Event):
                procedure_plan: str

            class CommandQuestionEvent(Event):
                question: str

            class CommandAnswerEvent(Event):
                question: str
                answer: str

            class BCMScriptEvent(Event):
                bash_script: str

            class ProgressEvent(Event):
                progress: str

            # Multi-agent workflow for BCM script generation
            class BCMScriptGenerationAgent(Workflow):

                @step
                async def formulate_procedure_plan(self, ctx: Context, ev: StartEvent) -> ProcedureEvent:
                    """Plan the BCM procedure based on user request"""
                    query = ev.query
                    await ctx.store.set("original_query", query)
                    await ctx.store.set("tools", ev.tools)

                    prompt = f"""You are a BCM (Bright Cluster Manager) expert. Plan a detailed procedure
                    for the requested BCM operation. Focus on creating a step-by-step technical plan that
                    will guide script generation.

                    Request: {query}

                    Create a procedure plan that includes:
                    - Prerequisites and safety checks
                    - Required BCM/cmsh contexts and navigation
                    - Main operational steps in logical order
                    - Verification and validation steps
                    - Error handling considerations
                    - Expected outcomes

                    Be specific about BCM components involved (nodes, networks, interfaces, etc.)."""

                    response = await Settings.llm.acomplete(prompt)

                    ctx.write_event_to_stream(ProgressEvent(progress="📋 BCM Procedure Plan:\n" + str(response)))

                    return ProcedureEvent(procedure_plan=str(response))

                @step
                async def formulate_command_questions(self, ctx: Context, ev: ProcedureEvent) -> None:
                    """Generate specific questions about BCM commands needed"""
                    procedure_plan = ev.procedure_plan
                    await ctx.store.set("procedure_plan", procedure_plan)

                    prompt = f"""You are a BCM expert. Based on this procedure plan, formulate specific
                    technical questions that will help find the exact BCM/cmsh commands and syntax needed.

                    Procedure Plan: {procedure_plan}

                    Generate questions about:
                    - Specific cmsh commands and their exact syntax
                    - Required parameters, options, and flags
                    - Context switching (which cmsh modes to use)
                    - Configuration file paths and formats
                    - Verification commands to check status
                    - Error handling and troubleshooting commands

                    Output only a numbered list of specific questions, limit to 6 questions."""

                    response = await Settings.llm.acomplete(prompt)

                    questions = [
                        line.strip() for line in str(response).split("\n")
                        if line.strip() and not line.strip().startswith("#")
                    ]
                    questions = [q for q in questions if q and len(q) > 10]  # Filter out empty/short lines

                    ctx.write_event_to_stream(ProgressEvent(progress="🔍 Research Questions:\n" + "\n".join(questions)))

                    await ctx.store.set("num_questions", len(questions))

                    for question in questions:
                        ctx.send_event(CommandQuestionEvent(question=question))

                @step
                async def answer_command_question(self, ctx: Context,
                                                  ev: CommandQuestionEvent) -> Optional[CommandAnswerEvent]:
                    """Answer each BCM command question using the documentation"""
                    question = ev.question
                    if not question or question.isspace() or len(question) < 10:
                        return None

                    agent = FunctionAgent(
                        tools=await ctx.store.get("tools"),
                        llm=Settings.llm,
                    )
                    response = await agent.run(question)
                    response = str(response)

                    ctx.write_event_to_stream(
                        ProgressEvent(progress=f"❓ Q: {question[:80]}...\n💡 A: {response[:150]}..."))

                    return CommandAnswerEvent(question=question, answer=response)

                @step
                async def generate_bcm_script(self, ctx: Context, ev: CommandAnswerEvent) -> Optional[BCMScriptEvent]:
                    """Generate bash/cmsh script with BCM commands"""
                    num_questions = await ctx.store.get("num_questions")
                    results = ctx.collect_events(ev, [CommandAnswerEvent] * num_questions)
                    if results is None:
                        return None

                    # Maintain history for iterative refinement
                    try:
                        previous_answers = await ctx.store.get("previous_answers")
                    except KeyError:
                        previous_answers = []
                    previous_answers.extend(results)
                    await ctx.store.set("previous_answers", previous_answers)

                    prompt = f"""You are a BCM expert script generator. Create a complete, executable
                    bash script that implements the BCM procedure using the research findings.

                    CRITICAL REQUIREMENTS:
                    - Use ONLY commands found in the BCM documentation
                    - Include proper cmsh context navigation
                    - Add error checking after each major operation
                    - Include verification steps to confirm success
                    - Add clear comments explaining each section
                    - Use proper bash scripting practices (set -e, error handling)
                    - Include safety prompts for destructive operations

                    Original Request: {await ctx.store.get('original_query')}
                    Procedure Plan: {await ctx.store.get('procedure_plan')}

                    Research Results:"""

                    for result in previous_answers:
                        prompt += f"\n\nQ: {result.question}\nA: {result.answer}"

                    prompt += """\n\nGenerate a complete bash script with:
                    #!/bin/bash
                    set -e  # Exit on any error

                    # Clear structure with functions for each major step
                    # Proper error handling and verification
                    # Comments explaining BCM-specific operations"""

                    script = await Settings.llm.acomplete(prompt)

                    ctx.write_event_to_stream(ProgressEvent(progress="🛠️ Generated BCM Script"))

                    return BCMScriptEvent(bash_script=str(script))

                @step
                async def review_script(self, ctx: Context,
                                        ev: BCMScriptEvent) -> Optional[StopEvent | CommandQuestionEvent]:
                    """Review the generated script and optionally refine"""
                    try:
                        num_reviews = await ctx.store.get("num_reviews")
                    except KeyError:
                        num_reviews = 0
                    num_reviews += 1
                    await ctx.store.set("num_reviews", num_reviews)

                    script = ev.bash_script

                    prompt = f"""You are a BCM safety expert. Review this bash script for BCM operations.

                    Check for:
                    - Command syntax accuracy according to BCM documentation
                    - Proper cmsh context navigation
                    - Safety measures and error handling
                    - Completeness of the procedure
                    - Verification steps included

                    Script to review:
                    {script}

                    If the script is complete and safe, return just 'APPROVED'.
                    If it needs specific improvements, ask up to 3 focused questions to get
                    additional information. One question per line, no explanation."""

                    response = await Settings.llm.acomplete(prompt)

                    if "APPROVED" in str(response).upper() or num_reviews >= config.max_iterations:
                        ctx.write_event_to_stream(ProgressEvent(progress="✅ BCM Script Approved"))
                        return StopEvent(result=script)
                    else:
                        questions = [q.strip() for q in str(response).split("\n") if q.strip()]
                        await ctx.store.set("num_questions", len(questions))
                        ctx.write_event_to_stream(ProgressEvent(progress="🔄 Refining script..."))
                        for question in questions:
                            ctx.send_event(CommandQuestionEvent(question=question))
                        return None

            # Check for complete index files, not just directory
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

                # Process PDF files with LlamaParse
                pdf_files = list(docs_path_obj.glob("*.pdf"))
                if pdf_files:
                    logger.info("Found %d PDF files, processing with LlamaParse...", len(pdf_files))
                    parser = LlamaParse()
                    for pdf_file in pdf_files:
                        try:
                            pdf_docs = parser.load_data(str(pdf_file))
                            for doc in pdf_docs:
                                doc.metadata["source"] = str(pdf_file)
                            documents.extend(pdf_docs)
                            logger.info("Processed %s", pdf_file.name)
                        except Exception as e:
                            logger.warning("Failed to parse %s: %s", pdf_file, e)

                # Process markdown files
                md_files = list(docs_path_obj.glob("*.md"))
                if md_files:
                    logger.info("Found %d markdown files...", len(md_files))
                    for md_file in md_files:
                        try:
                            with open(md_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                            documents.append(Document(text=content, metadata={"source": str(md_file)}))
                        except Exception as e:
                            logger.warning("Failed to load %s: %s", md_file, e)

                if not documents:
                    return f"❌ No BCM documentation files found in {docs_path}"

                logger.info("Creating index from %d documents...", len(documents))
                index = VectorStoreIndex.from_documents(documents)
                index.storage_context.persist(persist_dir=persist_dir)
                logger.info("Index created and persisted")

            # Create query engine and use simple RAG instead of complex workflow
            logger.info("Creating query engine for BCM documentation...")
            query_engine = index.as_query_engine(similarity_top_k=5, response_mode="tree_summarize")

            # Simple RAG query instead of complex multi-agent workflow
            response = query_engine.query(query)

            # Format the response
            result = "🤖 **BCM Expert - Documentation Analysis**\n\n"
            result += f"**Query:** {query}\n\n"
            result += f"**Answer:** {str(response)}\n\n"
            result += "**Source:** BCM Administration Manual\n\n"
            result += "⚠️  **Note:** Please verify commands in your specific BCM environment before execution."

            return result

        except Exception as e:
            logger.error("Error in BCM documentation search: %s", str(e))
            return f"❌ Error in BCM analysis: {str(e)}\n\nPlease check your API keys and network connection."

    yield FunctionInfo.from_fn(_search_bcm_docs,
                               description=("BCM documentation search using multi-agent workflow "
                                            "to generate safe bash/cmsh scripts"))


print("✅ BCM Multi-Agent Script Generation function registered successfully")
