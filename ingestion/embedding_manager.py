# Import necessary modules 
from sentence_transformers import SentenceTransformer

# Class logic
class EmbeddingManager:

    def __init__(self, model_name = "BAAI/bge-base-en-v1.5"):

        print("Model is Loading...")        
        self.model_name = model_name

        self.model = SentenceTransformer(self.model_name)
        print("Model Name : ", self.model_name)

    def generate_embeddings(self, texts):

        # first extract only page_contents inside the chunck_documents 
        # texts = [doc.page_content for doc in texts]
        
        embeddings = self.model.encode(texts, show_progress_bar = True)

        # Add some logs indicators 
        print("Type of Embeddings : ", type(embeddings))
        print("Type of Embeddings Data : ", type(embeddings[0]))
        print("Embedding Dimensions : ", embeddings.shape)
        
        return embeddings 