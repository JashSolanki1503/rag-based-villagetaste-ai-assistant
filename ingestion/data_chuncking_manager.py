# Import necessary modules
from langchain_text_splitters import RecursiveCharacterTextSplitter


# Main class logic
class DataChunkingManager:

    def __init__(self):

        # PDF and Text Document Chunk Splitter
        self.pdf_and_text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )

        # MS Word Document Chunk Splitter
        '''
        Priority of splitting:
        1. Paragraph
        2. Line
        3. Sentence
        4. Word
        5. Character

        This helps preserve document structure as much as possible.
        '''

        self.docs_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=150,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    # Chunk PDF and Text Documents
    def chunk_pdfs_and_texts_files(self, pdfs_documents, texts_documents):

        documents = pdfs_documents + texts_documents

        chunk_docs = self.pdf_and_text_splitter.split_documents(documents)

        # Log messages
        print("\nPDFs and Text Document chunking : Length of chunks = ", len(chunk_docs))

        return chunk_docs

    # Chunk DOCX Documents
    def chunk_docx_files(self, docs_documents):

        chunk_docs = self.docs_splitter.split_documents(docs_documents)

        # Log messages
        print("\nMSWord Document chunking : Length of chunks = ", len(chunk_docs))

        return chunk_docs

    # Sheet Documents already act as row-level chunks
    def chunk_sheet_files(self, sheet_documents):

        print("\nMSExcel Document chunking : Length of chunks = ", len(sheet_documents))

        return sheet_documents

    # Combine all chunks
    def get_chunk_data(
        self,
        pdfs_documents,
        texts_documents,
        docs_documents,
        sheet_documents
    ):

        pdf_text_chunks = self.chunk_pdfs_and_texts_files(
            pdfs_documents,
            texts_documents
        )

        docs_chunks = self.chunk_docx_files(docs_documents)

        sheet_chunks = self.chunk_sheet_files(sheet_documents)

        # Combine all chunks
        all_chunks = pdf_text_chunks + docs_chunks + sheet_chunks

        print("\nAll Documents chunk size : ", len(all_chunks))

        return all_chunks