from qdrant_client import QdrantClient,models
from langchain_openai import OpenAIEmbeddings
from app.core.config import settings
from typing import List
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from uuid import uuid4
class VectorStoreManager:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model=settings.EMBEDDING_MODEL)
        self.client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.create_collection_if_not_exists()

    def create_collection_if_not_exists(self):
        if not self.client.collection_exists(collection_name=self.collection_name):
            print(f"Creating Qdrant collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=settings.EMBEDDING_DIMENSION,
                    distance=models.Distance.COSINE,
                ),
            )
        else:
            print(f"Qdrant collection '{self.collection_name}' already exists.")
    def get_vectorstore(self):
        vectorstore = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings
        )
        return vectorstore

    def add_documents(self, documents: List[Document]):
        uuids = [str(uuid4()) for _ in range(len(documents))]
        return self.get_vectorstore().add_documents(documents=documents, ids=uuids)

    def get_retriever(self):
        vectorstore = self.get_vectorstore()
        return vectorstore.as_retriever(search_kwargs={"k": settings.TOP_K_CONTEXT})
