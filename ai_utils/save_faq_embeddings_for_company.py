
from langchain.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from dotenv import load_dotenv

load_dotenv()
VECTOR_CACHE={}
def save_faq_embeddings_for_company(company, faq_data):
    

    # Prepare documents
    docs = [
        Document(page_content=item["question"], metadata={"answer": item["answer"]})
        for item in faq_data
    ]

    # Initialize embeddings
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Build FAISS index from documents
    vectorstore = FAISS.from_documents(
        documents=docs,
        embedding=embeddings
    )

    # Save FAISS index locally
    vectorstore.save_local("temp_faiss")

    # Read saved index files and store them in the company model
    with open("temp_faiss/index.faiss", "rb") as f:
        company.faq_index_faiss = f.read()

    with open("temp_faiss/index.pkl", "rb") as f:
        company.faq_index_metadata = f.read()

    company.save()

    company_id = str(company.id)
    VECTOR_CACHE[company_id] = {
        'vectorstore': vectorstore
    }