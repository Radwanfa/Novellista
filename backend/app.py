from flask import Flask, jsonify
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
import bcrypt
from psycopg2 import Binary
from bs4 import BeautifulSoup

c = Console()

llm = llama_cpp.Llama(
    model_path="./models/mxbai-embed-large-v1-f16.gguf",
    n_gpu_layers=-1,
    embedding=True,
    verbose=False
)
Mistral = llama_cpp.Llama(
    model_path="./models/mistral-small-instruct-2409-q4_k_m.gguf",
    verbose=False,
    n_gpu_layers=25,
    n_ctx=2048
)

conn = psycopg2.connect("postgresql://neondb_owner:npg_oGcui5al1YAb@ep-morning-bonus-aby7xgf9-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS users (" \
"id SERIAL PRIMARY KEY," \
"username varchar(255) NOT NULL," \
"password BYTEA NOT NULL" \
")")
cur.execute("CREATE TABLE IF NOT EXISTS sessions (" \
"id SERIAL PRIMARY KEY," \
"string varchar(255) NOT NULL," \
"person_id int NOT NULL,"
"CONSTRAINT fk_person" \
"   FOREIGN KEY(person_id)" \
"       REFERENCES users(id)" \
")")
cur.execute("CREATE TABLE IF NOT EXISTS stories (" \
"id SERIAL PRIMARY KEY," \
"story varchar(1030000)," \
"person_id int NOT NULL," \
"CONSTRAINT fk_person" \
"   FOREIGN KEY(person_id)" \
"       REFERENCES users(id)" \
")")
conn.commit()
app = Flask(__name__)
CORS(app)
@app.post("/api/gen")
def gen():
    string = request.form.get("text")
    soup = BeautifulSoup(string, "html.parser")
    text = soup.get_text()
    
    if len(text) > 2500:
        documents = splitter(text.strip())
        embeddings = embed(documents, llm)
        client = store(embeddings)
        search_query = documents[len(documents)-1].page_content
        query_vector = llm.create_embedding(search_query)['data'][0]['embedding']
        search_result = client.search(
            collection_name="Cage of Crimson",
            query_vector=query_vector,
            limit=5
        )
    else:
        search_query = text

    if len(text) > 2500:
        template = """
        you are a helpful assistant who writes a new paragraph inspired on the given information and your own input.

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
        c.print(stream)
    else:
        template = """
        you are a helpful assistant who writes a new paragraph inspired on the given information and your own input.

        {context}

        Unfinished paragraph: {question}"""

        stream = Mistral.create_chat_completion(
            messages = [
                {"role": "user", "content": template.format(
                    context = search_query,
                    question = search_query
                )}
            ],
            stream=True
        )
        c.print(stream)
    result = ""
    for chunk in stream:
        result += chunk["choices"][0]["delta"].get('content', '')
    return result


@app.post("/api/register")
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    Rpassword = request.form.get("Rpassword")
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(password.encode('utf-8'), salt)

    if (password != Rpassword):
        return jsonify({"status": "fail", "message": "wachtwoorden kloppen niet. Heb je een spelfout gemaakt?"})
    cur.execute("INSERT INTO users (username, password) values (%s, %s);", (username, Binary(hash)))
    cur.execute("SELECT lastval();")
    result = cur.fetchone()
    conn.commit()
    session = create_session(result[0])
    return jsonify({"status": "success", "id": result[0], "string": session})

@app.post("/api/login")
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    cur.execute(f"SELECT id, password FROM users WHERE username=\'{username}\';")
    result = cur.fetchone()
    passwordhash = bcrypt.checkpw(password.encode('utf-8'),  bytes(result[1]))
    if result == None:
        return jsonify({"status": "fail", "message": "Geen gebruiker gevonden"})
    elif passwordhash == False:
        return jsonify({"status": "fail", "message": "Wachtwoorden kloppen niet"})
    else:
        session = create_session(result[0])
        return jsonify({"status": "success", "id": result[0], "string": session})

@app.post("/api/get_session")
def get_session():
    session = request.form.get("session")
    cur.execute(f"SELECT users.id, username FROM users INNER JOIN sessions ON sessions.person_id = users.id WHERE string = '{session}'")
    result = cur.fetchone()
    return jsonify({"id": result[0], "username": result[1]})

@app.post("/api/save_story")
def save_story():
    story = request.form.get("story")
    personId = request.form.get("userId")
    if request.form.get("id") == None:
        cur.execute("INSERT INTO stories (story, person_id) values (%s, %s)", (story, personId))
        cur.execute("SELECT lastval();")
        result = cur.fetchone()
        conn.commit()
        return jsonify({"status": "success", "id": result[0]})
    else:
        id = request.form.get("id")
        cur.execute("UPDATE stories SET story = %s WHERE id = %s", (story, id))
        conn.commit()
        return jsonify({"status": "success"})

@app.post("/api/get_stories")
def get_stories():
    userID = request.headers.get("userId")
    cur.execute(f"SELECT id FROM stories WHERE person_id=\'{userID}\'")
    result = cur.fetchall()
    return jsonify({"stories": result})

@app.get("/api/get_story")
def get_story():
    id = request.args.get("id")
    cur.execute(f"SELECT story FROM stories WHERE id=\'{id}\'")
    result = cur.fetchone()
    return jsonify({"story": result[0]})

def create_session(userID):
    length = 50
    randomString = ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    cur.execute("INSERT INTO sessions (string, person_id) values (%s, %s)", (randomString, userID))
    conn.commit()
    return randomString

def splitter(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1024,
        chunk_overlap = 10,
        length_function = len,
        is_separator_regex = False,
    )

    return text_splitter.create_documents([text])

def embed(documents, llm):
    batchSize = 100
    documentsEmbeddings = []
    batches = list(batched(documents, batchSize))

    start = time.time()
    for batch in batches:
        embeddings = llm.create_embedding([item.page_content for item in batch])
        documentsEmbeddings.extend(
            [
                (document, embeddings['embedding'])
                for document, embeddings in zip(batch, embeddings['data'])
            ]
        )
    end = time.time()
    allText = [item.page_content for item in documents]
    charPerSec = len(''.join(allText)) / (end-start)
    c.print(f"time: {end-start:.2f} seconds / {charPerSec:,.2f} chars/second")
    return documentsEmbeddings




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