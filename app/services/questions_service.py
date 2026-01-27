from app.rag.vectorstore import VectorStoreManager
from app.agents.graph import create_graph
from typing import Dict, Any

class QuestionService:
    def __init__(self):
        self.vectorstore = VectorStoreManager()
        self.graph = create_graph()

    async def generate_questions(self, query: str) -> Dict[str, Any]:
        retriever = self.vectorstore.get_retriever()
        docs = retriever.invoke(query)
        context = "\n\n".join([doc.metadata.get("full_content", "") for doc in docs])
        
        initial_state = {
            "query": query,
            "context": context,
            "iterations": 0,
            "passed": False,
            "questions": "",
            "evaluation": ""
        }
        
        final_state = self.graph.invoke(initial_state)
        return final_state
