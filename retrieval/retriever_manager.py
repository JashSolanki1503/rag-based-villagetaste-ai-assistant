# important modules 
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI

# Class logic
class RetreiverManager:

    def __init__(self, embedding_manager, vector_store):
        
        self.embedding_manager = embedding_manager
        self.vector_store = vector_store

    def retreive(self, query, top_k = 5, score_threshold = 0.15):
        
        # Add BGE query prefix for better retrieval
        bge_query = "Represent this sentence for searching relevant passages: " + query

        # Query => Embeddings 
        # Here embedding_manager expect the multiple sentences as queries but we have only one query 
        # so to access the given query embeddings from nested of list given by embedding_manager that we use 0th index 
        query_embeddings = self.embedding_manager.generate_embeddings([bge_query])[0]

        # retreive the top_k result 
        results = self.vector_store.collection.query(
            query_embeddings = [query_embeddings.tolist()],
            n_results = top_k
        )

        # Validate the retreived results
        # Here we check documents key containes valid data and inside this valid data we check it empty or not
        retreived_documents = []
        
        if results["documents"] and results["documents"][0]:

            # Extract data inside the results
            ids = results["ids"][0]
            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0]

            for i, (doc_id, document, metadata, distance) in enumerate(zip(ids, documents, metadatas, distances)):

                # Compute the cosine similarity 
                similarity_score = 1 - distance

                # Check retreived document compatible with score_threshold 
                if similarity_score >= score_threshold:

                    retreived_documents.append({
                        "doc_id": doc_id,
                        "document": document,
                        "metadata": metadata,
                        "distance": distance,
                        "similarity_score": similarity_score,
                        "rank": i + 1
                    })
            print(f"Retreived {len(retreived_documents)} Documents") 
                    
        else:
            print("No Related Document Retreived")

        return retreived_documents     