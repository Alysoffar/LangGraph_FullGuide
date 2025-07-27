# LangGraph Chatbots Collection

A collection of increasingly sophisticated chatbot implementations using LangGraph and LangChain, demonstrating different architectural patterns and capabilities in conversational AI systems.

## Table of Contents

- [Overview](#overview)
- [Theoretical Foundation](#theoretical-foundation)
- [Architecture Patterns](#architecture-patterns)
- [Implementation Details](#implementation-details)
- [Setup and Installation](#setup-and-installation)
- [Usage Examples](#usage-examples)
- [Technical Analysis](#technical-analysis)
- [Troubleshooting](#troubleshooting)

## Overview

This repository contains four distinct chatbot implementations that showcase the progression from simple stateless interactions to complex agent-based systems with memory, tools, and document management capabilities:

1. **SimpleBot.py** - Basic stateless chatbot
2. **ChatBotIncludingMemory.py** - Conversational memory implementation
3. **ReactAgent.py** - Tool-enabled reactive agent
4. **Drafter.py** - Document management agent with persistent state

## Theoretical Foundation

### Graph-Based Conversation Management

LangGraph implements conversations as **state graphs**, where each node represents a processing step and edges define the flow of conversation. This approach provides several advantages:

- **Deterministic Flow Control**: Conversations follow predictable paths
- **State Management**: Explicit handling of conversation context
- **Modularity**: Individual components can be modified independently
- **Debugging**: Clear visualization of conversation flow

### Message-Centric Architecture

All implementations use LangChain's message abstraction:

```python
# Core message types
HumanMessage    # User input
AIMessage       # AI responses  
SystemMessage   # System instructions
ToolMessage     # Tool execution results
```

This abstraction enables:
- **Standardized Communication**: Consistent interface across different AI models
- **Conversation History**: Natural tracking of multi-turn interactions
- **Tool Integration**: Seamless incorporation of external functions

### State Management Patterns

Each bot implements a different state management strategy:

- **Stateless**: No persistence between interactions
- **Session Memory**: In-memory conversation history
- **Functional State**: State transformed through pure functions
- **Persistent State**: Global variables with file I/O

## Architecture Patterns

### 1. Linear Processing (SimpleBot)

```
START → Process → END
```

**Characteristics:**
- Single processing node
- No memory between requests
- Immediate response pattern
- Suitable for FAQ-style interactions

### 2. Memory-Enhanced Linear (ChatBotIncludingMemory)

```
START → Process (with history) → END
```

**Characteristics:**
- Conversation history accumulation
- Context-aware responses
- Session-based memory
- Logging capabilities

### 3. Reactive Agent Pattern (ReactAgent)

```
START → Agent → Decision → [Tools|END]
           ↑              ↓
           └── Tool Results ←
```

**Characteristics:**
- Dynamic decision making
- Tool invocation based on need
- ReAct (Reasoning + Acting) paradigm
- Conditional flow control

### 4. Stateful Document Agent (Drafter)

```
START → Agent → Tools → Decision → [Agent|END]
                  ↓
            [Update|Save]
```

**Characteristics:**
- Persistent document state
- Specialized tool ecosystem
- Multi-step workflows
- File system integration

## Implementation Details

### SimpleBot.py

**Purpose**: Demonstrates basic LangGraph structure

**Key Components**:
- `SimpleBotState`: TypedDict defining message structure
- `process()`: Single processing function
- Linear graph with START→process→END flow

**Limitations**:
- No conversation memory
- Single-turn interactions only
- No error handling for malformed input

### ChatBotIncludingMemory.py

**Purpose**: Adds conversation memory and logging

**Key Features**:
- **Conversation History**: Maintains full session context
- **Response Logging**: Console output for debugging
- **File Persistence**: Saves conversation to `logging.txt`
- **Exit Handling**: Graceful termination with "exit" command

**Memory Management**:
```python
conversation_history = []  # Global session storage
# Messages accumulated: [Human, AI, Human, AI, ...]
```

**Note**: File writing bug present - opens in read mode instead of write mode.

### ReactAgent.py

**Purpose**: Implements ReAct (Reasoning + Acting) pattern

**Key Features**:
- **Tool Binding**: Mathematical operations (add, subtract, multiply)
- **Conditional Execution**: Tools called only when needed
- **Decision Logic**: `should_continue()` determines flow
- **Reactive Processing**: Responds to tool requirements dynamically

**ReAct Cycle**:
1. **Reasoning**: Analyze user query
2. **Acting**: Call appropriate tools if needed
3. **Observing**: Process tool results  
4. **Response**: Generate final answer

**Bugs Present**:
- `mult` function implements addition instead of multiplication
- Model string has extra space: `"gpt -4o"`
- Typo in `set_entery_point()` should be `set_entry_point()`
- Incorrect message initialization in main loop

### Drafter.py

**Purpose**: Document management with persistent state

**Key Features**:
- **Global Document State**: `document_content` variable
- **Specialized Tools**: `update()` and `save()` functions
- **File Operations**: Automatic `.txt` extension handling
- **Workflow Control**: Terminates after successful save
- **Interactive Loop**: Continuous user interaction until save

**Tool Functions**:
- `update(content: str)`: Replaces entire document content
- `save(filename: str)`: Writes to file and terminates session

**State Flow**:
```python
# Document lifecycle
"" → update(content) → save(filename) → file.txt
```

## Setup and Installation

### Prerequisites

```bash
pip install langchain-core
pip install langchain-openai
pip install langgraph
pip install python-dotenv
```

### Environment Configuration

Create `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### File Structure
```
project/
├── .env
├── SimpleBot.py
├── ChatBotIncludingMemory.py
├── ReactAgent.py
├── Drafter.py
└── README.md
```

## Usage Examples

### SimpleBot
```bash
python SimpleBot.py
# Single-turn conversations, no memory
```

### Memory Bot
```bash
python ChatBotIncludingMemory.py
# Multi-turn with history, type 'exit' to quit
```

### React Agent
```bash
python ReactAgent.py
# Ask mathematical questions like "What is 15 + 23?"
```

### Drafter
```bash
python Drafter.py
# Interactive document creation and editing
```

## Technical Analysis

### Performance Considerations

- **Token Usage**: Memory bots consume more tokens due to history
- **Latency**: Tool-enabled agents have additional API calls
- **Memory**: Global state in Drafter may cause issues in concurrent usage

### Security Implications

- **API Key Exposure**: Ensure `.env` files are not committed
- **File Operations**: Drafter has unrestricted file write access
- **Input Validation**: Limited sanitization of user inputs

### Scalability Factors

- **Session Management**: Current implementations use global state
- **Concurrent Users**: Not designed for multi-user scenarios  
- **Resource Management**: No cleanup of conversation histories

### Error Handling Gaps

- **Network Failures**: No retry mechanisms for API calls
- **Invalid Inputs**: Limited input validation and error recovery
- **File I/O Errors**: Basic exception handling in Drafter only

## Advanced Concepts

### State Graph Theory

LangGraph implements **Finite State Machines** with:
- **States**: Conversation contexts (TypedDict definitions)
- **Transitions**: Edge functions determining next states
- **Actions**: Node functions that transform state
- **Termination**: END state for conversation completion

### Message Passing Semantics

The `add_messages` annotation implements **message accumulation**:
```python
Annotated[Sequence[BaseMessage], add_messages]
# Automatically concatenates new messages to existing sequence
```

### Tool Integration Patterns

Tools follow the **Function Calling** paradigm:
1. **Declaration**: `@tool` decorator with type hints
2. **Binding**: `model.bind_tools(tools)` for LLM awareness  
3. **Invocation**: Automatic based on user intent
4. **Response**: ToolMessage with execution results

## Troubleshooting

### Common Issues

**Import Errors**:
```bash
# Solution: Install missing packages
pip install -r requirements.txt
```

**API Authentication**:
```bash
# Solution: Check .env file exists and contains valid key
export OPENAI_API_KEY=your_key_here
```

**File Permission Errors**:
```bash
# Solution: Ensure write permissions in current directory
chmod 755 .
```

### Debugging Tips

1. **Enable Verbose Logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **State Inspection**:
```python
print(f"Current state: {state}")
```

3. **Message Tracing**:
```python
for msg in state["messages"]:
    print(f"{type(msg).__name__}: {msg.content}")
```

## Future Enhancements

### Suggested Improvements

1. **Error Recovery**: Implement robust exception handling
2. **Session Management**: Add user session isolation
3. **Tool Validation**: Input sanitization for tool functions
4. **Async Support**: Non-blocking operations for better performance
5. **Configuration**: External config files for model parameters
6. **Testing**: Unit tests for each component
7. **Monitoring**: Conversation analytics and performance metrics

### Advanced Features

- **Multi-Agent Collaboration**: Agent-to-agent communication
- **Dynamic Tool Loading**: Runtime tool registration
- **Custom Memory Backends**: Database-backed conversation storage
- **Streaming Responses**: Real-time response generation
- **Context Compression**: Automatic summarization of long conversations

---

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## Support

For issues and questions:
- Create GitHub issue
- Check documentation at [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- Review LangChain documentation for message handling