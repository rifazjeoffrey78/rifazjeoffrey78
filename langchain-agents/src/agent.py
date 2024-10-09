from langchain_together import ChatTogether
from langgraph.graph import END, START, StateGraph, MessagesState
from typing import Annotated, Literal, TypedDict
from langsmith import traceable
from langchain_core.runnables import Runnable, RunnableConfig
from langgraph.graph.message import AnyMessage, add_messages
from datetime import date, datetime
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import tools_condition
from langchain_mistralai import ChatMistralAI

from tools import getToolsSensitive, getToolsSafe

from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    user_info: str

class Assistant:
    def __init__(self, runnable: Runnable):
        self.runnable = runnable

    def __call__(self, state: State, config: RunnableConfig):
        while True:
            print('-------------------XX')
            print(state)
            print('-------------------XX')
            result = self.runnable.invoke(state)
            # If the LLM happens to return an empty response, we will re-prompt it
            # for an actual response.
            if not result.tool_calls and (
                not result.content
                or isinstance(result.content, list)
                and not result.content[0].get("content")
            ):
                print("11111")
                messages = state["messages"] + [("user", "Respond with a real output.")]
                state = {**state, "messages": messages}
            else:
                print("22222")
                break
        return {"messages": result}

# Define the function that calls the model
def call_model(state: MessagesState):
    messages = state['messages']
    response = model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}

def route_tools(state: State):
    print('$$$$$$$$$')
    print(state)
    print('$$$$$$$$$')
    next_node = tools_condition(state)
    print('******')
    print(next_node)
    print('******')
    # If no tools are invoked, return to the user
    if next_node == END:
        return END
    ai_message = state["messages"][-1]
    print(')))))))')
    print(ai_message)
    print(')))))))')
    # This assumes single tool calls. To handle parallel tool calling, you'd want to
    # use an ANY condition
    first_tool_call = ai_message.tool_calls[0]
    print('&&&')
    print(first_tool_call)
    print(first_tool_call["name"])
    print(getToolsSensitive())
    print('&&&')
    #if first_tool_call["name"] in getToolsSensitive():
    if any(tool.name == first_tool_call["name"] for tool in getToolsSensitive()):
        print("inside sensitive tool by jaff")
        return "sensitive_tools"
    print(',,,,,,,,,,,,,,,,,,,')
    return "safe_tools"

assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful support assistant for weather and stocks. "
            " When searching, be persistent. Expand your query bounds if the first search returns no results. "
            " If a search comes up empty, expand your search before giving up."
            #"\n\nCurrent user:\n<User>\n{user_info}\n</User>"
            #"\nCurrent time: {time}."
            ,
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())

model = ChatTogether(model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo", temperature=0)
#model = ChatMistralAI(model="mistral-large-latest")

agent_runnable = assistant_prompt | model.bind_tools(
    getToolsSensitive() + getToolsSafe()
)

