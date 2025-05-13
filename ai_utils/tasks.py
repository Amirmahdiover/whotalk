from celery import shared_task
from account.models import User
from home.models import Meesages
import openai
import base64
from PIL import Image
import io
import mimetypes
from django.core.cache import cache
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re
import logging
import time
import faiss
import os
import json


api_key = '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'


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    filename=r'tasks.log'
)

@shared_task
def process_message(message_id, file_data=None, file_name=None):
    start = time.time()
    openai.api_key = api_key
    try:
        message = Meesages.objects.get(id=message_id)
        company = message.company
        admin_user =  User.objects.get(name=message.msg_receiver)
        user_question = message.text.strip()

        
        faq_data = company.faq_json  # JSONField: list of {"question": ..., "answer": ...}
        embedding_bytes = company.faq_embeddings
        logging.info(f"0.01 {time.time() - start:.2f} seconds")
        start=time.time()
        logging.info(f"0.1 {time.time() - start:.2f} seconds")
        start=time.time()
        # Restore embeddings and FAISS index
        embeddings = np.frombuffer(embedding_bytes, dtype='float32')
        embedding_dim = len(embeddings) // len(faq_data)
        embeddings = embeddings.reshape(len(faq_data), embedding_dim)
        # embeddings = embeddings.reshape(len(faq_data), -1)

        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)

# 2-----------------------------------------------------

        logging.info(f"1 {time.time() - start:.2f} seconds")
        start = time.time()
        if not faq_data:
            chatgpt_response = "لطفاً با پشتیبانی تماس بگیرید: ۰۹۱۲۴۲۲۵۷۲۹"
            processed_by_api = True

        else:
            
            # Embed user question
            user_embedding = openai.Embedding.create(
                model="text-embedding-3-small",
                input=user_question
            ).data[0].embedding
            user_embedding = np.array(user_embedding, dtype='float32')
            user_embedding = user_embedding / np.linalg.norm(user_embedding)
            k = 3
            D, I = index.search(np.array([user_embedding]), k)



            logging.info(f"2 {time.time() - start:.2f} seconds")
            start = time.time()
            # ✅ Distance threshold (FAISS returns L2 by default)
            threshold = 0.7  # adjust depending on your embeddings' quality

            top_indices = I[0]
            top_distances = D[0]

            valid_indices = [
                idx for idx, dist in zip(top_indices, top_distances) if idx != -1 and dist < threshold
            ]
            print('valid_indices:',valid_indices)
            if not valid_indices:
                chatgpt_response = f'متاسفانه پاسخ شما را نمیتوانم.\n لطفا با پشتیبانی تماس بگیرید: {company.owner.phone_number}'
                processed_by_api = True
            else:
                top_faqs = [faq_data[i] for i in valid_indices]
                print('top_faqs:',top_faqs)
                faq_context = "\n\n".join([f"Q: {item['question']}\nA: {item['answer']}" for item in top_faqs])
                prompt = f"شما یک ربات پشتیبانی حرفه‌ای برای برند {company.name} هستید. با استفاده از اطلاعات زیر به سوالات کاربران پاسخ دهید.\n\n{faq_context}\n\nسوال کاربر: {user_question}"
                print("📤 PROMPT TO CHATGPT:\n", prompt)
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "شما یک دستیار پشتیبانی هستید."},
                        {"role": "user", "content": prompt}
                    ]
                )

                chatgpt_response = response.choices[0].message.content.strip()

                processed_by_api = False

        full_img_url = admin_user.image.url if admin_user and admin_user.image else ''

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
