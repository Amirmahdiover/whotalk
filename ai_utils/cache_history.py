from django.core.cache import cache
import numpy as np
from openai import OpenAI
import os

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def get_history_embedding(company_id, sender_number, user_embedding):
    """
    Retrieve chat history embedding from cache.
    If not found, initialize it with user_embedding.
    """
    cache_key = f"chat_history_embedding_{company_id}_{sender_number}"
    cached_history = cache.get(cache_key)

    if cached_history:
        cached_history_embedding = cached_history["embedding"]
        cached_history_text = cached_history.get("text", "")
        history_embedding = np.array(cached_history_embedding, dtype='float32')
        context_similarity = np.dot(user_embedding, history_embedding)
        print("📜 Cached History Text:", cached_history_text)
    else:
        history_embedding = user_embedding  # first message default
        context_similarity = 0.2
    print('get------------------------',cache_key)
    return history_embedding, context_similarity, cache_key


def update_history_embedding(cache_key, history_embedding, user_embedding, assistant_response, history_context, user_question):
    """
    Update history embedding with new user message and assistant response.
    Save updated embedding back to cache.
    """
    assistant_embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=assistant_response
    ).data[0].embedding

    assistant_embedding = np.array(assistant_embedding, dtype='float32')
    assistant_embedding = assistant_embedding / np.linalg.norm(assistant_embedding)

    # Simple average of old history + new user + new assistant  
    updated_history_embedding = (history_embedding + assistant_embedding + user_embedding) / 3.0
    updated_history_embedding = updated_history_embedding / np.linalg.norm(updated_history_embedding)
    
    # Update history text for traceability
    updated_history_text = history_context + f"\nUser: {user_question}\nAssistant: {assistant_response}"

    print('update------------------------',cache_key)
    # Save back to cache
    cache.set(cache_key, {
    "embedding": updated_history_embedding.tolist(),
    "text": updated_history_text  # this is what you want to inspect later
    }, timeout=600)
