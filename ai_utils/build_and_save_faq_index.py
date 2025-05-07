# ai_utils.py
import openai
import faiss
import numpy as np
import json
import os
import re

api_key = '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'
openai.api_key = api_key

def slugify(name):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', name).lower()

def build_and_save_faq_index(company_name, faq_data, output_dir="companies"):
    openai.api_key = api_key
    # Embed and normalize FAQ questions
    faq_embeddings = []
    for item in faq_data:

        emb = openai.Embedding.create(
            model="text-embedding-3-small",
            input=item["question"].strip()
        ).data[0].embedding
        emb = np.array(emb, dtype='float32')
        emb = emb / np.linalg.norm(emb)
        faq_embeddings.append(emb)


    # Create FAISS index
    dimension = faq_embeddings[0].shape[0]
    index = faiss.IndexFlatIP(dimension)
    index.add(np.stack(faq_embeddings))

    # Save index and metadata
    company_slug = slugify(company_name)
    company_folder = os.path.join(output_dir, company_slug)
    os.makedirs(company_folder, exist_ok=True)

    faiss.write_index(index, os.path.join(company_folder, "faq.index"))
    with open(os.path.join(company_folder, "faq_data.json"), "w", encoding="utf-8") as f:
        json.dump(faq_data, f, ensure_ascii=False)
