import os
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import JSONLoader
import json
from pathlib import Path
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_iris import IRISVector
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
embeddings = OpenAIEmbeddings()

def load_docs(folder_path, name):
    username = 'demo'
    password = 'demo' 
    hostname = os.getenv('IRIS_HOSTNAME', 'localhost')
    port = '1972' 
    namespace = 'USER'
    CONNECTION_STRING = f"iris://{username}:{password}@{hostname}:{port}/{namespace}"
    COLLECTION_NAME = name
    count=0
    for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            loader =PyPDFLoader(file_path)
            documents= loader.load()
            text_splitter = CharacterTextSplitter(chunk_size=250, chunk_overlap=50)
            data= text_splitter.split_documents(documents)
            if count==0:
                db = IRISVector.from_documents(
                embedding=embeddings,
                documents=data,
                collection_name=COLLECTION_NAME,
                connection_string=CONNECTION_STRING,
                )
            else:
                db = IRISVector(
                embedding_function=embeddings,
                dimension=1536,
                collection_name=COLLECTION_NAME,
                connection_string=CONNECTION_STRING,
                )
            db.add_documents(data)
            print("done")
     
    ret= db.similarity_search("hello")
    print(ret)
    

def search_q(query, coll="test"):
    embeddings = OpenAIEmbeddings()
    username = 'demo'
    password = 'demo' 
    hostname = os.getenv('IRIS_HOSTNAME', 'localhost')
    port = '1972' 
    namespace = 'USER'
    CONNECTION_STRING = f"iris://{username}:{password}@{hostname}:{port}/{namespace}"
    COLLECTION_NAME = "main"
    db = IRISVector(
    embedding_function=embeddings,
    dimension=1536,
    # collection_name=COLLECTION_NAME,
    collection_name=coll,
    connection_string=CONNECTION_STRING,
    )
    ret= db.similarity_search(query)
    print(ret)
    # print(f"Number of docs in vector store: {len(db.get()['ids'])}")
    return ret



# load_docs("../docs", "test")
# search_q("what")
