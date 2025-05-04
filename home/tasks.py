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
from django.contrib.auth import get_user_model
import re
import difflib

# User = get_user_model()


@shared_task
def process_message(message_id, file_data=None, file_name=None):
    openai.api_key = "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"
    try:
        # دریافت پیام از دیتابیس
        message = Meesages.objects.get(id=message_id)
        company = message.company
        # ذخیره پیام ادمین
        admin_user = User.objects.get(name=message.msg_receiver)
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

        # بارگذاری داده‌های FAQ برای RAG
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

            # تابع محاسبه شباهت بین دو رشته

        def similarity(a, b):
            return difflib.SequenceMatcher(None, a, b).ratio()

        # بررسی تطبیق سوال کاربر با سوالات FAQ با استفاده از شباهت متنی
        best_match_answer = None
        highest_similarity = 0
        user_question = message.text.strip()
        threshold = 0.5  # آستانه شباهت (50 درصد)

        for item in faq_data:
            faq_question = item["question"].strip()
            sim = similarity(user_question, faq_question)
            if sim > highest_similarity:
                highest_similarity = sim
                best_match_answer = item["answer"].strip()

        # اگر شباهت بیش از آستانه بود، از پاسخ FAQ استفاده می‌کنیم
        if highest_similarity >= threshold:
            chatgpt_response = best_match_answer
            processed_by_api = True  # API صدا زده نشد
        else:
            context = "\n".join([f"سوال: {item['question']}\nپاسخ: {item['answer']}" for item in faq_data])

            # Prepare prompt for ChatGPT
            prompt = f"""
                    You are acting as a customer support specialist for the website {company.website} under the brand name {company.name}. You can access all relevant information about the website, its brand identity, and FAQs from the uploaded file. Using this information, you will respond professionally and helpfully to user inquiries as a chatbot support agent. Avoid using the phrase "پاسخ:" in your replies.
                    {context}
                    سوال کاربر: "{message.text}"
                    اگر سوال کاربر دقیقاً با یکی از سوالات مطابقت داشت یا مشابه بود، پاسخ مرتبط را ارائه دهید. اگر تصویری ضمیمه شده باشد و مشکلی در آن باشد، توضیحی در مورد تصویر و ارائه راه حل برای آن اضافه کنید.
                    در غیر این صورت، پاسخ "نامشخص" را برگردانید.
    
                    {image_analysis_result if image_analysis_result else "No image was attached."}
                    """

            # Call ChatGPT with RAG approach
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system",
                     "content": "شما یک متخصص پشتیبانی حرفه‌ای هستید که از RAG برای پاسخ به سوالات استفاده می‌کنید."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            chatgpt_response = response.choices[0].message["content"].strip()
            chatgpt_response = re.sub(r'\s*پاسخ:\s*', '', chatgpt_response).strip()
            processed_by_api = False
            # Handle unknown responses
            if chatgpt_response.lower() == "نامشخص":
                chatgpt_response = "لطفاً با پشتیبانی تماس بگیرید: ۰۹۱۲۴۲۲۵۷۲۹"
                processed_by_api = True

        if admin_user and admin_user.image:
            full_img_url = admin_user.image.url
        else:
            full_img_url = ''
        admin_response = Meesages.objects.create(
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
        print(f"Error in process_message task: {e}")

