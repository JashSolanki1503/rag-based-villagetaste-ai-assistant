# ==========================================
# Import Necessary Modules
# ==========================================
from ingestion.embedding_manager import EmbeddingManager
from ingestion.vector_store_manager import VectorStoreManager
from retrieval.retriever_manager import RetreiverManager
from pipline.rag_pipline_manager import RAGPipelineManager

print("Initializing RAG Chat Bot....\n")

# Initialize embedding_manager
embedding_manager = EmbeddingManager()

# Initialize vector_store_manager
vector_store_manager = VectorStoreManager()

# Initialize retreiver_manager
retriever_manager = RetreiverManager(embedding_manager=embedding_manager, vector_store=vector_store_manager)

# Initialize rag_pipline_manager 
rag_pipline_manager = RAGPipelineManager(retreiver_manager=retriever_manager)

print("\nVillageTaste Foods AI Chatbot Ready...\n")

# ==========================================
# CLI Chatbot Loop
# ==========================================

while True:

    query = input("\nYou : ")
    
    # User explicitly want to quit the chat 
    if query.lower() in ["exit", "quit", "bye"]:
        print("\nChat Bot : Thank you for visiting VillageTaste Foods. Goodbye...\n")
        break 
    
    # User just press the enter noting informative enter 
    if not query.strip():
        print("\nChat Bot : Please enter a valid query.\n")
        continue
    
    try:
        respone = rag_pipline_manager.chat(query=query)
        
        # Extract llm_response
        llm_response = respone["llm_response"]

        print(f"\nChat Bot : {llm_response}")

    except Exception as e:
        
        print("\nSome error occur while processing your request.")
        print(f"Error : {e}")