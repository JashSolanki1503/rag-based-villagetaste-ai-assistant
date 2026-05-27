# important modules 
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI

# Main Retriever Pipline
class RAGPipelineManager:

    def __init__(self, retreiver_manager):

        # Load the api key 
        load_dotenv()
        self.API_KEY = os.getenv("GEMINI_API_KEY")

        # Define query_refine_model
        self.query_refine_llm = ChatGoogleGenerativeAI(
            model = "gemini-2.5-flash",
            temperature = 0.1,
            max_tokens = 300,      
            google_api_key = self.API_KEY 
        )


        # Define actual final model 
        self.response_generation_llm = ChatGoogleGenerativeAI(
            model = "gemini-2.5-flash",
            temperature  = 0.3,
            max_tokens = 1024,
            google_api_key = self.API_KEY
        )

        # Other important managers 
        self.retreiver_manager = retreiver_manager

    # To refine the user query 
    def refine_query(self, query):

        # Define sample query which we pass into the llm 
        sample_query = f"""
            You are an expert search query optimizer for a village-based food business chatbot called "VillageTaste Foods".
            
            Your ONLY job is to rewrite the user's input query into an optimized search query for a vector database.
            
            The knowledge base contains:
            - food products (traditional food catalogs, ingredients, items)
            - company services (packaging, delivery, traditional cooking methods)
            - employee policies (shifts, roles, departments like Kitchen)
            - order information
            
            Optimization Rules:
            1. If the query is vague (e.g., "Food list", "what do you sell?"), make it explicit by including domain keywords like "VillageTaste Foods menu products traditional items catalog".
            2. Maintain the core intent of the user.
            3. Keep the output concise and optimized for semantic keyword matching.
            4. Return ONLY the rewritten text. Do not include any explanations, greetings, or quotes.
            
            User Query: {query}
            Optimized Vector Search Query:
            """

        # get refine query 
        refine_query = self.query_refine_llm.invoke(sample_query)

        # becoz at the end over refine_prompt exist inside the content key section 
        refine_query = refine_query.content.strip()
        
        return refine_query

    # Retreive refine query related documents 
    def retreive_documents(self, refine_query, top_k = 5):

        retreived_documents = self.retreiver_manager.retreive(refine_query, top_k = top_k)

        return retreived_documents
        
    # Retreived document related we generate the answer 
    def generate_answer(self, query, retreived_documents):

        # Check very imp edge case 
        if not retreived_documents:
            return """I apologize, but your query does not appear to be related to VillageTaste Foods services or available information.
                    
                    Please ask questions related to:
                    - Food products & catalogs
                    - Services & company overview
                    - Employee policies
                    - Order information
                    """

        else :
            
            # Exteact the real retreived document content 
            context = "\n\n".join([doc["document"] for doc in retreived_documents])

            # here we define over main prompt
            prompt = f"""
                    You are a warm, professional, and friendly AI assistant for VillageTaste Foods, an Indian village-based food business.
                    
                    Instructions:
                    1. Answer the user's question using ONLY the provided context snippets.
                    2. If the user asks for a list or catalog of items, look through the provided context and present all matching items found in the text as a clean, bulleted list.
                    3. Base your answer strictly on the facts directly mentioned. Do NOT infer or extrapolate beyond the text.
                    4. If the context does not contain the answer or enough details to answer completely, politely explain what you can find, but state that specific list details are unavailable.
                    
                    Context: {context}
                    
                    User Question: {query}
                    Helpful Response:"""

            # Extract the response from the llm 
            response = self.response_generation_llm.invoke(prompt)

            return response.content

    # Join all pipline functions
    def chat(self, query, top_k = 5):

        refine_query = self.refine_query(query)

        retreived_documents = self.retreive_documents(refine_query, top_k = top_k)

        llm_response = self.generate_answer(query, retreived_documents)

        return {
            "llm_response": llm_response,
            "query": query,
            "refine_query": refine_query,
            "rertreived_documents": retreived_documents
        }