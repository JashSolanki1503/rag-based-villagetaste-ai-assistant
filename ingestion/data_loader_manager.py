# Necessary modules 
import os 

from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader, TextLoader
from langchain_community.document_loaders.csv_loader import CSVLoader
import pandas as pd

# Main class logic
class DataLoaderManager:

    def __init__(self):
        
        self.pdf_folder_path = "data/pdfs_data"
        self.docs_folder_path = "data/docs_data"
        self.text_folder_path = "data/text_data"
        self.sheet_folder_path = "data/sheet_data"
        self.csv_folder_path = "data/csv_data"

    def load_pdfs(self):

        # Extract the all files name first 
        all_files = os.listdir(self.pdf_folder_path)

        # define list to store this all contents inside it 
        all_documents = []
        num_docs = 0

        for filename in all_files:
            
            if filename.lower().strip().endswith(".pdf"):

                # Extract the full file path 
                file_path = os.path.join(self.pdf_folder_path, filename)

                # Load the pdf file content 
                pdf_loader = PyMuPDFLoader(file_path)
                doc = pdf_loader.load()

                # add metadata part 
                for d in doc:
                    d.metadata["source_type"] = "pdf"

                # here every pdf containes the diffrent no of pages so that why we use extend() instead of the append()
                all_documents.extend(doc)
                num_docs += 1

        # Print the log message 
        print("\nPDFs => Extracted Documents Size : ", len(all_documents))
        print("PDFs => No of Documents Extracted : ", num_docs)

        return all_documents

        
    def load_docs(self):

        # Extract the all files name first 
        all_files = os.listdir(self.docs_folder_path)

        # define list to store this all contents inside it 
        all_documents = []
        num_docs = 0

        for filename in all_files:
            
            if filename.lower().strip().endswith(".docx"):

                # Extract the full file path 
                file_path = os.path.join(self.docs_folder_path, filename)

                # Load the pdf file content 
                doc_loader = Docx2txtLoader(file_path)
                doc = doc_loader.load()

                # add metadata part 
                for d in doc:
                    d.metadata["source_type"] = "docx"

                # here every pdf containes the diffrent no of pages so that why we use extend() instead of the append()
                all_documents.extend(doc)
                num_docs += 1

        # Print the log message 
        print("\nDocuments => Extracted Documents Size : ", len(all_documents))
        print("Documents => No of Documents Extracted : ", num_docs)

        return all_documents

    def __convert_excel_to_clean_csv(self, excel_file_path, csv_file_path):

        # first load hte excel file 
        # here sheet_name = 0 means we want to access the very first sheet inside the MS Workbook (every excel file can containes multiple sheets and we can see this in bottom tab section
        # We want to fill empty cell as empty string becoz if we not do explicitly then pandas add NaN which further causes ERROR in ingestion Pipline
        df = pd.read_excel(excel_file_path, sheet_name = 0).fillna("")

        # this map fnx we apply on entire dataset so it apply each cell of row and work on row by row (top modt left cell to bottom most right cell)
        # if any cell is string and containes some leading and traling space that case we remove it to improve ingestion pipline
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

        # save this modified sheet in given folder as csv file 
        df.to_csv(csv_file_path, index = False)     

    def load_sheets(self):

        # Extract the all files name first 
        all_files = os.listdir(self.sheet_folder_path)

        # define list to store this all contents inside it 
        all_documents = []
        num_docs = 0

        for filename in all_files:

            if filename.lower().strip().endswith(".xlsx"):

                # Extract the full file path 
                file_path = os.path.join(self.sheet_folder_path, filename)

                # We convert this sheet into the csv and store this csv in desire folder 
                self.__convert_excel_to_clean_csv(file_path, os.path.join(self.csv_folder_path, f"{filename.replace('.xlsx', '')}.csv"))

                # Load the csv file content 
                csv_filename = filename.replace(".xlsx", ".csv")
                csv_path = os.path.join(self.csv_folder_path, csv_filename)
                csv_loader = CSVLoader(csv_path)

                doc = csv_loader.load()

                # add metadata part 
                for d in doc:
                    d.metadata["source_type"] = "sheet"

                all_documents.extend(doc)
                num_docs += 1

        # Print the log message 
        print("\nSheets => Extracted Documents Size : ", len(all_documents))
        print("Sheets => No of Documents Extracted : ", num_docs)

        return all_documents
        

    def load_texts(self):
        
        # Extract the all files name first 
        all_files = os.listdir(self.text_folder_path)

        # define list to store this all contents inside it 
        all_documents = []
        num_docs = 0

        for filename in all_files:
            
            if filename.lower().strip().endswith(".txt"):

                # Extract the full file path 
                file_path = os.path.join(self.text_folder_path, filename)

                # Load the pdf file content 
                text_loader = TextLoader(file_path)
                doc = text_loader.load()

                # add metadata part 
                for d in doc:
                    d.metadata["source_type"] = "text"

                # here every pdf containes the diffrent no of pages so that why we use extend() instead of the append()
                all_documents.extend(doc)
                num_docs += 1

        # Print the log message 
        print("\nText File => Extracted Documents Size : ", len(all_documents))
        print("Text File => No of Documents Extracted : ", num_docs)

        return all_documents

    def load_all_documents(self):
        
        pdf_documents = self.load_pdfs()
        docs_documents = self.load_docs()
        texts_documents = self.load_texts()
        sheets_documents = self.load_sheets()

        return {
            "pdf_documents": pdf_documents, 
            "docs_documents": docs_documents,
            "texts_documents": texts_documents,
            "sheets_documents": sheets_documents,
            "all_documents": pdf_documents + docs_documents + texts_documents + sheets_documents
        }