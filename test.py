from celery import shared_task
from home.models import Meesages
import openai
from django.core.cache import cache
from sklearn.metrics.pairwise import cosine_similarity
import re
import logging
import time
from langchain.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
import tempfile
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os 
from ai_utils.save_faq_embeddings_for_company import VECTOR_CACHE

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    filename=r'C:\Users\Amirmahdi\Desktop\Chatbot Project\WhoTalk-stable\tasks.log'
)

def get_vectorstore_for_company(company):
    company_id = str(company.id)

    if company_id in VECTOR_CACHE:
        print(f"✅ Cache hit for company {company_id}")
        return VECTOR_CACHE[company_id]['vectorstore']

    print(f"⚠️ Cache miss for company {company_id}, loading from DB...")

    if not company.faq_index_faiss or not company.faq_index_metadata:
        print(f"❗ No FAQ index found for company {company_id}")
        return None

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=os.getenv("OPENAI_API_KEY"))

    with tempfile.TemporaryDirectory() as temp_dir:
        faiss_path = os.path.join(temp_dir, "index.faiss")
        metadata_path = os.path.join(temp_dir, "index.pkl")

        with open(faiss_path, "wb") as f:
            f.write(company.faq_index_faiss)

        with open(metadata_path, "wb") as f:
            f.write(company.faq_index_metadata)

        vectorstore = FAISS.load_local(temp_dir, embeddings)

    # ✅ Update VECTOR_CACHE after DB load
    VECTOR_CACHE[company_id] = {'vectorstore': vectorstore}
    print(f"✅ VECTOR_CACHE updated for company {company_id} from DB.")

    return vectorstore

@shared_task
def process_message(message_id, file_data=None, file_name=None):

    openai.api_key = os.getenv("OPENAI_API_KEY")
    try:
        message = Meesages.objects.get(id=message_id)
        company = message.company
        user_question = message.text.strip()
        
        vectorstore = get_vectorstore_for_company(company)

        
        start = time.time()
        if not vectorstore:
            fallback = f'متاسفانه پاسخ شما را ندارم.\n لطفا با پشتیبانی تماس بگیرید: {company.owner.phone_number}'
            Meesages.objects.create(
                text=fallback,
                msg_sender=message.msg_receiver,
                msg_receiver=message.msg_sender,
                msg_receiver_number=message.msg_sender_number,
                received=False,
                processed_by_api=False,
                company=company,
            )
            return
        
        
        # ✅ Search relevant FAQ entries
        docs_and_scores = vectorstore.similarity_search_with_score(user_question, k=3)
        results = [doc for doc, score in docs_and_scores if score >= 0.2]

        if not results:
            fallback = f'متاسفانه پاسخ شما را ندارم.\n لطفا با پشتیبانی تماس بگیرید: {company.owner.phone_number}'
            Meesages.objects.create(
                text=fallback,
                msg_sender=message.msg_receiver,
                msg_receiver=message.msg_sender,
                msg_receiver_number=message.msg_sender_number,
                received=False,
                processed_by_api=False,
                company=company,
            )
            return

        # ✅ Prepare context
        faq_context = "\n\n".join([f"Q: {doc.page_content}\nA: {doc.metadata.get('answer')}" for doc in results])

        # ✅ Build prompt
        template = """شما یک ربات پشتیبانی برای {brand} هستید.
    با استفاده از اطلاعات زیر به سوالات کاربران پاسخ دهید:

    {context}

    سوال کاربر: {question}"""
        
        prompt_template = PromptTemplate(
            input_variables=["brand", "context", "question"],
            template=template
        )

        llm = ChatOpenAI(model="gpt-4o-mini", openai_api_key=os.getenv("OPENAI_API_KEY"))

        prompt_input = {
            "brand": company.name,
            "context": faq_context,
            "question": user_question
        }
        
        response = llm.invoke(prompt_template.format(**prompt_input)).content
        
        # ✅ Save chatbot response
        Meesages.objects.create(
            text=response,
            msg_sender=message.msg_receiver,
            msg_receiver=message.msg_sender,
            msg_receiver_number=message.msg_sender_number,
            received=False,
            processed_by_api=False,
            company=company,
        )
        logging.info(f"1 {time.time() - start:.2f} seconds")
        logging.info(f"4 {time.time() - start:.2f} seconds")
    except Exception as e:
        print(f"Error in process_message: {e}")
