from flask import Flask, request, jsonify, render_template
import os
from pathlib import Path
from langchain_huggingface import HuggingFaceEndpoint, HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS

# Initialize Flask app
app = Flask(__name__)

# Get Hugging Face token from environment
HF_TOKEN = os.environ.get("HF_TOKEN")
HUGGINGFACE_REPO_ID = "mistralai/Mistral-7B-Instruct-v0.3"

# Load the LLM with updated arguments
def load_llm(huggingface_repo_id):
    llm = HuggingFaceEndpoint(
        repo_id=huggingface_repo_id,
        task="text-generation",
        huggingfacehub_api_token=HF_TOKEN,
        temperature=0.5,
        max_new_tokens=512,
        do_sample=True
    )
    return llm

# Custom prompt template
CUSTOM_PROMPT_TEMPLATE = """
Use the pieces of information provided in the context to answer user's question.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Don't provide anything out of the given context.

Context: {context}
Question: {question}

Start the answer directly. No small talk please.
"""

def set_custom_prompt(custom_prompt_template):
    prompt = PromptTemplate(
        template=custom_prompt_template,
        input_variables=["context", "question"]
    )
    return prompt

# Load FAISS vectorstore
DB_FAISS_PATH = str(Path("vectorstore/db_faiss").resolve())
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.load_local(DB_FAISS_PATH, embedding_model, allow_dangerous_deserialization=True)

# Create RetrievalQA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=load_llm(HUGGINGFACE_REPO_ID),
    chain_type="stuff",
    retriever=db.as_retriever(search_kwargs={'k': 3}),
    return_source_documents=True,
    chain_type_kwargs={'prompt': set_custom_prompt(CUSTOM_PROMPT_TEMPLATE)}
)

# Define routes
@app.route('/')
def home():
    return render_template('index.html')  # Render a simple HTML form

@app.route('/ask', methods=['POST'])
def ask_question():
    user_query = request.form.get('query')
    response = qa_chain.invoke({'query': user_query})
    
    # Extract the result (without source documents)
    result = response["result"]
    
    # Only pass the result to the result page
    return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
