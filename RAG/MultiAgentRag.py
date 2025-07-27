from dotenv import load_dotenv
import os
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence, Literal
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, ToolMessage, AIMessage
from operator import add as add_messages
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.tools import tool
import json

load_dotenv()

# Base LLM configuration
base_llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Embedding model
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# PDF processing (same as before)
pdf_path = "Stock_Market_Performance_2024.pdf"

if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"PDF file not found: {pdf_path}")

pdf_loader = PyPDFLoader(pdf_path)
pages = pdf_loader.load()
print(f"PDF loaded with {len(pages)} pages")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
pages_split = text_splitter.split_documents(pages)

persist_directory = r"D:\WORK\LangGraph\RAG"
collection_name = "stock_market"

if not os.path.exists(persist_directory):
    os.makedirs(persist_directory)

vectorstore = Chroma.from_documents(
    documents=pages_split,
    embedding=embeddings,
    persist_directory=persist_directory,
    collection_name=collection_name
)

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

# =============================================================================
# TOOLS DEFINITION
# =============================================================================

@tool
def retriever_tool(query: str) -> str:
    """Searches the Stock Market Performance 2024 document for relevant information."""
    docs = retriever.invoke(query)
    if not docs:
        return "No relevant information found."
    
    results = []
    for i, doc in enumerate(docs):
        results.append(f"Document {i+1}:\n{doc.page_content}")
    return "\n\n".join(results)

@tool
def calculator_tool(expression: str) -> str:
    """Performs mathematical calculations. Use Python-style expressions."""
    try:
        # Safe evaluation of mathematical expressions
        result = eval(expression, {"__builtins__": {}}, {
            "abs": abs, "round": round, "min": min, "max": max,
            "sum": sum, "len": len, "pow": pow
        })
        return f"Result: {result}"
    except Exception as e:
        return f"Calculation error: {str(e)}"

@tool
def analysis_tool(data: str, analysis_type: str) -> str:
    """Performs analysis on data. Types: 'summary', 'trends', 'comparison', 'insights'."""
    analysis_prompts = {
        'summary': f"Provide a concise summary of this data:\n{data}",
        'trends': f"Identify key trends in this data:\n{data}",
        'comparison': f"Compare and contrast elements in this data:\n{data}",
        'insights': f"Provide key insights and implications from this data:\n{data}"
    }
    
    prompt = analysis_prompts.get(analysis_type, f"Analyze this data:\n{data}")
    
    # Simple analysis (in practice, you might use another LLM call here)
    return f"Analysis ({analysis_type}): {prompt[:500]}..."

# =============================================================================
# MULTI-AGENT STATE
# =============================================================================

class MultiAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    current_agent: str
    task_queue: list
    findings: dict
    final_answer: str
    iteration_count: int

# =============================================================================
# AGENT DEFINITIONS
# =============================================================================

class RouterAgent:
    """Decides which specialized agent should handle the query"""
    
    def __init__(self):
        self.llm = base_llm
        self.system_prompt = """
        You are a Router Agent that decides which specialized agent should handle a user query.
        
        Available agents:
        1. RESEARCHER: Searches documents, gathers information
        2. ANALYST: Performs analysis, calculations, comparisons
        3. SYNTHESIZER: Combines information and creates final answers
        
        Analyze the user query and decide which agent should handle it first.
        Respond with just the agent name: RESEARCHER, ANALYST, or SYNTHESIZER
        
        Examples:
        - "What does the document say about Apple?" → RESEARCHER
        - "Calculate the percentage change in revenue" → ANALYST  
        - "Compare Apple and Google performance" → RESEARCHER (need data first)
        - "Summarize all findings" → SYNTHESIZER
        """
    
    def route(self, query: str) -> str:
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"Route this query: {query}")
        ]
        response = self.llm.invoke(messages)
        agent = response.content.strip().upper()
        
        # Fallback to RESEARCHER if unclear
        if agent not in ["RESEARCHER", "ANALYST", "SYNTHESIZER"]:
            agent = "RESEARCHER"
            
        print(f"🎯 Router: Directing to {agent}")
        return agent

class ResearcherAgent:
    """Specialized in finding and retrieving information"""
    
    def __init__(self):
        self.llm = base_llm.bind_tools([retriever_tool])
        self.system_prompt = """
        You are a Research Agent specialized in finding information from documents.
        
        Your job:
        1. Use the retriever_tool to search for relevant information
        2. Make multiple searches if needed for comprehensive coverage
        3. Organize findings clearly
        4. Always cite your sources
        
        Be thorough and systematic in your research.
        """
    
    def research(self, state: MultiAgentState) -> MultiAgentState:
        print("🔍 RESEARCHER AGENT: Starting research...")
        
        messages = [SystemMessage(content=self.system_prompt)] + list(state['messages'])
        response = self.llm.invoke(messages)
        
        # Execute any tool calls
        new_messages = [response]
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                if tool_call['name'] == 'retriever_tool':
                    print(f"🔍 Searching: {tool_call['args']['query']}")
                    result = retriever_tool.invoke(tool_call['args']['query'])
                    tool_message = ToolMessage(
                        tool_call_id=tool_call['id'],
                        name=tool_call['name'],
                        content=result
                    )
                    new_messages.append(tool_message)
            
            # Get final response with tool results
            final_response = self.llm.invoke(
                [SystemMessage(content=self.system_prompt)] + 
                list(state['messages']) + new_messages
            )
            new_messages.append(final_response)
        
        # Store findings
        findings = state.get('findings', {})
        findings['research'] = new_messages[-1].content
        
        return {
            'messages': new_messages,
            'current_agent': 'ANALYST',  # Next agent
            'findings': findings
        }

class AnalystAgent:
    """Specialized in analysis, calculations, and insights"""
    
    def __init__(self):
        self.llm = base_llm.bind_tools([calculator_tool, analysis_tool])
        self.system_prompt = """
        You are an Analysis Agent specialized in data analysis and calculations.
        
        Your job:
        1. Analyze information provided by the Researcher
        2. Perform calculations when needed
        3. Identify trends, patterns, and insights
        4. Use analysis_tool for different types of analysis
        5. Provide quantitative insights
        
        Be analytical and precise in your work.
        """
    
    def analyze(self, state: MultiAgentState) -> MultiAgentState:
        print("📊 ANALYST AGENT: Starting analysis...")
        
        # Include research findings in context
        context = ""
        if 'research' in state.get('findings', {}):
            context = f"Research findings to analyze:\n{state['findings']['research']}\n\n"
        
        messages = [
            SystemMessage(content=self.system_prompt + "\n" + context)
        ] + list(state['messages'])
        
        response = self.llm.invoke(messages)
        
        # Execute any tool calls
        new_messages = [response]
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                if tool_call['name'] == 'calculator_tool':
                    print(f"🧮 Calculating: {tool_call['args']['expression']}")
                    result = calculator_tool.invoke(tool_call['args']['expression'])
                elif tool_call['name'] == 'analysis_tool':
                    print(f"📈 Analyzing: {tool_call['args']['analysis_type']}")
                    result = analysis_tool.invoke(tool_call['args']['data'], tool_call['args']['analysis_type'])
                else:
                    result = "Unknown tool"
                
                tool_message = ToolMessage(
                    tool_call_id=tool_call['id'],
                    name=tool_call['name'],
                    content=result
                )
                new_messages.append(tool_message)
            
            # Get final response with tool results
            final_response = self.llm.invoke(
                [SystemMessage(content=self.system_prompt + "\n" + context)] + 
                list(state['messages']) + new_messages
            )
            new_messages.append(final_response)
        
        # Store findings
        findings = state.get('findings', {})
        findings['analysis'] = new_messages[-1].content
        
        return {
            'messages': new_messages,
            'current_agent': 'SYNTHESIZER',  # Next agent
            'findings': findings
        }

class SynthesizerAgent:
    """Combines all findings into a comprehensive final answer"""
    
    def __init__(self):
        self.llm = base_llm
        self.system_prompt = """
        You are a Synthesizer Agent that creates comprehensive final answers.
        
        Your job:
        1. Review all findings from Researcher and Analyst agents
        2. Combine information into a coherent, comprehensive answer
        3. Ensure all key points are covered
        4. Provide proper citations and sources
        5. Structure the answer clearly and professionally
        
        Create a well-organized, complete response that addresses the original question.
        """
    
    def synthesize(self, state: MultiAgentState) -> MultiAgentState:
        print("🔄 SYNTHESIZER AGENT: Creating final answer...")
        
        # Combine all findings
        findings_context = ""
        findings = state.get('findings', {})
        
        if 'research' in findings:
            findings_context += f"RESEARCH FINDINGS:\n{findings['research']}\n\n"
        
        if 'analysis' in findings:
            findings_context += f"ANALYSIS FINDINGS:\n{findings['analysis']}\n\n"
        
        messages = [
            SystemMessage(content=self.system_prompt + "\n" + findings_context),
            HumanMessage(content="Please synthesize all findings into a comprehensive final answer.")
        ]
        
        response = self.llm.invoke(messages)
        
        return {
            'messages': [response],
            'current_agent': 'COMPLETE',
            'final_answer': response.content,
            'findings': findings
        }

# =============================================================================
# WORKFLOW NODES
# =============================================================================

# Initialize agents
router = RouterAgent()
researcher = ResearcherAgent()
analyst = AnalystAgent()
synthesizer = SynthesizerAgent()

def route_query(state: MultiAgentState) -> MultiAgentState:
    """Route the initial query to appropriate agent"""
    user_query = state['messages'][-1].content
    next_agent = router.route(user_query)
    
    return {
        'current_agent': next_agent,
        'iteration_count': state.get('iteration_count', 0) + 1
    }

def research_node(state: MultiAgentState) -> MultiAgentState:
    """Research agent node"""
    return researcher.research(state)

def analysis_node(state: MultiAgentState) -> MultiAgentState:
    """Analysis agent node"""
    return analyst.analyze(state)

def synthesis_node(state: MultiAgentState) -> MultiAgentState:
    """Synthesis agent node"""
    return synthesizer.synthesize(state)

def should_continue(state: MultiAgentState) -> Literal["research", "analysis", "synthesis", "end"]:
    """Determine next step in the workflow"""
    current_agent = state.get('current_agent', '')
    iteration_count = state.get('iteration_count', 0)
    
    # Safety check to prevent infinite loops
    if iteration_count > 10:
        return "end"
    
    if current_agent == 'RESEARCHER':
        return "research"
    elif current_agent == 'ANALYST':
        return "analysis"
    elif current_agent == 'SYNTHESIZER':
        return "synthesis"
    else:
        return "end"

# =============================================================================
# BUILD THE MULTI-AGENT GRAPH
# =============================================================================

def build_multiagent_graph():
    """Build the multi-agent workflow graph"""
    
    graph = StateGraph(MultiAgentState)
    
    # Add nodes
    graph.add_node("router", route_query)
    graph.add_node("research", research_node)
    graph.add_node("analysis", analysis_node)
    graph.add_node("synthesis", synthesis_node)
    
    # Set entry point
    graph.set_entry_point("router")
    
    # Add conditional edges from router
    graph.add_conditional_edges(
        "router",
        should_continue,
        {
            "research": "research",
            "analysis": "analysis", 
            "synthesis": "synthesis",
            "end": END
        }
    )
    
    # Add edges between agents
    graph.add_conditional_edges(
        "research",
        should_continue,
        {
            "analysis": "analysis",
            "synthesis": "synthesis", 
            "end": END
        }
    )
    
    graph.add_conditional_edges(
        "analysis", 
        should_continue,
        {
            "synthesis": "synthesis",
            "end": END
        }
    )
    
    graph.add_edge("synthesis", END)
    
    return graph.compile()

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def run_multiagent_system():
    """Run the multi-agent RAG system"""
    
    print("\n🚀 === MULTI-AGENT RAG SYSTEM ===")
    print("Agents: Router → Researcher → Analyst → Synthesizer")
    print("Type 'exit' or 'quit' to stop\n")
    
    multiagent_system = build_multiagent_graph()
    
    while True:
        user_input = input("\n❓ What would you like to know: ")
        if user_input.lower() in ['exit', 'quit']:
            break
        
        print(f"\n🎬 Processing: {user_input}")
        print("=" * 50)
        
        # Initialize state
        initial_state = {
            'messages': [HumanMessage(content=user_input)],
            'current_agent': '',
            'task_queue': [],
            'findings': {},
            'final_answer': '',
            'iteration_count': 0
        }
        
        try:
            # Run the multi-agent system
            result = multiagent_system.invoke(initial_state)
            
            print("\n" + "=" * 50)
            print("🎯 FINAL ANSWER:")
            print("=" * 50)
            
            if 'final_answer' in result and result['final_answer']:
                print(result['final_answer'])
            else:
                print("No answer generated. Please try a different question.")
                
            # Optional: Show agent findings
            show_details = input("\n🔍 Show agent details? (y/n): ").lower() == 'y'
            if show_details:
                findings = result.get('findings', {})
                for agent, finding in findings.items():
                    print(f"\n📋 {agent.upper()} FINDINGS:")
                    print("-" * 30)
                    print(finding)
                    
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("Please try again with a different question.")

if __name__ == "__main__":
    run_multiagent_system()