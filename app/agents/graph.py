from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from app.services.llm_service import LLMService

class AgentState(TypedDict):
    query: str
    context: str
    questions: str
    evaluation: str
    iterations: int
    passed: bool

class QuestionAgents:
    def __init__(self):
        self.llm_service = LLMService()
        self.llm = self.llm_service.get_agent_llm()

    def generator_node(self, state: AgentState):
        context = state["context"]
        query = state["query"]
        print(f"context: {context}")
        prompt = f"""You are an expert educator. Based on the following context, generate 3 Multiple Choice Questions (MCQs) and 2 Fill-in-the-blank questions.
        
        Context: {context}
        Topic/Query: {query}
        
        Format each question clearly with options and the correct answer.
        """
        response = self.llm.invoke([
            SystemMessage(content="You generate high-quality assessment questions based on provided context."),
            HumanMessage(content=prompt)
        ])
        return {
            "questions": response.content,
            "iterations": state.get("iterations", 0) + 1
        }

    def evaluator_node(self, state: AgentState):
        questions = state["questions"]
        context = state["context"]
        prompt = f"""Evaluate the following questions for accuracy against the context and pedagogical quality. 
        
        Context: {context}
        Questions: {questions}
        
        If the questions are accurate and high quality, start your response with 'PASSED'. 
        Otherwise, provide specific feedback for improvement.
        """
        response = self.llm.invoke([
            SystemMessage(content="You are a strict quality controller for educational content."),
            HumanMessage(content=prompt)
        ])
        passed = response.content.strip().startswith("PASSED")
        return {
            "evaluation": response.content,
            "passed": passed
        }

def should_continue(state: AgentState):
    if state["passed"] or state["iterations"] >= 3:
        return END
    return "generator"

def create_graph():
    agents = QuestionAgents()
    workflow = StateGraph(AgentState)
    
    workflow.add_node("generator", agents.generator_node)
    workflow.add_node("evaluator", agents.evaluator_node)
    
    workflow.set_entry_point("generator")
    workflow.add_edge("generator", "evaluator")
    workflow.add_conditional_edges("evaluator", should_continue)
    
    return workflow.compile()
