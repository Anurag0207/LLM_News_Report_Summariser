import os
import streamlit as st
import pickle
from langchain import OpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredURLLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

from dotenv import load_dotenv
load_dotenv(".env")

st.title("News Research Tool 📈 and Summarizer")
st.sidebar.title("News Article URLs")

urls = []
for i in range(3):
    url = st.sidebar.text_input(f"URL {i+1}")
    urls.append(url)

process_url_clicked = st.sidebar.button("Process URLs")
file_path = "faiss_store_openai.pkl"

main_placeholder = st.empty()
llm = OpenAI(temperature=0.9, max_tokens=400)

if process_url_clicked:
    loader = UnstructuredURLLoader(urls=urls)
    main_placeholder.text("Data Loading...")
    data = loader.load()
    main_placeholder.text("Data Loaded!")
    
    if data:
        text_splitter = RecursiveCharacterTextSplitter(separators=['\n\n', '\n', '.', ','],
                                                      chunk_size=1000)
        docs = text_splitter.split_documents(data)
        embeddings = OpenAIEmbeddings()
        vectors_openai = FAISS.from_documents(docs, embeddings)
        
        with open(file_path, "wb") as f:
            pickle.dump(vectors_openai, f)
        
        main_placeholder.text("Embedding Vector Build Completed!")

query = main_placeholder.text_input("Question: ")
if query:
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            vectorstore = pickle.load(f)
            chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=vectorstore.as_retriever())
            result = chain({"question": query}, return_only_outputs=True)
            
            st.header("Answer")
            st.write(result["answer"])

            sources = result.get("sources", "")
            if sources:
                st.subheader("Sources:")
                sources_list = sources.split("\n")
                for source in sources_list:
                    st.write(source)

# Summarization Section
if process_url_clicked and data:
    st.sidebar.subheader("Generate Summary")
    summary_button = st.sidebar.button("Generate Summary")
    
    if summary_button:
        st.subheader("Article Summaries")
        for i, doc in enumerate(docs):
            st.markdown(f"**Article {i+1}**")
            # Simple summary by taking the first 3 sentences
            sentences = doc.split(".")
            summary = ". ".join(sentences[:3]) + "."
            st.write(summary)
