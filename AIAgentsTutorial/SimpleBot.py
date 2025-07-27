from typing import TypedDict , List
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START,END
from dotenv import load_dotenv #For loading environment variables, such as for example API keys

# This is a simple bot using LangGraph and LangChain.
#Note,  We can use LangChanin in LangGraph,as langgraph was created to compile also langchain on top of it ,as we need to use the LangChain OpenAI wrapper to use the OpenAI API.

load_dotenv() 


class SimpleBotState(TypedDict):
    messages: List[HumanMessage]


llm = ChatOpenAI(model = "gpt-3.5-turbo", temperature=0.0, max_tokens=1000)

def process(state: SimpleBotState) -> SimpleBotState:
    """Process the messages in the state."""
    if not state["messages"]:
        return state
    response = llm.invoke(state["messages"])
    state["messages"].append(response)
    return state


graph = StateGraph(SimpleBotState)

graph.add_node("process" , process)

graph.add_edge(START, "process")
graph.add_edge("process", END)
agent =  graph.compile()

user_input = input("Enter your message: ")
while user_input != "exit":
    agent.invoke({"message":[HumanMessage(content=user_input)]})
    user_input = input("Enter your message: ")