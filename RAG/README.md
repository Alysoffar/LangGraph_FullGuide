# RAG Systems with LangGraph: Single-Agent vs Multi-Agent

This repository contains two implementations of Retrieval-Augmented Generation (RAG) systems using LangGraph:
1. **Single-Agent System** - Simple, fast implementation
2. **Multi-Agent System** - Advanced, specialized team-based approach

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Single-Agent System](#single-agent-system)
- [Multi-Agent System](#multi-agent-system)
- [Architecture Comparison](#architecture-comparison)
- [Usage Examples](#usage-examples)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Overview

### What is RAG?
**RAG (Retrieval-Augmented Generation)** combines document retrieval with AI generation to provide accurate, grounded answers based on your specific documents. Think of it as giving your AI assistant access to a smart filing cabinet.

### Why LangGraph?
**LangGraph** enables stateful, multi-step AI workflows where agents can use tools, make decisions, and collaborate to solve complex problems.

## Prerequisites

- Python 3.8+
- OpenAI API key
- PDF document(s) for analysis

## Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd rag-langgraph-systems

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

### Required Dependencies
```txt
python-dotenv
langgraph
langchain
langchain-openai
langchain-community
langchain-chroma
pypdf
chromadb
```

## Quick Start

1. **Place your PDF** in the project directory as `Stock_Market_Performance_2024.pdf`
2. **Set your OpenAI API key** in `.env` file
3. **Choose your system**:
   - Run `python single_agent_rag.py` for simple questions
   - Run `python multi_agent_rag.py` for complex analysis

---

## Single-Agent System

### Architecture
```
User Question → LLM → Search Tool → LLM → Answer
```

A single AI agent handles everything: understanding questions, searching documents, and generating answers.

### Code Structure
```python
# Core Components
llm = ChatOpenAI(model="gpt-4o", temperature=0)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Chroma.from_documents(...)
retriever = vectorstore.as_retriever()

# Simple workflow
def call_llm(state) -> response
def take_action(state) -> tool_results
def should_continue(state) -> True/False
```

### Key Features
- ✅ Simple implementation
- ✅ Fast for basic questions
- ✅ Easy to understand and debug
- ✅ Low resource usage
- ❌ Limited for complex queries
- ❌ No specialization

### Best For
- Simple document searches
- Quick fact lookups
- Straightforward Q&A
- Learning and prototyping

### Usage
```python
python single_agent_rag.py

# Example interaction:
> What is your question: How did Apple perform in 2024?
> Answer: Based on the Stock Market Performance 2024 document, Apple showed strong performance with 15% revenue growth...
```

---

## Multi-Agent System

### Architecture
```
User Question → Router → Researcher → Analyst → Synthesizer → Answer
```

Four specialized AI agents work as a team:
- **🎯 Router**: Decides which specialist should handle the query
- **🔍 Researcher**: Finds and gathers information from documents  
- **📊 Analyst**: Performs calculations, analysis, and insights
- **🔄 Synthesizer**: Creates comprehensive, professional answers

### Advanced Features
- ✅ Specialized expertise per agent
- ✅ Handles complex multi-step queries
- ✅ Transparent decision-making process
- ✅ Professional-quality outputs
- ✅ Easily extensible
- ❌ More complex setup
- ❌ Higher resource usage

### Agent Specifications

#### 🎯 Router Agent
```python
class RouterAgent:
    """Intelligent query routing to appropriate specialists"""
    
    # Routes queries based on patterns:
    # "What does document say..." → RESEARCHER
    # "Calculate percentage..." → ANALYST
    # "Compare A and B..." → RESEARCHER (needs data first)
    # "Summarize findings..." → SYNTHESIZER
```

#### 🔍 Researcher Agent  
```python
class ResearcherAgent:
    """Information gathering specialist"""
    
    Tools: [retriever_tool]
    Capabilities:
    - Multiple targeted searches
    - Systematic information gathering
    - Source citation and organization
    - Comprehensive coverage of topics
```

#### 📊 Analyst Agent
```python
class AnalystAgent:
    """Quantitative analysis specialist"""
    
    Tools: [calculator_tool, analysis_tool]
    Capabilities:
    - Mathematical calculations
    - Trend analysis and pattern identification
    - Data comparisons and metrics
    - Statistical insights
```

#### 🔄 Synthesizer Agent
```python
class SynthesizerAgent:
    """Professional report creation specialist"""
    
    Capabilities:
    - Combines research and analysis findings
    - Creates structured, comprehensive answers
    - Ensures completeness and clarity
    - Professional formatting with citations
```

### Workflow Example

**Query**: "Compare Apple and Google's 2024 performance and calculate growth rates"

```
1. 🎯 Router: "Complex comparison query" → Routes to RESEARCHER

2. 🔍 Researcher: 
   - Search 1: "Apple 2024 financial performance"
   - Search 2: "Google 2024 financial performance"  
   - Organizes: Structured findings with citations

3. 📊 Analyst:
   - Calculates: Apple growth rate = (Q4-Q1)/Q1 * 100
   - Calculates: Google growth rate = (Q4-Q1)/Q1 * 100
   - Compares: Revenue, profit, market metrics
   - Identifies: Key performance trends

4. 🔄 Synthesizer:
   - Creates: Executive summary
   - Includes: Quantitative comparisons
   - Provides: Investment insights
   - Cites: All sources properly
```

### State Management
```python
class MultiAgentState(TypedDict):
    messages: Sequence[BaseMessage]      # Conversation history
    current_agent: str                   # Active agent
    findings: dict                       # Agent discoveries
    final_answer: str                    # Complete response
    iteration_count: int                 # Loop prevention
```

---

## Architecture Comparison

| Feature | Single-Agent | Multi-Agent |
|---------|--------------|-------------|
| **Setup Complexity** | Simple | Advanced |
| **Answer Quality** | Good for simple queries | Excellent for all queries |
| **Speed** | Fast | Moderate (thorough) |
| **Specialization** | General purpose | Expert specialists |
| **Transparency** | Limited | Full visibility |
| **Complex Queries** | Struggles | Excels |
| **Extensibility** | Hard to extend | Easy to add agents |
| **Resource Usage** | Low | Higher |
| **Best Use Case** | Quick lookups | Professional analysis |

## Usage Examples

### Single-Agent Examples

**Simple Fact Lookup:**
```
Q: What was Apple's Q3 revenue?
A: According to the document, Apple's Q3 revenue was $89.5 billion.
```

**Basic Document Search:**
```
Q: What does the report say about tech stocks?
A: The report indicates that tech stocks showed strong performance...
```

### Multi-Agent Examples

**Complex Analysis:**
```
Q: Compare Apple and Microsoft's performance, calculate their growth rates, and recommend which is a better investment.

🎯 Router: Routes to RESEARCHER
🔍 Researcher: 
   - Searches Apple financial data
   - Searches Microsoft financial data
   - Gathers competitive analysis info
   
📊 Analyst:
   - Calculates Apple growth: 15.2%
   - Calculates Microsoft growth: 12.8%
   - Compares P/E ratios, market cap, margins
   - Performs risk analysis
   
🔄 Synthesizer:
   Creates comprehensive investment analysis with:
   - Executive summary
   - Quantitative comparison table
   - Risk assessment
   - Investment recommendation with rationale
   - Full source citations
```

**Multi-Step Research:**
```
Q: What are the key trends in renewable energy investments and how do they impact tech companies?

Multi-agent system:
1. Researches renewable energy trends
2. Researches tech company energy usage
3. Analyzes correlation patterns
4. Calculates impact metrics
5. Synthesizes comprehensive trend report
```

## Advanced Features

### Adding New Agents

```python
class ValidatorAgent:
    """Fact-checking specialist"""
    def __init__(self):
        self.llm = base_llm.bind_tools([fact_check_tool])
        self.system_prompt = "You validate information accuracy..."

# Add to workflow
graph.add_node("validator", validator_node)
graph.add_edge("synthesis", "validator")
```

### Custom Tools

```python
@tool
def web_search_tool(query: str) -> str:
    """Search current web information"""
    # Implementation here
    pass

@tool  
def chart_generator_tool(data: str, chart_type: str) -> str:
    """Generate visualization charts"""
    # Implementation here
    pass

# Bind to specific agents
analyst.llm = analyst.llm.bind_tools([calculator_tool, chart_generator_tool])
```

### Dynamic Workflows

```python
def intelligent_routing(state: MultiAgentState):
    """Dynamic routing based on query complexity"""
    query = state['messages'][-1].content
    
    if is_complex_analysis(query):
        return "research"
    elif needs_validation(query):
        return "validator"
    elif is_calculation_heavy(query):
        return "analyst"
    else:
        return "synthesis"
```

## File Structure

```
project/
├── single_agent_rag.py          # Simple RAG implementation
├── multi_agent_rag.py           # Advanced multi-agent system
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
├── Stock_Market_Performance_2024.pdf  # Your document
├── D:/WORK/LangGraph/RAG/       # ChromaDB storage (auto-created)
└── README.md                    # This file
```

## Configuration

### Environment Variables
```bash
# .env file
OPENAI_API_KEY=your_openai_api_key_here
PERSIST_DIRECTORY=D:/WORK/LangGraph/RAG  # Adjust path as needed
```

### System Settings
```python
# Model configuration
llm = ChatOpenAI(
    model="gpt-4o",         # Or "gpt-3.5-turbo" for faster/cheaper
    temperature=0           # 0 = deterministic, 0.7 = creative
)

# Embedding configuration  
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"  # Or "text-embedding-3-large"
)

# Retrieval settings
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}  # Number of document chunks to retrieve
)

# Text chunking
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # Characters per chunk
    chunk_overlap=200       # Overlap between chunks
)
```

## Troubleshooting

### Common Issues

**"PDF file not found"**
```python
# Solution: Check file path and name
pdf_path = "Stock_Market_Performance_2024.pdf"  # Must match exactly
if not os.path.exists(pdf_path):
    print(f"Looking for file at: {os.path.abspath(pdf_path)}")
```

**"OpenAI API key not found"**
```bash
# Solution: Check .env file
cat .env
# Should show: OPENAI_API_KEY=sk-...
```

**"ChromaDB creation failed"**
```python
# Solution: Check directory permissions
persist_directory = r"D:\WORK\LangGraph\RAG"  # Windows
# persist_directory = "/path/to/your/directory"  # Linux/Mac

# Ensure directory exists and is writable
if not os.path.exists(persist_directory):
    os.makedirs(persist_directory)
```

**"Empty search results"**
```python
# Solution: Check document content and query
docs = retriever.invoke("your query here")
print(f"Found {len(docs)} documents")
for i, doc in enumerate(docs):
    print(f"Doc {i}: {doc.page_content[:100]}...")
```

### Performance Optimization

**Speed up processing:**
```python
# Use smaller embedding model
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# Reduce chunk retrieval
search_kwargs={"k": 3}  # Instead of 5

# Use faster model for simple queries
llm = ChatOpenAI(model="gpt-3.5-turbo")
```

**Improve accuracy:**
```python
# Increase chunk retrieval
search_kwargs={"k": 8}

# Reduce chunk size for more precise matches
chunk_size=500, chunk_overlap=100

# Use more powerful model
llm = ChatOpenAI(model="gpt-4o")
```

## When to Use Which System

### Choose Single-Agent When:
- ✅ Simple document Q&A
- ✅ Quick prototyping
- ✅ Limited computational resources
- ✅ Learning RAG concepts
- ✅ Basic fact retrieval

### Choose Multi-Agent When:
- ✅ Complex analysis required
- ✅ Professional-quality outputs needed
- ✅ Multi-step reasoning necessary
- ✅ Transparency important
- ✅ Handling diverse query types
- ✅ Production applications

## Example Interactions

### Single-Agent Session
```
=== RAG AGENT===

What is your question: What was Apple's revenue growth in 2024?

Calling Tool: retriever_tool with query: Apple revenue growth 2024
Result length: 1247
Tools Execution Complete. Back to the model!

=== ANSWER ===
Based on the Stock Market Performance 2024 document, Apple achieved strong revenue growth in 2024. According to Document 1, Apple reported quarterly revenue of $89.5 billion, representing a 15% increase compared to the previous year. The growth was primarily driven by strong iPhone sales and expanding services revenue.
```

### Multi-Agent Session
```
🚀 === MULTI-AGENT RAG SYSTEM ===
Agents: Router → Researcher → Analyst → Synthesizer

❓ What would you like to know: Compare Apple and Google's 2024 performance and tell me which performed better

🎬 Processing: Compare Apple and Google's 2024 performance and tell me which performed better
==================================================
🎯 Router: Directing to RESEARCHER
🔍 RESEARCHER AGENT: Starting research...
🔍 Searching: Apple 2024 financial performance  
🔍 Searching: Google 2024 financial performance
🔍 Searching: Apple Google comparison 2024
📊 ANALYST AGENT: Starting analysis...
🧮 Calculating: 89.5 - 76.3
📈 Analyzing: comparison
🔄 SYNTHESIZER AGENT: Creating final answer...
==================================================

🎯 FINAL ANSWER:
==================================================

# Apple vs Google 2024 Performance Comparison

## Executive Summary
Apple significantly outperformed Google across key financial metrics in 2024, demonstrating superior revenue generation and growth momentum.

## Financial Performance Analysis

### Revenue Comparison
- **Apple**: $89.5 billion quarterly revenue
- **Google**: $76.3 billion quarterly revenue  
- **Difference**: $13.2 billion advantage to Apple (17.3% higher)

### Growth Rate Analysis
- **Apple**: 15% annual growth rate
- **Google**: 12% annual growth rate
- **Apple's advantage**: 3 percentage points higher growth

### Absolute Growth Impact
- **Apple's growth in dollars**: $13.4 billion
- **Google's growth in dollars**: $9.2 billion
- **Apple generated $4.2 billion more in absolute growth**

## Key Insights

1. **Market Leadership**: Apple maintains its position as the larger revenue generator
2. **Growth Momentum**: Apple's 15% growth rate exceeds Google's 12%, indicating stronger business acceleration
3. **Scale Advantage**: Apple's larger base combined with higher growth rate creates compounding advantages

## Conclusion
**Apple performed significantly better than Google in 2024.** With higher absolute revenue, superior growth rates, and greater dollar-value growth generation, Apple demonstrated stronger overall financial performance and market execution.

## Sources
Analysis based on Stock Market Performance 2024 document data, with quantitative calculations performed on reported financial metrics.
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Adding New Agents
```python
# Template for new agent
class YourCustomAgent:
    def __init__(self):
        self.llm = base_llm.bind_tools([your_tools])
        self.system_prompt = "Your agent's instructions..."
    
    def process(self, state: MultiAgentState) -> MultiAgentState:
        # Your agent's logic here
        return updated_state
```

### Adding New Tools
```python
@tool
def your_custom_tool(parameter: type) -> str:
    """Clear description of what this tool does."""
    # Tool implementation
    return result
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [LangGraph](https://langchain-ai.github.io/langgraph/) for workflow orchestration
- Uses [OpenAI](https://openai.com/) for language models and embeddings
- Document storage with [ChromaDB](https://www.trychroma.com/)
- PDF processing with [PyPDF](https://pypdf.readthedocs.io/)

---

## System Requirements

- **Memory**: 4GB+ RAM recommended
- **Storage**: 1GB+ for document embeddings
- **Python**: 3.8 or higher
- **API**: OpenAI API access required

## Support

For questions and support:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review [example interactions](#usage-examples)
3. Open an issue on GitHub
4. Consult [LangGraph documentation](https://langchain-ai.github.io/langgraph/)

---

**Happy RAG building! 🚀**