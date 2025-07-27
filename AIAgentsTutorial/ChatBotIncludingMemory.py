from typing import TypedDict , List, Union
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START,END
from dotenv import load_dotenv
#Human Messages and AI messages are data types are used to store the messages exchanged between the user and the AI in a chat session.


load_dotenv()

class MemoryBotState(TypedDict):
    messages: List[Union[HumanMessage, AIMessage]]

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0, max_tokens=1000)

def process(state: MemoryBotState) -> MemoryBotState:
    """Process the messages in the state."""
    if not state["messages"]:
        return state
    response = llm.invoke(state["messages"])
    state["messages"].append(AIMessage(content=response.content))
    print("\nAI Response:", {response.content})  # Print the AI's response to the console
    return state

graph = StateGraph(MemoryBotState)
graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)
agent = graph.compile()

conversation_history = []

user_input = input("Enter your message: ")

while user_input.lower() != "exit":

    conversation_history.append(HumanMessage(content=user_input))
    agent.invoke({"messages": conversation_history})
    user_input = input("Enter your message: ")
    if user_input.lower() == "exit":
        break
    conversation_history.append(AIMessage(content=agent.state["messages"][-1].content))  # Append the AI's response to the history

with open("logging.txt", "r") as file:
    file.write("Your convo history:\n")

    for message in conversation_history:
        if isinstance(message, HumanMessage):
            file.write(f"User: {message.content}\n")
        elif isinstance(message, AIMessage):
            file.write(f"AI: {message.content}\n")
    file.write("\nEnd of conversation history.\n")
