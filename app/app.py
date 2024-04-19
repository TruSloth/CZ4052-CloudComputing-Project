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
    st.link_button("Streamlit Reference", "https://docs.streamlit.io/")
    st.link_button(
        label="Github Repository",
        url="https://github.com/TruSloth/LLM-Quiz-Generator/tree/main",
        type="primary",
    )

st.title("💬 Checkbot")
st.caption("Powered by Google's Gemini LLM")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "embeddingModel" not in st.session_state:
    with st.spinner("Getting ready..."):
        st.session_state.embeddingModel = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

chat = ChatVertexAI(
    model_name="gemini-pro",
    temperature=0,
    max_output_tokens=2048,
    convert_system_message_to_human=True,
    location="asia-southeast1",
)

system = (
    "You are a helpful assistant for question-answering tasks. Using the following pieces of retrieved \
contexts provide an answer based on a query regarding those contexts. Answer with the best of your abilities, but if you \
don't know the answer, just say that you don't know. Keep the answer within five sentences and try to keep the answer consise.\
Context: {context}"
)

human = "Query: {query}"

prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

chain = prompt | chat

def uploadNewFile():
    if "uploaded_file" in st.session_state:
        del st.session_state.uploaded_file     
    if "retriever" in st.session_state:
        del st.session_state.retriever     
    if "images" in st.session_state:
        del st.session_state.images 
    if "filepath" in st.session_state:
        del st.session_state.filepath
    st.session_state.messages = []


st.session_state.uploaded_file = st.sidebar.file_uploader("Choose a file", type="pdf", on_change=uploadNewFile)

if st.session_state.uploaded_file is not None:
    if "retriever" in st.session_state:
        if "images" in st.session_state:
            for page in st.session_state.images:
                st.session_state.imagesList.append(page)

            if st.session_state.imagesList:
                st.sidebar.header("Page Selector")

            st.session_state.selected_page = st.sidebar.selectbox(
                "Select Page", range(len(st.session_state.imagesList)), index=0
            )

            if st.session_state.selected_page is not None:
                st.image(
                    st.session_state.imagesList[st.session_state.selected_page],
                    channels="BGR",
                    use_column_width=True,
                )

            # Display chat messages from history on app rerun
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            query = st.chat_input("Enter your query here.")

            if query:
                st.chat_message("user").markdown(query)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": query})

            retrievedDocs = st.session_state.retriever.invoke(query)

            with st.spinner("Let me see..."):
                message = chain.invoke(
                    {
                        "context": retrievedDocs,
                        "query": query,
                    }
                )

            st.session_state.messages.append(
                {"role": "assistant", "content": message.content}
            )

            with st.chat_message("assistant"):
                st.markdown(message.content)
    else:
        # Write uploaded_file bytes to container filesystem
        filename = uuid4()

        if "filepath" not in st.session_state:
            st.session_state.filepath = Path(f"/tmp/{filename}.pdf")

        with open(st.session_state.filepath, "wb") as f:
            f.write(st.session_state.uploaded_file.getbuffer())

        with st.spinner("Loading PDF..."):
            loader = PyPDFLoader(str(st.session_state.filepath))
            pages = loader.load_and_split()

            temp = []

            for page in pages:
                texts = text_splitter.create_documents([page.page_content])
                temp.append(texts)

            # flattens the 2d temp list
            pdf = sum(temp, [])

            vectorStore = Chroma.from_documents(pdf, st.session_state.embeddingModel)

            st.session_state.retriever = vectorStore.as_retriever(
                search_type="similarity", search_kwargs={"k": 5}
            )

            st.session_state.imagesList = []
            st.session_state.images = pdf2image.convert_from_bytes(
                st.session_state.uploaded_file.read()
            )

            if "images" in st.session_state:
                for page in st.session_state.images:
                    st.session_state.imagesList.append(page)

                if st.session_state.imagesList:
                    st.sidebar.header("Page Selector")

                st.session_state.selected_page = st.sidebar.selectbox(
                    "Select Page", range(len(st.session_state.imagesList)), index=0
                )

                if st.session_state.selected_page is not None:
                    st.image(
                        st.session_state.imagesList[st.session_state.selected_page],
                        channels="BGR",
                        use_column_width=True,
                    )

                # Display chat messages from history on app rerun
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

                query = st.chat_input("Enter your query here.")

                if query:
                    st.chat_message("user").markdown(query)
                    # Add user message to chat history
                    st.session_state.messages.append({"role": "user", "content": query})

                    retrievedDocs = st.session_state.retriever.invoke(query)

                    with st.spinner("Let me see..."):
                        message = chain.invoke(
                            {
                                "context": retrievedDocs,
                                "query": query,
                            }
                        )

                    st.session_state.messages.append(
                        {"role": "assistant", "content": message.content}
                    )

                    with st.chat_message("assistant"):
                        st.markdown(message.content)
