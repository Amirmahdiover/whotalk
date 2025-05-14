from openai import OpenAI
import numpy as np
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

def save_faq_embeddings_for_company(company, faq_file):

    client = OpenAI(api_key=api_key)

    embedding_objects = []

    for item in faq_file:
        question = item["question"].strip()
        answer = item["answer"].strip()

        emb = client.embeddings.create(
            model="text-embedding-3-small",
            input=question
        ).data[0].embedding

        emb = np.array(emb, dtype='float32')
        emb = emb / np.linalg.norm(emb)
        embedding_objects.append(emb)


    embedding_bytes = np.stack(embedding_objects).tobytes()

    if hasattr(company, 'faq_embeddings'):
        company.faq_embeddings = embedding_bytes
    elif hasattr(company, 'faq_index_faiss'):
        company.faq_index_faiss = embedding_bytes
    else:
        raise AttributeError("Company model has neither 'faq_embeddings' nor 'faq_index_faiss' field.")

    company.save()