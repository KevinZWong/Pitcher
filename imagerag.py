from langchain.text_splitter import RecursiveCharacterTextSplitter
import json
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

def load_image_descriptins(name="images"):
    with open("image_metadata.json", 'r', encoding='utf-8') as file:
                data = json.load(file)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=4000, 
        chunk_overlap=0,  
        length_function=len,
        separators=["\n\n", "\n", " ", ""]
    )
    all_chunks = []
    for item in data:
        chunks = text_splitter.create_documents(
            texts=[item['description']],
            metadatas=[{
                'filepath': item['filepath'],
                'page_number': item['page_number'],
                'width': item['width'],
                'height': item['height']
            }]
        )
        all_chunks.extend(chunks)
    
    username = 'demo'
    password = 'demo' 
    hostname = os.getenv('IRIS_HOSTNAME', 'localhost')
    port = '1972' 
    namespace = 'USER'
    CONNECTION_STRING = f"iris://{username}:{password}@{hostname}:{port}/{namespace}"
    COLLECTION_NAME = name
    db = IRISVector.from_documents(
                embedding=embeddings,
                documents=all_chunks,
                collection_name=COLLECTION_NAME,
                connection_string=CONNECTION_STRING,
                )
    db.add_documents(all_chunks)
    print("done")  
    ret= db.similarity_search("hello")
    print(ret)
    

def search_q(query, coll="images"):
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
    collection_name=coll,
    connection_string=CONNECTION_STRING,
    )
    ret= db.similarity_search(query, k=4)
    out=[]
    for r in ret:
        out.append(r.metadata['filepath'])

    print(ret)
    print(out)
    return out

# load_image_descriptins()
# search_q("chlorophyl")
