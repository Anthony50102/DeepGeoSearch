import json
import os
import subprocess
import logging
from abc import ABC, abstractmethod

from openai import OpenAI
from sentence_transformers import SentenceTransformer
from tenacity import retry, stop_after_attempt, wait_random_exponential

logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)


class BaseEmbeddingModel(ABC):
    @abstractmethod
    def create_embedding(self, text):
        pass


class OpenAIEmbeddingModel(BaseEmbeddingModel):
    def __init__(self, model="text-embedding-ada-002"):
        self.model = model

    @retry(wait=wait_random_exponential(min=1, max=6), stop=stop_after_attempt(6))
    def create_embedding(self, text):
        text = text.replace("\n", " ")
        try:
            response = self._call_openai_api(text)
            embedding = json.loads(response)["data"][0]["embedding"]
            return embedding
        except:
            logging.debug(f"Failed to create embedding for text: {text}")
            raise

    def _call_openai_api(self, text):
        api_key = os.getenv("OPENAI_API_KEY")  # Replace with your actual API key
        headers = [
            "Content-Type: application/json",
            f"Authorization: Bearer {api_key}"
        ]
        data = {
            "input": text,
            "model": self.model,
            "encoding_format": "float"
        }
        data_str = json.dumps(data)
        
        curl_command = [
            "curl", "https://api.openai.com/v1/embeddings",
            "-H", headers[0], "-H", headers[1],
            "-d", data_str
        ]
        
        result = subprocess.run(curl_command, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Curl command failed with error: {result.stderr}")
        
        return result.stdout
class SBertEmbeddingModel(BaseEmbeddingModel):
    def __init__(self, model_name="sentence-transformers/multi-qa-mpnet-base-cos-v1"):
        self.model = SentenceTransformer(model_name)

    def create_embedding(self, text):
        return self.model.encode(text)
