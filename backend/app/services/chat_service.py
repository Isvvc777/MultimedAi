import asyncio
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from app.config import settings

class ChatService:
    def __init__(self):
        # 1. Setup LLM
        if settings.openai_api_key:
            self.llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                api_key=settings.openai_api_key,
                streaming=True,
                temperature=0.7
            )
        else:
            self.llm = ChatOllama(
                base_url=settings.ollama_base_url,
                model="llama3.1",
                temperature=0.7
            )
            
        # 2. Setup Embeddings (runs locally, downloads model on first run)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # 3. Setup Qdrant
        self.qdrant_client = QdrantClient(url=settings.qdrant_url)
        self.collection_name = "reports_collection"
        
        # Ensure collection exists
        try:
            self.qdrant_client.get_collection(self.collection_name)
        except Exception:
            # Create collection if it doesn't exist
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
            
        self.vector_store = QdrantVectorStore(
            client=self.qdrant_client,
            collection_name=self.collection_name,
            embedding=self.embeddings
        )

    async def index_report(self, analysis_id: str, report_text: str):
        """
        Embeds and indexes the report in Qdrant.
        """
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_text(report_text)
        
        metadatas = [{"analysis_id": analysis_id} for _ in chunks]
        
        # Add to Qdrant asynchronously
        await self.vector_store.aadd_texts(texts=chunks, metadatas=metadatas)

    async def generate_chat_stream(self, analysis_id: str, message: str, history: list):
        """
        Retrieves context and streams the LLM response via async generator.
        """
        # 1. Retrieve top-3 chunks filtered by analysis_id
        # Qdrant Langchain wrapper supports dict filters
        docs = await self.vector_store.asimilarity_search(
            message, 
            k=3, 
            filter={"analysis_id": analysis_id}
        )
        context_text = "\n\n".join([d.page_content for d in docs])
        
        # 2. Build Prompt
        system_prompt = (
            "Tu es un assistant médical informatif. Rappelle toujours que "
            "tes réponses ne remplacent pas un avis médical professionnel.\n\n"
            "Contexte du rapport médical du patient:\n{context}"
        )
        
        messages = [SystemMessage(content=system_prompt.format(context=context_text))]
        
        # 3. Append History
        for msg in history:
            role = msg.get("role")
            content = msg.get("content")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
                
        # 4. Append Current Message
        messages.append(HumanMessage(content=message))
        
        # 5. Stream LLM Response
        async for chunk in self.llm.astream(messages):
            if chunk.content:
                yield chunk.content

_chat_service_instance = None

def get_chat_service() -> ChatService:
    global _chat_service_instance
    if _chat_service_instance is None:
        _chat_service_instance = ChatService()
    return _chat_service_instance
