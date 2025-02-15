import os
from dotenv import load_dotenv
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from openai import OpenAI
from langchain_iris import IRISVector

load_dotenv(override=True)
OPENAI_KEY=os.getenv("OPENAI_API_KEY")
PERPLEXITY_KEY=os.getenv("PERPLEXITY_API_KEY")
parser = StrOutputParser()
embeddings = OpenAIEmbeddings( model="text-embedding-3-small", openai_api_key=OPENAI_KEY)
username = 'demo'
password = 'demo' 
hostname = os.getenv('IRIS_HOSTNAME', 'localhost')
port = '1972' 
namespace = 'USER'
CONNECTION_STRING = f"iris://{username}:{password}@{hostname}:{port}/{namespace}"
vectorstore = IRISVector(
    embedding_function=embeddings,
    dimension=1536,
    collection_name="test",
    connection_string=CONNECTION_STRING)


messages=[{
             'role': 'system',
                'content': f""""You are a panel member of a presentation that is currently being held. 
                An audience member just asked a question about something. Your job is to answer the question.
                I will provide you with a combination of information that you can use to answer the question.
                I will provide you with information retrieved from our db and I will also provide you some context from the internet.
                If you feel these are usefyll then you can use them to answer the question.
                """
            }]

client=OpenAI(api_key=OPENAI_KEY)

messages_p = [
    {
        "role": "system",
        "content": (
            "You are a research assistant and your job is togather information from the internet to answer a user's question."
            "You will be given a question and based off that question respond with thee most useful info from the web."
        ),
    }
]

Perplexity = OpenAI(api_key=PERPLEXITY_KEY, base_url="https://api.perplexity.ai")


def get_relevant_info(query):
    perplexity_message=f"""This is the User's Query:\n {query}"""
    messages_p.append(
            {
                'role': 'user',
                'content': perplexity_message
            })
    internet_context=Perplexity.chat.completions.create(
                        model="sonar-pro",
                        messages=messages_p,
                    )
    context=vectorstore.similarity_search(query, k=5)
    formatted_user_query = f"""
        This is the User's Query:\n
        {query}
        This is the context retrieved based on the internal documents:\n
        {context}
        This is the context retrieved based on the stack exchange:\n
        {internet_context}
    """
    messages.append(
            {
                'role': 'user',
                'content': formatted_user_query
            })
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )
    out = response.choices[0].message.content
    print(out)
    return out



if __name__=="__main__":
    query="What are the use cases of Program Derived Addresses?"
    output=get_relevant_info(query)
    print(output)