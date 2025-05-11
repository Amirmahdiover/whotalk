import openai
import numpy as np
import pandas as pd

api_key = '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'
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