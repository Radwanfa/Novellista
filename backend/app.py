from flask import Flask
from flask import request
import random
import string
import psycopg2
import json
from flask_cors import CORS
import llama_cpp
import time
from itertools import batched
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import uuid
from rich.console import Console

c = Console()

conn = psycopg2.connect("postgresql://neondb_owner:npg_yZTjsEzBOU64@ep-wispy-dream-a4erkeq5-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (" \
"id SERIAL PRIMARY KEY," \
"username varchar(255) NOT NULL," \
"password varchar(255) NOT NULL" \
")")
cur.execute("CREATE TABLE IF NOT EXISTS sessions (" \
"id SERIAL PRIMARY KEY," \
"string varchar(255) NOT NULL," \
"person_id int NOT NULL,"
"CONSTRAINT fk_person" \
"   FOREIGN KEY(person_id)" \
"       REFERENCES users(id)" \
")")
conn.commit()
app = Flask(__name__)
CORS(app)
@app.post("/api/gen")
def gen():
    
    text = request.form.get("text")

    documents = splitter(text.strip())

    llm = llama_cpp.Llama(
        model_path="./models/mxbai-embed-large-v1-f16.gguf",
        n_gpu_layers=-1,
        embedding=True,
        verbose=False
    )

    embeddings = embed(documents, llm)

    client = store(embeddings)

    search_query = documents[len(documents)-1].page_content
    c.print(search_query)
    query_vector = llm.create_embedding(search_query)['data'][0]['embedding']
    search_result = client.search(
        collection_name="Cage of Crimson",
        query_vector=query_vector,
        limit=5
    )

    Mistral = llama_cpp.Llama(
        model_path="./models/mistral-small-instruct-2409-q4_k_m.gguf",
        verbose=False,
        n_gpu_layers=25,
        n_ctx=2048
    )

    template = """
    you are a helpful assistant who completes paragraphs only on the information provided.
    If you don't know, simply state you don't know.

    {context}

    Unfinished paragraph: {question}"""

    stream = Mistral.create_chat_completion(
        messages = [
            {"role": "user", "content": template.format(
                context = "\n\n".join([row.payload['text'] for row in search_result]),
                question = search_query
            )}
        ],
        stream=True
    )
    result = ""
    for chunk in stream:
        result += chunk["choices"][0]["delta"].get('content', '')
    return result


@app.post("/api/register")
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    Rpassword = request.form.get("Rpassword")

    if (password != Rpassword):
        return json.dumps({"status": "fail", "message": "wachtwoorden kloppen niet. Heb je een spelfout gemaakt?"})
    cur.execute("INSERT INTO users (username, password) values (%s, %s);", (username, password))
    cur.execute("SELECT lastval();")
    result = cur.fetchone()
    conn.commit()
    return json.dumps({"status": "success", "id": result[0]})

@app.post("/api/login")
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    cur.execute(f"SELECT id, password FROM users WHERE username=\'{username}\';")
    result = cur.fetchone()
    if result == None:
        return json.dumps({"status": "fail", "message": "Geen gebruiker gevonden"})
    elif password != result[1]:
        return json.dumps({"status": "fail", "message": "Wachtwoorden kloppen niet"})
    else:
        return json.dumps({"status": "success", "id": result[0]})
    
@app.post("/api/create_session")
def create_session():
    userID = request.form.get("userID")
    print(userID)
    length = 50
    randomString = ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    cur.execute("INSERT INTO sessions (string, person_id) values (%s, %s)", (randomString, userID))
    conn.commit()
    return json.dumps({"status": "success", "string": randomString})

@app.post("/api/get_session")
def get_session():
    session = request.form.get("session")
    cur.execute(f"SELECT username FROM users INNER JOIN sessions ON sessions.person_id = users.id WHERE string = '{session}'")
    result = cur.fetchone()
    return json.dumps({"username": result[0]})


def splitter(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1024,
        chunk_overlap = 10,
        length_function = len,
        is_separator_regex = False,
    )

    return text_splitter.create_documents([text])

def embed(documents, llm):
    batch_size = 100
    documents_embeddings = []
    batches = list(batched(documents, batch_size))

    start = time.time()
    for batch in batches:
        embeddings = llm.create_embedding([item.page_content for item in batch])
        documents_embeddings.extend(
            [
                (document, embeddings['embedding'])
                for document, embeddings in zip(batch, embeddings['data'])
            ]
        )
    end = time.time()
    all_text = [item.page_content for item in documents]
    char_per_sec = len(''.join(all_text)) / (end-start)
    c.print(f"time: {end-start:.2f} seconds / {char_per_sec:,.2f} chars/second")
    return documents_embeddings




def store(embeddings):
    client = QdrantClient(path="embeddings")
    client.delete_collection(collection_name="Cage of Crimson")
    client.create_collection(
        collection_name="Cage of Crimson",
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
    )

    points = [
        PointStruct(
            id = str(uuid.uuid4()),
            vector=embeddings,
            payload= {
                "text": document.page_content
            }
        )
        for document, embeddings in embeddings
    ]

    operation_info = client.upsert(
        collection_name="Cage of Crimson",
        wait=True,
        points=points
    )
    c.print(operation_info)
    return client