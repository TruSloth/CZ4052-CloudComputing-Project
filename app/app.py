import streamlit as st
# import pandas as pd
# import cv2
# import numpy as np
import pdf2image
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_vertexai import ChatVertexAI

from pathlib import Path
from uuid import uuid4

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500,
    chunk_overlap=50,
    length_function=len,
    is_separator_regex=False,
)

instructions = """
1. Upload a PDF file using the file uploader.
2. Use the page selector to choose the page to display the page of your choice.
3. Enter the query in the prompt below.
4. ...
"""

# Sidebar button to show instructions
with st.sidebar.expander("Instructions"):
    st.write(instructions)

with st.sidebar:
    # openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
    # st.link_button("Get an OpenAI API key", "https://platform.openai.com/account/api-keys")
    st.link_button("Streamlit Reference", "https://docs.streamlit.io/")
    st.link_button(label="Github Repository", url = "https://github.com/TruSloth/LLM-Quiz-Generator/tree/main", type="primary")

st.title("💬 Checkbot")
st.caption("Powered by Google's Gemini LLM")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

embeddingModel = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')

chat = ChatVertexAI(
        model_name="gemini-pro",
        temperature=0,
        max_output_tokens=2048,
        convert_system_message_to_human=True
    )

# human = "You are a helpful assistant for question-answering tasks. Use the following pieces of retrieved \
# context to answer the question. If you don't know the answer, just say that you don't know. Use five sentences \
# maximum and try to keep the answer consise.\
# Question: {question}\
# Context: {context}"

system = "You are a helpful assistant for question-answering tasks. Using the following pieces of retrieved \
contexts provide an answer based on a query regarding those contexts. Answer with the best of your abilities, but if you \
don't know the answer, just say that you don't know. Keep the answer within five sentences and try to keep the answer consise.\
Context: {context}"

human = "Query: {query}"

prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

chain = prompt | chat

uploaded_file = st.file_uploader("Choose a file", type="pdf")

if uploaded_file is not None:
    # Write uploaded_file bytes to container filesystem
    filename = uuid4()

    filepath = Path(f"/tmp/{filename}.pdf")

    with open(filepath, 'wb') as f:
        f.write(uploaded_file.getbuffer())

    loader = PyPDFLoader(str(filepath), extract_images=True)
    pages = loader.load_and_split()

    temp = []

    for page in pages:
        texts = text_splitter.create_documents([page.page_content])
        temp.append(texts)
    
    # flattens the 2d temp list
    pdf = sum(temp, [])

    vectorStore = Chroma.from_documents(pdf, embeddingModel)

    retriever = vectorStore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

    imagesList = []
    images = pdf2image.convert_from_bytes(uploaded_file.read())
    for page in images:
        #st.write(page)
        imagesList.append(page)

    if imagesList:
        st.sidebar.header("Page Selector")
        selected_page = st.sidebar.selectbox("Select Page", range(len(imagesList)), index=0)

        if selected_page is not None:
            st.image(imagesList[selected_page], channels="BGR", use_column_width=True)

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        query = st.chat_input("Enter your query here.")

        if query:
            st.chat_message("user").markdown(query)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": query})

            retrievedDocs = retriever.invoke(query)

            message = chain.invoke(
                {
                    "context": retrievedDocs,
                    "query": query,
                }
            )

            st.session_state.messages.append({"role": "assistant", "content": message.content})







