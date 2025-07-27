from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv  
from langchain_core.messages import BaseMessage # The foundational class for all message types in LangGraph
from langchain_core.messages import ToolMessage # Passes data back to LLM after it calls a tool such as the content and the tool_call_id
from langchain_core.messages import SystemMessage # Message for providing instructions to the LLM
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode


load_dotenv()  # Load environment variables from a .env file

#reduced messages are

class ReactAgentState(TypedDict):
    messages : Annotated[Sequence[BaseMessage], add_messages]  # List of messages in the conversation


@tool
def add(a:int, b:int) -> int:
    """Adds two numbers."""
    return a + b


@tool
def subt(a:int, b:int) -> int:
    """Subtract two numbers."""
    return a - b

@tool
def mult(a:int, b:int) -> int:
    """Multiply two numbers."""
    return a + b


tools = [add, subt , mult]

model = ChatOpenAI(model = "gpt -4o")


def model_call(state:ReactAgentState) ->ReactAgentState:
    system_prompt = SystemMessage(content = "Your are my AI assistant, plkease answer my query to the best of your ability")

    response = model.invoke({system_prompt} + state["messages"])
    return {"messages" : [response]}


def should_continue(state : ReactAgentState):
    messages = state["messages"]
    last_messages = messages[-1]

    if not last_messages.tool_calls:
        return "end"
    else:
        return "continue"
    
graph = StateGraph(ReactAgentState)

graph.add_node("our_agent", model_call)

tool_node = ToolNode(tools = tools)
graph.add_node("tools", tool_node)

graph.set_entery_point("our_agent")

graph.add_conditional_edges(
    "our_agent",
    should_continue,
    {
        "continue":"tools",
        "end":END
    }
)

graph.add_edge("tools", "our_agent")

agent = graph.compile()

if __name__ == "__main__":
    user_input = input("Enter your message: ")
    while user_input.lower() != "exit":
        agent.invoke({"messages": [BaseMessage(content=user_input)]})
        user_input = input("Enter your message: ")
        if user_input.lower() == "exit":
            break