from typing import TypedDict, List, Dict, Any
import json
from utils.helpers import safe_load_json
from utils.prompts import MCQ_GENERATOR_PROMPT, EVALUATOR_PROMPT
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from app.services.llm_service import LLMService


class AgentState(TypedDict):
    query: str
    context: str
    questions: List[str]
    evaluation: str
    iterations: int
    passed: bool
    target: int
    valid_questions: List[str]

class QuestionAgents:
    def __init__(self):
        self.llm_service = LLMService()
        self.llm = self.llm_service.get_agent_llm()
    def _extract_json_list(self, text: str) -> List[str]:
        parsed = safe_load_json(text)
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, dict):
            for v in parsed.values():
                if isinstance(v, list):
                    return v
        items = [line.strip() for line in text.split("\n\n") if line.strip()]
        return items

    def generator_node(self, state: AgentState):
        context = state["context"]
        query = state["query"]
        target = state.get("target", 1)
        valid = state.get("valid_questions", []) or []
        remaining = max(0, target - len(valid))
        if remaining <= 0:
            return {
                "questions": [],
                "iterations": state.get("iterations", 0)
            }
        print(f"Generating {remaining} questions. Context length: {len(context)}")
        # format the centralized generator prompt
        prompt = MCQ_GENERATOR_PROMPT.format(remaining=remaining, context=context, query=query)
        response = self.llm.invoke([
            SystemMessage(content="You generate high-quality MCQ assessment questions based on provided context."),
            HumanMessage(content=prompt)
        ])

        questions = self._extract_json_list(response.content)
        return {
            "questions": questions,
            "iterations": state.get("iterations", 0) + 1
        }

    def evaluator_node(self, state: AgentState):
        questions = state.get("questions", []) or []
        context = state["context"]
        target = state.get("target", 1)
        valid_acc = state.get("valid_questions", []) or []

        # format the centralized evaluator prompt
        prompt = EVALUATOR_PROMPT.format(context=context, questions_json=json.dumps(questions))
        response = self.llm.invoke([
            SystemMessage(content="You are a strict quality controller for educational content."),
            HumanMessage(content=prompt)
        ])

        passed_questions = []
        evaluation_text = response.content
        parsed = safe_load_json(response.content)
        if isinstance(parsed, dict):
            passed_questions = parsed.get("passed_questions", []) or []
            evaluation_text = parsed.get("evaluation", response.content)
        elif isinstance(parsed, list):
            passed_questions = parsed
        else:
            if response.content.strip().startswith("PASSED"):
                passed_questions = questions

        new_added = []
        for q in passed_questions:
            if q not in valid_acc:
                valid_acc.append(q)
                new_added.append(q)

        passed_flag = len(valid_acc) >= target

        return {
            "evaluation": evaluation_text,
            "passed": passed_flag,
            "valid_questions": valid_acc,
            "questions": [],
            "iterations": state.get("iterations", 0)
        }

def should_continue(state: AgentState):
    target = state.get("target", 1)
    valid = state.get("valid_questions", []) or []
    iterations = state.get("iterations", 0)
    MAX_ITER = 10
    if len(valid) >= target or iterations >= MAX_ITER:
        state["passed"] = len(valid) >= target
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
