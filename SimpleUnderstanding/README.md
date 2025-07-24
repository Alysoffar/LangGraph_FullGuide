# Mastering LangGraph: From Basics to Advanced Applications


Welcome to this collection of hands-on examples designed to take you from a beginner to a confident user of LangGraph. This repository breaks down the core concepts of LangGraph through a series of progressively complex Jupyter notebooks. Whether you're building a simple sequential chain or a complex, stateful multi-agent system, these examples will provide a solid foundation.

## 📋 Table of Contents

- [Mastering LangGraph: From Basics to Advanced Applications](#mastering-langgraph-from-basics-to-advanced-applications)
  - [📋 Table of Contents](#-table-of-contents)
  - [🧠 What is LangGraph and Why Use It?](#-what-is-langgraph-and-why-use-it)
  - [🏛️ Core Concepts of LangGraph](#️-core-concepts-of-langgraph)
    - [1. The State (StateGraph)](#1-the-state-stategraph)
    - [2. Nodes: The Workers](#2-nodes-the-workers)
    - [3. Edges: The Pathways](#3-edges-the-pathways)
  - [🚀 Getting Started](#-getting-started)
  - [📚 Notebook Examples](#-notebook-examples)
    - [1. Hello\_World.ipynb \& Compliment.ipynb](#1-hello_worldipynb--complimentipynb)
    - [2. Multiple\_Input\_graph.ipynb \& Simple\_Calc.ipynb](#2-multiple_input_graphipynb--simple_calcipynb)
    - [3. SequentioalGraph.ipynb](#3-sequentioalgraphipynb)
    - [4. Conditional\_Graph.ipynb](#4-conditional_graphipynb)
    - [5. More\_complex\_conditional.ipynb](#5-more_complex_conditionalipynb)
    - [6. Looping.ipynb](#6-loopingipynb)
    - [7. Guessing\_Game.ipynb](#7-guessing_gameipynb)

## 🧠 What is LangGraph and Why Use It?

LangGraph is a library built on top of LangChain that allows you to build robust, stateful applications with Large Language Models (LLMs) using a graph-based structure.

While LangChain's Expression Language (LCEL) is excellent for creating linear chains (prompt | llm | parser), many real-world applications require more complex logic:

- **Cycles and Loops**: The ability to repeat a step until a condition is met (e.g., an agent reflecting on its work).
- **Conditional Branching**: Making decisions and taking different paths based on the output of a previous step.
- **State Management**: Maintaining a shared "memory" or "scratchpad" that multiple agents or tools can read from and write to.
- **Human-in-the-Loop**: Pausing the execution to wait for human input or approval.

LangGraph addresses these needs by letting you define your application as a state machine or a "graph" of computation.

## 🏛️ Core Concepts of LangGraph

Understanding these three components is key to mastering LangGraph.

### 1. The State (StateGraph)

The State is the heart and memory of your LangGraph application. It's a central object that is passed between all the nodes in your graph.

- **Definition**: You define the state's structure using a Python TypedDict. This provides type hints and makes your code more readable and maintainable.
- **Function**: As the graph executes, each node can read from the state and update it. The state persists and evolves throughout the entire workflow.
- **Analogy**: Think of the state as a shared whiteboard. Each "worker" (node) comes to the board, reads what's there, adds their own notes or erases something, and then leaves it for the next worker.

```python
from typing import TypedDict, List

class AgentState(TypedDict):
    # The state can contain any type of data
    name: str
    values: List[int]
    result: str
```

### 2. Nodes: The Workers

Nodes are the computational units of the graph. They are the "doers" that perform the actual work.

- **Definition**: A node is simply a Python function or a LangChain Runnable.
- **Signature**: Each node function accepts the current state as its only argument and returns a dictionary containing the values to update in the state. LangGraph automatically merges this dictionary back into the main state.

```python
# A simple node that modifies the state
def greeting_node(state: AgentState) -> AgentState:
    """A node that creates a greeting message."""
    state['result'] = f"Hello {state['name']}!"
    return state
```

### 3. Edges: The Pathways

Edges define the connections and flow of control between the nodes. They are the "roads" that direct the execution from one worker to the next.

- **set_entry_point(node_name)**: This special edge specifies which node should run first.
- **add_edge(start_node, end_node)**: This creates a simple, unconditional edge. After start_node finishes, end_node will always run next.
- **add_conditional_edges(...)**: This is where the real power of LangGraph shines. It allows for branching and decision-making. You provide:
  - A source node whose output will be used for the decision.
  - A condition function that takes the current state and returns a string, which represents the "path" to take.
  - A dictionary that maps the path strings to their corresponding destination nodes.
- **set_finish_point(node_name)**: This defines a terminal node. When execution reaches this node, the graph run is considered complete.

## 🚀 Getting Started

To run these examples, you first need to install the necessary libraries.

```bash
# Install langgraph
pip install langgraph

# You will also need jupyter to run the notebooks
pip install jupyter
```

Then, clone this repository and launch Jupyter Notebook to explore the examples.

## 📚 Notebook Examples

The notebooks are numbered to guide you from basic to advanced concepts.

### 1. Hello_World.ipynb & Compliment.ipynb

- **Concept**: The absolute basics of a single-node graph.
- **Description**: These notebooks demonstrate how to define a StateGraph, add a single node, set the entry and finish points, and compile() the graph into a runnable application. The invoke() method is used to run the graph.

### 2. Multiple_Input_graph.ipynb & Simple_Calc.ipynb

- **Concept**: Handling multiple inputs and performing operations.
- **Description**: These examples show how the state TypedDict can be used to pass complex data (like a list of numbers and an operation string) into the graph. The Simple_Calc notebook demonstrates performing different calculations within a single node based on the state.

### 3. SequentioalGraph.ipynb

- **Concept**: Creating a linear, multi-step workflow.
- **Description**: This notebook introduces the add_edge() method to chain multiple nodes together in a specific sequence (A -> B -> C). This is the foundation for building more complex chains.


### 4. Conditional_Graph.ipynb

- **Concept**: Branching logic with add_conditional_edges.
- **Description**: This is a key example that shows how to create a graph that makes decisions. A "decide" node routes the execution to either an "adder" or "subtractor" node based on an operation key in the state.


### 5. More_complex_conditional.ipynb

- **Concept**: Chaining multiple conditional branches.
- **Description**: This extends the previous example by showing a workflow with multiple decision points. The graph first decides on one operation, executes it, and then moves to a second decision node to perform another operation.


### 6. Looping.ipynb

- **Concept**: Creating cycles and iterative processes.
- **Description**: This notebook demonstrates how to create loops. A conditional edge is used to either route the execution back to a previous node (continuing the loop) or to the END (exiting the loop). This is essential for agentic behaviors like reflection or retrying a failed task.


### 7. Guessing_Game.ipynb

- **Concept**: A practical application combining all concepts.
- **Description**: This capstone notebook brings everything together to create a fun, interactive number guessing game. It uses:
  - A setup node to initialize the game state.
  - An I/O node to get user input.
  - Conditional logic to check if the guess is too high, too low, or correct.
  - Looping to allow the user to keep guessing until they win or run out of tries.


Happy graphing! 🔗