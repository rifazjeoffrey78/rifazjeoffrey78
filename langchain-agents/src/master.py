from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver

from agent import State, Assistant, agent_runnable, route_tools, model
from tools import create_tool_node_with_fallback, getToolsSafe, getToolsSensitive
from langgraph.prebuilt import create_react_agent

class Master():
    def __init__(self):
        self.app = self.initGraph()

    def initGraph(self):
        # Define a new graph
        workflow = StateGraph(State)

        def user_info(state: State):
            return {"user_info": "This is a user info string."}

        # Set the entrypoint as `agent`
        # This means that this node is the first one called
        workflow.add_edge(START, "agent")

        # Define the two nodes we will cycle between
        workflow.add_node("agent", Assistant(agent_runnable))
        workflow.add_node("sensitive_tools", create_tool_node_with_fallback(getToolsSensitive()))
        workflow.add_node("safe_tools", create_tool_node_with_fallback(getToolsSafe()))

        # We now add a conditional edge
        workflow.add_conditional_edges(
            # First, we define the start node. We use `agent`.
            # This means these are the edges taken after the `agent` node is called.
            "agent",
            # Next, we pass in the function that will determine which node is called next.
            route_tools,
            ["safe_tools", "sensitive_tools", END]
        )

        # We now add a normal edge from `tools` to `agent`.
        # This means that after `tools` is called, `agent` node is called next.
        #workflow.add_edge("sensitive_tools", 'agent')
        #workflow.add_edge("safe_tools", 'agent')

        # Initialize memory to persist state between graph runs
        checkpointer = MemorySaver()

        # Finally, we compile it!
        # This compiles it into a LangChain Runnable,
        # meaning you can use it as you would any other runnable.
        # Note that we're (optionally) passing the memory when compiling the graph
        #app = workflow.compile(checkpointer=checkpointer)
        app = workflow.compile()
        #app = create_react_agent(model, getToolsSafe() + getToolsSensitive())
        return app

    def invoke(self, messages: list[HumanMessage], config: dict):
        # Use the Runnable
        final_state = self.app.invoke(
            {"messages": messages},
            config=config
        )
        print('%%%%%%%%%')
        print(final_state)
        print('%%%%%%%%%')
        return final_state["messages"][-1].content
    # # Use the Runnable
    # final_state = app.invoke(
    #     {"messages": [HumanMessage(content="what is the weather in sf")]},
    #     config={"configurable": {"thread_id": 42}}
    # )
    # print('^^^^^^')
    # print(final_state)
    # print(final_state["messages"][-1].content)
    # print('^^^^^^')