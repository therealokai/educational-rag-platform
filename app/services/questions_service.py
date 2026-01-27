from app.rag.vectorstore import VectorStoreManager
from app.agents.graph import create_graph
from typing import Dict, Any, List


class QuestionService:
    def __init__(self):
        self.vectorstore = VectorStoreManager()
        self.graph = create_graph()

    async def generate_questions(self, query: str, num_questions: int = 5) -> Dict[str, Any]:

        retriever = self.vectorstore.get_retriever()
        docs = retriever.invoke(query)
        context = "\n\n".join([doc.metadata.get("full_content", "") for doc in docs])

        initial_state = {
            "query": query,
            "context": context,
            "iterations": 0,
            "passed": False,
            "questions": [],  
            "evaluation": "",
            "target": num_questions,
            "valid_questions": []  
        }

        final_state = self.graph.invoke(initial_state)

        final_state.setdefault("valid_questions", [])
        return {
            "questions": final_state.get("valid_questions", []),
            "evaluation": final_state.get("evaluation", ""),
            "iterations": final_state.get("iterations", 0),
            "passed": final_state.get("passed", False),
        }
