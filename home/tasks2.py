from celery import shared_task
from account.models import User
from .models import Meesages
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

api_key = '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'

@shared_task
def process_message(message_id, file_data=None, file_name=None):
    openai.api_key = api_key
    try:
        message = Meesages.objects.get(id=message_id)
        company = message.company
        admin_user = User.objects.get(name=message.msg_receiver)
        user_question = message.text.strip()

        # تحلیل تصویر (در صورت وجود)
        image_analysis_result = None
        if file_data and file_name:
            decoded_file = base64.b64decode(file_data)
            mime_type, _ = mimetypes.guess_type(file_name)
            if mime_type in ['image/png', 'image/jpeg']:
                try:
                    image = Image.open(io.BytesIO(decoded_file))
                    image_bytes = io.BytesIO()
                    image.save(image_bytes, format=image.format)
                    image_bytes = image_bytes.getvalue()

                    # تحلیل تصویر با OpenAI
                    image_analysis_result = openai.Image.create_edit(
                        image=image_bytes,
                        instructions="Explain the content of the image for customer support.",
                    ).get("data", [{}])[0].get("url", "Analysis failed.")
                except Exception as e:
                    image_analysis_result = f"Error analyzing image: {e}"

        # Load FAQ data
        cache_key = f"faq_data_{company.id}"
        faq_data = cache.get(cache_key)
        if not faq_data and company and company.faq:
            faq_file_path = company.faq.path
            faq_excel = pd.read_excel(faq_file_path)
            faq_data = [
                {"question": row["سوال"], "answer": row["پاسخ"]}
                for _, row in faq_excel.iterrows()
            ]
            cache.set(cache_key, faq_data, timeout=3600)

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

            # Embed FAQ questions
            faq_embeddings = []
            for item in faq_data:
                emb = openai.Embedding.create(
                    model="text-embedding-3-small",
                    input=item["question"].strip()
                ).data[0].embedding
                faq_embeddings.append(np.array(emb, dtype='float32'))

            # Compute similarities
            similarities = cosine_similarity([user_embedding], faq_embeddings)[0]
            top_indices = similarities.argsort()[-3:][::-1]  # Top 3
            top_scores = similarities[top_indices]
            threshold = 0.50

            if all(score < threshold for score in top_scores):
                chatgpt_response = "لطفاً با پشتیبانی تماس بگیرید: ۰۹۱۲۴۲۲۵۷۲۹"
                processed_by_api = True
            else:
                top_faqs = [faq_data[i] for i in top_indices]
                faq_context = "\n\n".join([f"Q: {item['question']}\nA: {item['answer']}" for item in top_faqs])
                prompt = f"شما یک ربات پشتیبانی حرفه‌ای برای برند {company.name} هستید. با استفاده از اطلاعات زیر به سوالات کاربران پاسخ دهید.\n\n{faq_context}\n\nسوال کاربر: {user_question}"

                response = openai.ChatCompletion.create(
                    model="gpt-4o",
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

    except Exception as e:
        print(f"Error in process_message: {e}")
