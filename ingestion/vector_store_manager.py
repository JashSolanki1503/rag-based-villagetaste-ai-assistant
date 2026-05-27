# Necessary modules 
import os 
import chromadb
import uuid

# Class logic
# note : by default ChromaDB use the L2 (Euclidean Distance) so we need to specify it 
class VectorStoreManager:

    def __init__(self, persist_directory = "data/vector_store", collection_name = "knowledge_base"):

        self.persist_directory  = persist_directory
        self.collection_name = collection_name

        self.client = None 
        self.collection = None

        self._initialize_store()

    def _initialize_store(self):

        # Create directory where over database actually store data
        os.makedirs(self.persist_directory, exist_ok = True)

        # Create client / Handler for handle the database all things
        self.client = chromadb.PersistentClient(
            path = self.persist_directory
        )

        # Create location where we actually store over knowledge_base data
        self.collection = self.client.get_or_create_collection(
            name = self.collection_name,
            metadata = {
                "description": "Knowledge_Base Creation to store pdfs, docx, sheets and text documents data",
                "hnsw:space": "cosine"   # add this to define the COSINE similarity 
            }
        )

    def add_documents(self, documents, embeddings):

        # Check first edge case 
        if len(documents) != len(embeddings):
            raise ValueError("No of Documents and No Document related Embeddings are not same")

        # Initialize some data structure for storing data
        ids = []
        all_metadatas = []
        all_documents_contents = []
        all_embeddings = []

        for i, (doc, emb) in enumerate(zip(documents, embeddings)):

            # Store each documents unique id 
            doc_id = f"doc_{uuid.uuid4()}"
            ids.append(doc_id)

            # Store each documents metadata
            metadata = dict(doc.metadata)

            metadata["doc_index"] = i
            metadata["doc_id"] = doc_id

            metadata["content_length"] = len(doc.page_content)
            all_metadatas.append(metadata)

            # Store each documents actual content 
            all_documents_contents.append(doc.page_content.strip())

            # Store each documents related embeddings
            '''
            here we convert embeddings into the list becoz individual chunck related embeddings in form of numpy array 
            and overall chuncks embeddings stores inside the list 
            '''
            
            all_embeddings.append(emb.tolist())

        # Store this four things in VectorDB 
        self.collection.add(
            ids = ids,
            metadatas = all_metadatas,
            documents = all_documents_contents,
            embeddings = all_embeddings
        )

        # add some log for the clarification 
        print("Length of Database's Collection : ", self.collection.count())
        print("Total Documents Count : ", len(all_documents_contents))