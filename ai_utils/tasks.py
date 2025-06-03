from celery import shared_task
from account.models import User
from home.models import Meesages
from django.core.cache import cache
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging
import time
import faiss
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    filename=r'tasks.log'
)

@shared_task
def process_message(message_id, file_data=None, file_name=None):
    """
    Celery task to process a user message and generate a chatbot response.
    Combines FAQ similarity search (via FAISS) with GPT-generated responses.
    """
    start = time.time()
    client = OpenAI(api_key=api_key)

    try:
        # --- Load message, company, and admin user from DB ---
        message = Meesages.objects.get(id=message_id)
        print('-----------------',message.text)
        company = message.company
        print('-----------------',company.name)
        admin_user = User.objects.get(name=message.msg_receiver)
        user_question = message.text.strip()

        # --- Get last 6 chat messages to build chat history context ---
        history_messages = Meesages.objects.filter(company=company).order_by('-id')[:6]
        history_messages = list(history_messages)[::-1]  # chronological order

        # --- Build history context text (user & assistant messages) ---
        history_context = ""
        for msg in history_messages:
            history_context += f" {msg.text}\n"

        # --- Load company's FAQ data and their vector embeddings ---
        faq_data = company.faq_json  # list of {"question": ..., "answer": ...}
        embedding_bytes = company.faq_embeddings

        logging.info(f"1 {time.time() - start:.2f} seconds")
        start = time.time()

        # --- Convert binary embeddings back to numpy array & reshape ---
        embeddings = np.frombuffer(embedding_bytes, dtype='float32')
        embedding_dim = len(embeddings) // len(faq_data)
        embeddings = embeddings.reshape(len(faq_data), embedding_dim)

        # --- Initialize FAISS index for similarity search ---
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)  # Inner Product (cosine similarity)
        index.add(embeddings)

        logging.info(f"2 {time.time() - start:.2f} seconds")
        start = time.time()

        # --- Handle case where no FAQ data exists ---
        if not faq_data:
            chatgpt_response = f'متاسفانه پاسخ شما را نمیتوانم.\n لطفا با پشتیبانی تماس بگیرید: {company.owner.phone_number}'
            processed_by_api = True
        else:
            # --- Embed user question to get its vector representation ---
            user_embedding = client.embeddings.create(
                model="text-embedding-3-small",
                input=user_question
            ).data[0].embedding
            user_embedding = np.array(user_embedding, dtype='float32')
            user_embedding = user_embedding / np.linalg.norm(user_embedding)

            # --- Search top-k most similar FAQs using FAISS ---
            k = 3
            D, I = index.search(np.array([user_embedding]), k)

            # --- Debug: Print similarity score for top-k FAQs ---
            for idx, sim_score in zip(I[0], D[0]):
                if idx != -1:
                    print(f"------------------FAQ Index: {idx} | Similarity Score: {sim_score:.4f} | Question: {faq_data[idx]['question']}")

            logging.info(f"3 {time.time() - start:.2f} seconds")
            start = time.time()

            # --- Filter valid matches based on similarity threshold ---
            threshold = 0.4  # Higher = stricter match
            top_indices = I[0]
            top_distances = D[0]


            valid_indices = [
                idx for idx, dist in zip(top_indices, top_distances) if idx != -1 and dist > threshold
            ]

            print('valid_indices:', valid_indices)
            
            # --- If no valid matches, fallback to contact support ---


            if valid_indices:
                                # --- Prepare FAQ context for GPT prompt from valid matches ---
                top_faqs = [faq_data[i] for i in valid_indices]

                # faq_context = "\n\n".join([f"{item['question']}\n{item['answer']}" for item in top_faqs])
                faq_context = "\n\n".join([f"{item['answer']}" for item in top_faqs])

                # --- Construct prompt with FAQ, chat history, and user question ---
                prompt_system = f"""
                شما یک ربات پشتیبانی برای{company.name} هستید.
                """
                prompt_user_with_history = f"""
                {faq_context}
                سوال کاربر: {user_question}
                """



                print("📤 PROMPT TO CHATGPT:\n", prompt_user_with_history)

                # --- Generate chatbot reply using OpenAI GPT ---
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": prompt_system},
                        {"role": "user", "content": prompt_user_with_history}
                    ]
                )
                chatgpt_response = response.choices[0].message.content.strip()
                processed_by_api = True
            else:
                                # --- Construct prompt with FAQ, chat history, and user question ---
                prompt_system = f"""
                شما یک ربات پشتیبانی برای{company.name} هستید.
                
                اگر سوال کاریبر غیر مرتبط بود پاسخ نده و فقط بگو لطفا با پشتیبانی تماس بگیرید 
                شماره پشتیبانی : {company.owner.phone_number}
                """
                prompt_user_with_history = f"""
                تاریخچه گفتگو:

                {history_context}
                سوال کاربر: {user_question}

                """
                print("📤 PROMPT TO CHATGPT:\n", prompt_user_with_history)

                # --- Generate chatbot reply using OpenAI GPT ---
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": prompt_system},
                        {"role": "user", "content": prompt_user_with_history}
                    ]
                )
                chatgpt_response = response.choices[0].message.content.strip()
                processed_by_api = True
        # --- Get admin user's image URL (if available) ---
        full_img_url = admin_user.image.url if admin_user and admin_user.image else ''

        # --- Save the chatbot's reply as a new message in DB ---
        Meesages.objects.create(
            text=chatgpt_response,
            msg_sender=message.msg_receiver,
            msg_receiver=message.msg_sender,
            msg_receiver_number=message.msg_sender_number,
            msgImg=full_img_url,
            received=False,
            processed_by_api=processed_by_api,
            company=company,
        )

        logging.info(f"4 {time.time() - start:.2f} seconds")

    except Exception as e:
        print(f"Error in process_message: {e}")