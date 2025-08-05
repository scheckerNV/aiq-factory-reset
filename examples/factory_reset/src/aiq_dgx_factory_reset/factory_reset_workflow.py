"""
Factory Reset Workflow with Multi-Agent Coordination

This module implements a LangGraph-based workflow that coordinates between
networking and BCM experts for complete DGX SuperPOD factory reset operations.
"""

import logging

from aiq.builder.builder import Builder
from aiq.builder.framework_enum import LLMFrameworkEnum
from aiq.cli.register_workflow import register_function
from aiq.data_models.component_ref import FunctionRef
from aiq.data_models.component_ref import LLMRef
from aiq.data_models.function import FunctionBaseConfig

logger = logging.getLogger(__name__)


class FactoryResetWorkflowConfig(FunctionBaseConfig, name="factory_reset_workflow"):
    llm: LLMRef
    networking_tool: FunctionRef
    bcm_tool: FunctionRef


@register_function(config_type=FactoryResetWorkflowConfig, framework_wrappers=[LLMFrameworkEnum.LANGCHAIN])
async def factory_reset_workflow(config: FactoryResetWorkflowConfig, builder: Builder):
    """Factory Reset Orchestrator using LangGraph for multi-agent coordination"""

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
    logger.info("Factory reset workflow config = %s", config)

    llm = await builder.get_llm(llm_name=config.llm, wrapper_type=LLMFrameworkEnum.LANGCHAIN)
    networking_tool = builder.get_tool(fn_name=config.networking_tool, wrapper_type=LLMFrameworkEnum.LANGCHAIN)
    bcm_tool = builder.get_tool(fn_name=config.bcm_tool, wrapper_type=LLMFrameworkEnum.LANGCHAIN)

    chat_hist = ChatMessageHistory()

    # Router prompt to classify factory reset requests
    router_prompt = """
    Given the user input below, classify it as either 'Networking', 'BCM', or 'Both'.

    'Networking' - questions about network configuration, IPs, VLANs, switches, interface setup, etc.
    'BCM' - questions specifically about BCM commands, cluster management, node operations without networking context
    'Both' - questions that require both networking analysis and BCM command generation (most factory reset scenarios)

    Examples:
    - "Reset networking for dgx-01" -> Both
    - "What are the IP requirements for Demeter cluster?" -> Networking
    - "How do I add a node in BCM?" -> BCM
    - "Factory reset the entire cluster" -> Both

    User query: {input}
    Classification:"""

    routing_chain = ({
        "input": RunnablePassthrough()
    } | PromptTemplate.from_template(router_prompt) | llm | StrOutputParser())

    supervisor_chain_with_message_history = RunnableWithMessageHistory(
        routing_chain,
        lambda _: chat_hist,
        history_messages_key="chat_history",
    )

    class AgentState(TypedDict):
        """State management for factory reset workflow"""
        input: str
        chat_history: list[BaseMessage] | None
        chosen_workflow: str | None
        networking_result: str | None
        bcm_result: str | None
        final_output: str | None

    async def supervisor(state: AgentState):
        """Classify the user request and determine workflow path"""
        query = state["input"]
        chosen_workflow = await supervisor_chain_with_message_history.ainvoke(
            {"input": query},
            {"configurable": {
                "session_id": "unused"
            }},
        )
        logger.info("%s========== Supervisor node - classified request as: %s", Fore.BLUE, chosen_workflow.strip())
        return {'input': query, "chosen_workflow": chosen_workflow.strip(), "chat_history": chat_hist}

    async def router(state: AgentState):
        """Route to appropriate workflow step based on current state"""
        status = list(state.keys())
        logger.info("========== Router node - current status keys: %s%s", Fore.CYAN, status)

        if 'final_output' in state and state['final_output']:
            route_to = "end"
        elif 'bcm_result' in state and state['bcm_result']:
            route_to = "synthesize"
        elif 'networking_result' in state and state['networking_result']:
            # If we have networking results, check if we need BCM too
            chosen_workflow_str = state.get('chosen_workflow', '')
            chosen_workflow = chosen_workflow_str.lower() if chosen_workflow_str else ''
            if 'both' in chosen_workflow:
                route_to = "bcm_expert"
            else:
                route_to = "synthesize"
        elif 'chosen_workflow' in state:
            # Start with networking for 'Both' and 'Networking', or BCM for 'BCM' only
            chosen_workflow_str = state.get('chosen_workflow', '')
            chosen_workflow = chosen_workflow_str.lower() if chosen_workflow_str else ''
            if 'bcm' in chosen_workflow and 'both' not in chosen_workflow:
                route_to = "bcm_expert"
            else:
                route_to = "networking_expert"
        else:
            route_to = "end"

        logger.info(" ############# Router directing to: %s %s", route_to, Fore.RESET)
        return route_to

    async def networking_expert(state: AgentState):
        """Call networking expert to analyze requirements"""
        query = state["input"]
        logger.info("%s========== Networking Expert node - processing query: %s", Fore.GREEN, query[:100] + "...")

        try:
            networking_result = await networking_tool.ainvoke(query)
            logger.info("Networking expert completed successfully")
            logger.info("Result preview: %s", networking_result[:200] + "...")

            return {**state, "networking_result": networking_result}
        except Exception as e:
            logger.error("Error in networking expert: %s", e)
            error_result = f"❌ Error in networking analysis: {str(e)}"
            return {**state, "networking_result": error_result}

    async def bcm_expert(state: AgentState):
        """Call BCM expert with networking context if available"""
        query = state["input"]
        networking_context = state.get("networking_result", "")

        logger.info("%s========== BCM Expert node - processing query", Fore.YELLOW)

        try:
            # Create enhanced query with networking context if available
            if networking_context and "❌" not in networking_context:
                enhanced_query = f"""
Original request: {query}

Networking analysis results:
{networking_context}

Based on the networking analysis above, generate the appropriate BCM commands for this factory reset scenario.
"""
                logger.info("Using enhanced query with networking context")
            else:
                enhanced_query = query
                logger.info("Using original query (no networking context available)")

            bcm_result = await bcm_tool.ainvoke(enhanced_query)
            logger.info("BCM expert completed successfully")
            logger.info("Result preview: %s", bcm_result[:200] + "...")

            return {**state, "bcm_result": bcm_result}
        except Exception as e:
            logger.error("Error in BCM expert: %s", e)
            error_result = f"❌ Error in BCM analysis: {str(e)}"
            return {**state, "bcm_result": error_result}

    async def synthesize_results(state: AgentState):
        """Combine networking and BCM results into final output"""
        networking_result = state.get("networking_result", "")
        bcm_result = state.get("bcm_result", "")
        chosen_workflow = state.get("chosen_workflow", "Both")
        chosen_workflow_lower = chosen_workflow.lower() if chosen_workflow else 'both'

        logger.info("%s========== Synthesize node - combining results", Fore.MAGENTA)

        if chosen_workflow_lower == "networking":
            final_output = networking_result
        elif chosen_workflow_lower == "bcm":
            final_output = bcm_result
        else:  # Both or other
            if networking_result and bcm_result:
                final_output = f"""# 🔄 DGX SuperPOD Factory Reset Analysis

## 🌐 Networking Analysis
{networking_result}

---

## 🤖 BCM Command Generation
{bcm_result}

---

## ⚠️ **IMPORTANT: Execution Order**
1. **First:** Review and implement the networking requirements above
2. **Second:** Execute the BCM commands in the specified order
3. **Third:** Verify cluster connectivity and node status after reset
4. **Finally:** Run post-reset validation checks

## 📋 **Next Steps Summary**
- Verify network configurations before executing BCM commands
- Test connectivity between management and compute nodes
- Validate cluster state after factory reset completion
"""
            elif networking_result:
                final_output = networking_result
            elif bcm_result:
                final_output = bcm_result
            else:
                final_output = "❌ No results generated from either networking or BCM experts."

        logger.info("Final output synthesized successfully")
        return {**state, "final_output": final_output}

    # Build the workflow graph
    workflow = StateGraph(AgentState)
    workflow.add_node("supervisor", supervisor)
    workflow.add_node("networking_expert", networking_expert)
    workflow.add_node("bcm_expert", bcm_expert)
    workflow.add_node("synthesize", synthesize_results)

    workflow.set_entry_point("supervisor")

    # Define the conditional edges based on router logic
    workflow.add_conditional_edges(
        "supervisor",
        router,
        {
            "networking_expert": "networking_expert", "bcm_expert": "bcm_expert", "end": END
        },
    )

    workflow.add_conditional_edges(
        "networking_expert",
        router,
        {
            "bcm_expert": "bcm_expert", "synthesize": "synthesize", "end": END
        },
    )

    workflow.add_conditional_edges(
        "bcm_expert",
        router,
        {
            "synthesize": "synthesize", "end": END
        },
    )

    workflow.add_edge("synthesize", END)

    app = workflow.compile()

    async def _response_fn(input_message: str) -> str:
        """Execute the factory reset workflow"""
        try:
            logger.info("🚀 Starting factory reset workflow execution")
            result = await app.ainvoke({"input": input_message, "chat_history": chat_hist})
            output = result.get("final_output", "No output generated")
            logger.info("✅ Factory reset workflow completed successfully")
            return output
        except Exception as e:
            logger.error("❌ Error in factory reset workflow: %s", e)
            return f"❌ Error in factory reset workflow: {str(e)}\n\nPlease check your configuration and try again."

    try:
        yield _response_fn
    except GeneratorExit:
        logger.exception("Factory reset workflow exited early!", exc_info=True)
    finally:
        logger.debug("Cleaning up factory reset workflow.")


print("✅ Factory Reset workflow registered successfully")
