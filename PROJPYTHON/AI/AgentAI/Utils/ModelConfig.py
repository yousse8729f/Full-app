from os import getenv
from pathlib import Path

from langchain_ollama import ChatOllama,OllamaEmbeddings
from langchain_groq import ChatGroq
from dotenv import load_dotenv
current = Path(__file__).parent
env_path = current/".env"
load_dotenv(dotenv_path=env_path)
GROG_API = getenv("GROG_API")
OLLAMA_API = getenv("OLLAMA_API")

class Model:
    def __init__(self,temp):
        self.temperature = temp

        self.embedding ="mxbai-embed-large:latest"
        self.embedding2="nomic-embed-text:latest"
        self.tools = "llama3.1:latest"
        self.llama32="llama3.2:latest"
    def model_llama(self):
        model = ChatOllama(model=self.tools,
                           temperature=self.temperature,
                           top_k=10,
                           top_p=0.7)
        return model
    def model_llama2(self):
        model = ChatOllama(model=self.llama32,
                           temperature=self.temperature,
                           top_k=10,
                           top_p=0.7)
        return model

    def model_llama_Grog(self):
        model = ChatOllama(
                    model="qwen3-next:80b-cloud",
                    base_url="https://ollama.com",
                    client_kwargs={
                        "headers": {
                            "Authorization": f"Bearer {OLLAMA_API}"
                        }
                    }
)
        return model
    def model_Gemma(self):
        model = ChatOllama(
                    model="gemma4:31b-cloud",
                    base_url="https://ollama.com",
                    client_kwargs={
                        "headers": {
                            "Authorization": f"Bearer {OLLAMA_API}"
                        }
                    }
)
        return model
    def model_Grog(self):
        model = ChatGroq(
                   model="llama-3.3-70b-versatile",
                   api_key=GROG_API


                         )
        return model


    def model_embedding(self):
        embedding =OllamaEmbeddings(model=self.embedding,top_k=30,temperature=self.temperature)
        return embedding
    def model_embedding_2(self):
        embedding =OllamaEmbeddings(model=self.embedding2,top_k=30,temperature=self.temperature)
        return embedding

