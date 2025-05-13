import openai
import numpy as np
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

def save_faq_embeddings_for_company(company, faq_file):

    openai.api_key = api_key

    embedding_objects = []

    for item in faq_file:
        question = item["question"].strip()
        answer = item["answer"].strip()

        emb = openai.Embedding.create(
            model="text-embedding-3-small",
            input=question
        ).data[0].embedding

        emb = np.array(emb, dtype='float32')
        emb = emb / np.linalg.norm(emb)
        embedding_objects.append(emb)


    company.faq_embeddings = np.stack(embedding_objects).tobytes()
    company.save()