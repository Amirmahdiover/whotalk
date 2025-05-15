
from langchain.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()
VECTOR_CACHE={}
def save_faq_embeddings_for_company(company, faq_data):
    
    
    # Prepare documents
    from langchain.document_loaders import DataFrameLoader

    faq_data['combined'] = faq_data['سوال'] + "\n" + faq_data['پاسخ']
    loader = DataFrameLoader(faq_data, page_content_column="combined")
    documents = loader.load()

    # splitting it into chunks
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200,separators='/n')
    all_splits = text_splitter.split_documents(documents)

    # Initialize embeddings
    from langchain_community.embeddings import OpenAIEmbeddings

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # Saving documents Embededd with Faiss
    from langchain.vectorstores import FAISS

    vector_store = FAISS.from_documents(all_splits, embeddings)
    vector_store.save_local("faiss_store_company123")



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