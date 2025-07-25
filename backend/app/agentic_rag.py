import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool, BaseTool
from langchain_community.llms import Together
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents.agent_types import AgentType
from langchain.agents.initialize import initialize_agent
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools.base import BaseTool
from pydantic import BaseModel, Field

from vector_store import hybrid_search, doc_metadata
from dotenv import load_dotenv

load_dotenv()


class DocumentSearchTool(BaseTool):
    name: str="document_search"
    description: str = "Search through uploaded documents using semantic similarity. Use this when you need to find specific information from the document database."

    def _run(self,query:str,run_manager:Optional[CallbackManagerForToolRun]=None)->str:
        try:
            docs = hybrid_search(query, top_k=5)
            if not docs:
                return "No relevant documents found for this query."
            
            results = []
            for i, doc in enumerate(docs[:3]):  # Limit to top 3 for conciseness
                results.append(f"Document {i+1}:\n{doc['text'][:500]}...")
            
            return "\n\n".join(results)
        except Exception as e:
            return f"Error searching documents: {str(e)}"

class DocumentMetadataSearchTool(BaseTool):
    name: str = "document_metadata_search"
    description: str = "Search documents by metadata like document type, filename, or creation date. Use when you need to filter documents by specific criteria."
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            # Parse query for metadata filters
            results = []
            for doc in doc_metadata:
                metadata = doc.get('metadata', {})
                if query.lower() in str(metadata).lower():
                    results.append(f"File: {metadata.get('filename', 'Unknown')}, Type: {metadata.get('doc_type', 'Unknown')}\nContent: {doc['text'][:300]}...")
            
            if not results:
                return f"No documents found matching metadata criteria: {query}"
            
            return "\n\n".join(results[:3]) 
        except Exception as e:
            return f"Error searching document metadata: {str(e)}"
        


class AgenticRAG:
    def __init__(self):
        self.llm = Together(
            model="mistralai/Mistral-7B-Instruct-v0.1",
            temperature=0.1,
            max_tokens=1024
        )
        
        self.memory = ConversationBufferWindowMemory(
            k=5,
            memory_key="chat_history",
            return_messages=True
        )

        self.tools=self._intialize_tools()

        self.agent=self._initialize_agent()

    def _intialize_tools(self)-> List[BaseTool]:
        """Initialize all available tools for the agent"""
        return [
            DocumentSearchTool(),
            DocumentMetadataSearchTool()
        ]
    
    def _initialize_agent(self):
        """Initialize the ReAct agent with tools and memory."""
        
        agent_prompt = PromptTemplate(
            input_variables=["tools", "tool_names", "input", "agent_scratchpad", "chat_history"],
            template="""You are an intelligent document assistant with access to various tools. Your goal is to provide accurate, helpful answers based on the uploaded documents.

Available tools:
{tools}

Tool names: {tool_names}

Previous conversation:
{chat_history}

Use the following format:

Question: the input question you must answer
Thought: think about what you need to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Important guidelines:
1. Always search for relevant documents first before answering
2. If the initial search doesn't provide enough information, try different search terms or use metadata search
3. For complex questions, use the query planner to break them down
4. Cite specific information from documents when possible
5. If you can't find information in the documents, clearly state that

Question: {input}
{agent_scratchpad}"""
        )

        agent =create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=agent_prompt
        )

        # Create agent executor with memory
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
            early_stopping_method="generate"
        )
    

    def query(self,question:str)-> Dict[str,Any]:
        """
        Process a query using the agentic RAG system.
        
        Args:
            question: User's question
            
        Returns:
            Dictionary containing the answer and metadata
        """

        try:
            query_type=self._classify_query(question)

            response=self.agent.agent.invoke({
                "input":question,
                "chat_history":self.memory.chat_memory.messages
            })

            return {
                "answer": response["output"],
                "query_type":query_type,
                "timestamp":datetime.now().isoformat(),
                "success":True
            }
        
        except Exception as e:
            logging.error(f"Error in agentic RAG query: {str(e)}")
            return{
                "answer": f"I encountered an error while processing your question: {str(e)}",
                "query_type": "error",
                "timestamp": datetime.now().isoformat(),
                "success": False
            }
        
    def _classify_query(self, question: str) -> str:
        """Classify the type of query to route appropriately."""
        question_lower = question.lower()

        if any(word in question_lower for word in ["what documents", "what files", "summary", "overview"]):
            return "document_overview"
        elif any(word in question_lower for word in ["compare", "difference", "versus", "vs"]):
                return "comparison"
        elif any(word in question_lower for word in ["calculate", "compute", "math", "number"]):
                return "calculation"
        elif len(question.split())>15:
            return "complex"
        else:
            return "simple"
        

    def clear_memory(self):
        """Clear conversation memory."""
        self.memory.clear()


    def get_conversation_history(self)-> List[Dict]:
        """Get the conversation history."""
        return [
            {"role": "human" if i % 2 == 0 else "assistant", "content": msg.content}
            for i, msg in enumerate(self.memory.chat_memory.messages)
        ]


class QueryRouter:
    def __init__(self, agentic_rag: AgenticRAG):
        self.agentic_rag = agentic_rag
        self.llm = Together(model="mistralai/Mistral-7B-Instruct-v0.1", temperature=0.1)
    
    def route_query(self, question: str) -> Dict[str, Any]:
        """
        Route queries to appropriate handling strategies.
        """
        # Determine if query needs agentic approach
        if self._needs_agentic_approach(question):
            return self.agentic_rag.query(question)
        else:
            # Use simple RAG for straightforward queries
            return self._simple_rag_query(question)
    
    def _needs_agentic_approach(self, question: str) -> bool:
        """Determine if a query needs the full agentic approach."""
        indicators = [
            len(question.split()) > 10,  # Complex questions
            any(word in question.lower() for word in ["compare", "analyze", "explain why", "how does", "what if"]),
            "?" in question and len(question.split("?")) > 2,  # Multiple questions
        ]
        return any(indicators)
    
    def _simple_rag_query(self, question: str) -> Dict[str, Any]:
        """Handle simple queries with traditional RAG."""
        try:
            docs = hybrid_search(question, top_k=3)
            if not docs:
                return {
                    "answer": "I couldn't find relevant information in the uploaded documents.",
                    "query_type": "simple",
                    "success": False
                }
            
            context = "\n\n".join([doc["text"] for doc in docs])
            
            prompt = f"""Based on the following context, answer the question concisely:

Context:
{context}

Question: {question}

Answer:"""
            
            response = self.llm(prompt)
            
            return {
                "answer": response,
                "query_type": "simple",
                "success": True,
                "sources": len(docs)
            }
            
        except Exception as e:
            return {
                "answer": f"Error processing query: {str(e)}",
                "query_type": "simple",
                "success": False
            }

# Self-Reflection and Correction Component
class SelfReflection:
    def __init__(self, llm):
        self.llm = llm
    
    def evaluate_answer(self, question: str, answer: str, context: str) -> Dict[str, Any]:
        """Evaluate if the answer is good and suggest improvements."""
        
        evaluation_prompt = f"""
        Evaluate this question-answer pair:
        
        Question: {question}
        Answer: {answer}
        Available Context: {context[:500]}...
        
        Rate the answer on:
        1. Accuracy (1-5): Does it correctly use the context?
        2. Completeness (1-5): Does it fully answer the question?
        3. Relevance (1-5): Is it relevant to the question?
        
        Provide scores and brief reasoning:
        """
        
        evaluation = self.llm(evaluation_prompt)
        
        # Simple parsing of evaluation (in production, use structured output)
        return {
            "evaluation": evaluation,
            "needs_improvement": "1" in evaluation or "2" in evaluation
        }

# Initialize the agentic RAG system
def create_agentic_rag_system():
    """Factory function to create the complete agentic RAG system."""
    agentic_rag = AgenticRAG()
    query_router = QueryRouter(agentic_rag)
    
    return {
        "agentic_rag": agentic_rag,
        "query_router": query_router,
        "reflection": SelfReflection(agentic_rag.llm)
    }


if __name__ == "__main__":
    # Initialize system
    system = create_agentic_rag_system()
    router = system["query_router"]
    
    # Example queries
    test_queries = [
        "What documents do I have?",
        "Compare the main points between document A and document B",
        "Explain the process described in the technical manual and how it relates to safety protocols"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = router.route_query(query)
        print(f"Answer: {result['answer']}")
        print(f"Query Type: {result['query_type']}")
        print("-" * 50)