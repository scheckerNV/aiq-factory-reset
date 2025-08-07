"""
Factory Reset Workflow with Reasoning Orchestrator and ReAct Agents

This module implements a LangGraph-based workflow that uses a reasoning orchestrator
to coordinate between sequential networking and DGX ReAct agents for complete
DGX SuperPOD factory reset operations.
"""

import logging

from aiq.builder.builder import Builder
from aiq.builder.framework_enum import LLMFrameworkEnum
from aiq.cli.register_workflow import register_function
from aiq.data_models.component_ref import FunctionRef
from aiq.data_models.component_ref import LLMRef
from aiq.data_models.function import FunctionBaseConfig

logger = logging.getLogger(__name__)


class FactoryResetReasoningWorkflowConfig(FunctionBaseConfig, name="factory_reset_reasoning_workflow"):
    llm: LLMRef
    networking_agent: FunctionRef
    dgx_agent: FunctionRef


@register_function(config_type=FactoryResetReasoningWorkflowConfig, framework_wrappers=[LLMFrameworkEnum.LANGCHAIN])
async def factory_reset_reasoning_workflow(config: FactoryResetReasoningWorkflowConfig, builder: Builder):
    """Factory Reset Reasoning Orchestrator coordinating ReAct agents"""

    from typing import TypedDict

    from colorama import Fore
    from langchain_community.chat_message_histories import ChatMessageHistory
    from langchain_core.messages import BaseMessage
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.prompts import PromptTemplate
    from langchain_core.runnables import RunnablePassthrough
    from langchain_core.runnables.history import RunnableWithMessageHistory
    from langgraph.graph import END
    from langgraph.graph import StateGraph

    # Use builder to get framework-specific tools and LLMs
    logger.info("Factory reset reasoning workflow config = %s", config)

    llm = await builder.get_llm(llm_name=config.llm, wrapper_type=LLMFrameworkEnum.LANGCHAIN)
    networking_agent = builder.get_tool(fn_name=config.networking_agent, wrapper_type=LLMFrameworkEnum.LANGCHAIN)
    dgx_agent = builder.get_tool(fn_name=config.dgx_agent, wrapper_type=LLMFrameworkEnum.LANGCHAIN)

    chat_hist = ChatMessageHistory()

    # Reasoning orchestrator prompt for high-level planning
    reasoning_prompt = """
    You are the Factory Reset Reasoning Orchestrator. Your role is to analyze the request and determine
    the appropriate execution strategy for DGX SuperPOD factory reset operations.

    User Request: {input}

    CRITICAL EXECUTION RULES:
    1. Network reset operations MUST be completed BEFORE any DGX node operations
    2. Both networking and DGX operations may require BCM commands
    3. Some requests may only need one type of agent

    Analyze the request and classify as:
    - "Networking_Only" - Only network-related issues (switches, VLANs, IP addressing, network fabric)
    - "DGX_Only" - Only DGX hardware issues (assuming network is already functional)
    - "Sequential_Both" - Requires both networking first, then DGX operations (most factory resets)
    - "Analysis_Only" - Requesting information/analysis without actual reset operations

    Reasoning Process:
    1. What specific components need to be reset?
    2. Does this involve network infrastructure changes?
    3. Does this involve DGX hardware/node operations?
    4. What is the correct sequence of operations?

    Based on your analysis, respond with ONLY the classification: Networking_Only, DGX_Only, Sequential_Both, or Analysis_Only

    Classification:"""

    reasoning_chain = ({
        "input": RunnablePassthrough()
    } | PromptTemplate.from_template(reasoning_prompt) | llm | StrOutputParser())

    reasoning_chain_with_history = RunnableWithMessageHistory(
        reasoning_chain,
        lambda _: chat_hist,
        history_messages_key="chat_history",
    )

    class AgentState(TypedDict):
        """State management for reasoning orchestrator workflow"""
        input: str
        chat_history: list[BaseMessage] | None
        execution_strategy: str | None
        networking_result: str | None
        dgx_result: str | None
        final_output: str | None

    async def reasoning_orchestrator(state: AgentState):
        """Analyze the request and determine execution strategy"""
        query = state["input"]
        logger.info("%s========== Reasoning Orchestrator - analyzing request", Fore.BLUE)

        execution_strategy = await reasoning_chain_with_history.ainvoke(
            {"input": query},
            {"configurable": {
                "session_id": "unused"
            }},
        )

        logger.info("Reasoning decision: %s", execution_strategy.strip())
        return {'input': query, 'execution_strategy': execution_strategy.strip(), 'chat_history': chat_hist}

    async def execute_networking(state: AgentState):
        """Execute networking analysis/operations using ReAct agent"""
        query = state["input"]
        logger.info("%s========== Executing Networking ReAct Agent", Fore.GREEN)

        # Add context about sequential execution
        networking_query = f"""
        Original request: {query}

        CONTEXT: You are handling the NETWORKING phase of a factory reset operation.
        Focus on network infrastructure, configurations, and connectivity requirements.
        Provide sequential reasoning and actions for network reset procedures.
        Remember that DGX operations will follow after network is ready.
        """

        try:
            networking_result = await networking_agent.ainvoke(networking_query)
            logger.info("Networking agent completed successfully")
            return {**state, 'networking_result': networking_result}
        except Exception as e:
            logger.error("Error in networking agent: %s", e)
            return {**state, 'networking_result': f"❌ Networking agent error: {str(e)}"}

    async def execute_dgx(state: AgentState):
        """Execute DGX analysis/operations using ReAct agent"""
        query = state["input"]
        networking_result = state.get('networking_result', '')
        logger.info("%s========== Executing DGX ReAct Agent", Fore.MAGENTA)

        # Add context about sequential execution and networking status
        dgx_query = f"""
        Original request: {query}

        CONTEXT: You are handling the DGX HARDWARE phase of a factory reset operation.
        The networking phase has been completed with the following status:

        Networking Status: {networking_result if networking_result else "Not applicable"}

        Focus on DGX hardware, BMC operations, and node-specific procedures.
        Provide sequential reasoning and actions for DGX reset procedures.
        Assume network infrastructure is ready for DGX operations.
        """

        try:
            dgx_result = await dgx_agent.ainvoke(dgx_query)
            logger.info("DGX agent completed successfully")
            return {**state, 'dgx_result': dgx_result}
        except Exception as e:
            logger.error("Error in DGX agent: %s", e)
            return {**state, 'dgx_result': f"❌ DGX agent error: {str(e)}"}

    async def synthesize_results(state: AgentState):
        """Synthesize results from executed agents"""
        execution_strategy = state.get('execution_strategy', '').lower()
        networking_result = state.get('networking_result', '')
        dgx_result = state.get('dgx_result', '')

        logger.info("%s========== Synthesizing Results", Fore.YELLOW)

        if 'networking_only' in execution_strategy:
            final_output = f"""# 🌐 DGX SuperPOD Networking Reset Analysis

{networking_result}

---
**Execution Strategy**: Networking Only
**Status**: Network analysis completed
"""

        elif 'dgx_only' in execution_strategy:
            final_output = f"""# 🖥️ DGX Hardware Reset Analysis

{dgx_result}

---
**Execution Strategy**: DGX Only
**Status**: DGX analysis completed
"""

        elif 'sequential_both' in execution_strategy:
            final_output = f"""# 🔄 DGX SuperPOD Complete Factory Reset

## Phase 1: 🌐 Networking Reset (MUST BE COMPLETED FIRST)
{networking_result}

---

## Phase 2: 🖥️ DGX Hardware Reset (EXECUTE AFTER NETWORKING)
{dgx_result}

---

## ⚠️ **CRITICAL EXECUTION ORDER**
1. **FIRST**: Complete all networking reset procedures from Phase 1
2. **VERIFY**: Ensure network connectivity and fabric are operational
3. **SECOND**: Execute DGX hardware reset procedures from Phase 2
4. **VALIDATE**: Verify complete cluster functionality after both phases

**Execution Strategy**: Sequential Both Phases
**Status**: Complete analysis for network → DGX reset sequence
"""

        elif 'analysis_only' in execution_strategy:
            if networking_result and dgx_result:
                final_output = f"""# 📋 DGX SuperPOD Analysis Report

## 🌐 Networking Analysis
{networking_result}

---

## 🖥️ DGX Analysis
{dgx_result}

---
**Execution Strategy**: Analysis Only
**Status**: Information gathering completed
"""
            elif networking_result:
                final_output = f"""# 📋 DGX SuperPOD Networking Analysis

{networking_result}

---
**Execution Strategy**: Analysis Only - Networking Focus
**Status**: Network information gathering completed
"""
            elif dgx_result:
                final_output = f"""# 📋 DGX SuperPOD DGX Analysis

{dgx_result}

---
**Execution Strategy**: Analysis Only - DGX Focus
**Status**: DGX information gathering completed
"""
            else:
                final_output = "❌ No analysis results available"

        else:
            final_output = f"""❌ Unknown execution strategy: {execution_strategy}

Available strategies: Networking_Only, DGX_Only, Sequential_Both, Analysis_Only"""

        return {**state, 'final_output': final_output}

    def route_execution(state: AgentState):
        """Route based on execution strategy"""
        execution_strategy = state.get('execution_strategy', '').lower()

        if 'networking_only' in execution_strategy:
            return "networking"
        elif 'dgx_only' in execution_strategy:
            return "dgx"
        elif 'sequential_both' in execution_strategy:
            return "networking"  # Start with networking for sequential
        elif 'analysis_only' in execution_strategy:
            return "networking"  # Default to networking for analysis
        else:
            return "synthesize"

    def route_after_networking(state: AgentState):
        """Route after networking phase"""
        execution_strategy = state.get('execution_strategy', '').lower()

        if 'sequential_both' in execution_strategy:
            return "dgx"  # Continue to DGX phase
        else:
            return "synthesize"  # Go directly to synthesis

    def route_after_dgx(state: AgentState):
        """Always go to synthesis after DGX"""
        return "synthesize"

    # Build the workflow graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("reasoning", reasoning_orchestrator)
    workflow.add_node("networking", execute_networking)
    workflow.add_node("dgx", execute_dgx)
    workflow.add_node("synthesize", synthesize_results)

    # Set entry point
    workflow.set_entry_point("reasoning")

    # Define routing logic
    workflow.add_conditional_edges("reasoning",
                                   route_execution, {
                                       "networking": "networking", "dgx": "dgx", "synthesize": "synthesize"
                                   })

    workflow.add_conditional_edges("networking", route_after_networking, {"dgx": "dgx", "synthesize": "synthesize"})

    workflow.add_conditional_edges("dgx", route_after_dgx, {"synthesize": "synthesize"})

    workflow.add_edge("synthesize", END)

    app = workflow.compile()

    async def _response_fn(input_message: str) -> str:
        """Execute the factory reset reasoning workflow"""
        try:
            logger.info("🚀 Starting factory reset reasoning workflow")
            result = await app.ainvoke({"input": input_message, "chat_history": chat_hist})
            output = result.get("final_output", "No output generated")
            logger.info("✅ Factory reset reasoning workflow completed")
            return output
        except Exception as e:
            logger.error("❌ Error in factory reset reasoning workflow: %s", e)
            return f"❌ Error in factory reset reasoning workflow: {str(e)}\n\nPlease check your configuration and try again."

    try:
        yield _response_fn
    except GeneratorExit:
        logger.exception("Factory reset reasoning workflow exited early!", exc_info=True)
    finally:
        logger.debug("Cleaning up factory reset reasoning workflow.")


print("✅ Factory Reset Reasoning workflow registered successfully")
