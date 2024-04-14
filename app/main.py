"""Python file to serve as the frontend"""

import sys
import os

sys.path.append(os.path.abspath("."))

import random

import streamlit as st
import time

from app.components.sidebar import sidebar
from app.topics.topics import get_topics, get_subtopic

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_google_vertexai import ChatVertexAI, create_structured_runnable
from langchain_core.pydantic_v1 import BaseModel, Field

class ResponseEvaluation(BaseModel):
    """Record the evaluation of a response to a question, including the given score, the maximum possible score and the feedback to the response provided."""

    score: int = Field(..., description="The given score")
    max_score: int = Field(..., description="The maximum possible score")
    feedback: str = Field(..., description="The feedback to the response that was provided to the question.")


def load_chat_chain(
    prompt,
    output_parser=None,
    temperature=0,
    location="asia-southeast1",
    max_output_tokens=2048,
):
    """Logic for loading the chat chain"""
    if output_parser is None:
        output_parser = StrOutputParser()
    chat = ChatVertexAI(
        model_name="chat-bison",
        temperature=temperature,
        location=location,
        max_output_tokens=max_output_tokens,
    )

    chat_chain = prompt | chat | output_parser
    return chat_chain


def start_quiz(topics, difficulty_level, question_format):
    if not topics or len(topics) == 0:
        st.error("You must select at least 1 topic!")
        return
    st.session_state["quiz_started"] = True
    st.session_state["current_question_number"] = 1
    st.session_state["messages"] = [[]]
    st.session_state["conversation_history"] = {}
    st.session_state["topics"] = topics
    st.session_state["difficulty_level"] = difficulty_level
    st.session_state["question_format"] = question_format
    st.session_state["scores"] = {}


def next_question():
    st.session_state["current_question_number"] += 1
    st.session_state["messages"].append([])


def output_ai_text(ai_response):
    """Output LLM response with a typewriter effect"""

    with st.chat_message("ai"):
        full_response = ""
        message_placeholder = st.empty()
        for chunk in ai_response.split(" "):
            full_response += chunk + " "
            time.sleep(0.05)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
    return full_response


def get_conversation_history(session_id):
    if session_id not in st.session_state["conversation_history"]:
        st.session_state["conversation_history"][session_id] = ChatMessageHistory()
    return st.session_state["conversation_history"][session_id]


# Configuration
TOPICS = get_topics()

LEVELS = ["Trivial", "Easy", "Medium", "Hard", "Insane"]

QUESTION_FORMATS = ["Multiple-Choice Questions", "Open-Ended Questions"]

if __name__ == "__main__":
    # Retrieve Secrets
    GOOGLE_PROJECT_ID = os.environ.get("GOOGLE_PROJECT_ID")
    GOOGLE_API_KEY_SECRET_ID = os.environ.get("GOOGLE_API_KEY_SECRET_ID")

    print("Starting chat server")

    st.set_page_config(
        page_title="Cloud Computing Quiz App",
        page_icon="📖",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.header("📖 Cloud Computing Quiz App")
    sidebar()

    response_evaluation_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a quiz response evaluator for a cloud computing quiz.\
Evaluate the response to the following question and provide friendly and appropriate feedback.\
Your feedback should start by stating if the response is correct or wrong, followed by additional explanations or feedback.\
You should make sure to assign a score to the response, out of a maximum possible score given in the question. Record all this information\
by making calls to the relevant function.\
Question: {question}",
            ),
            #MessagesPlaceholder(variable_name="history"),
            ("human", "The response is: {response}"),
        ]
    )
    question_generation_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "human",
                "You are a quiz question generator for a cloud computing course.\
Generate a {question_format} question for {subtopic} in the context of {topic}. Include the maximum score (ranging from 1 to 5) you would assign to the question.\
Ensure that the question begins with the question number {question_number} and is of {difficulty_level} difficulty.\
You must not include the correct answer in your response.",
            )
        ]
    )

    question_generation_chain = load_chat_chain(
        prompt=question_generation_prompt, output_parser=StrOutputParser()
    )

    response_evaluation_chain = load_chat_chain(
        prompt=response_evaluation_prompt, output_parser=PydanticOutputParser(pydantic_object=ResponseEvaluation)
    )

    chat = ChatVertexAI(
        model_name="gemini-pro",
        temperature=0,
        location="asia-southeast1",
        max_output_tokens=2048,
        convert_system_message_to_human=True
    )

    response_evaluation_chain = create_structured_runnable([ResponseEvaluation], llm=chat, prompt=response_evaluation_prompt)

    # Add history to response_evaluation_chain
    response_evaluation_chain_with_history = RunnableWithMessageHistory(
        response_evaluation_chain,
        get_conversation_history,
        input_messages_key="response",
        history_messages_key="history",
    )


    # Check if an exisiting chat session exists and if not, initialize it
    if "quiz_started" not in st.session_state or not st.session_state["quiz_started"]:
        st.markdown("## Quiz Settings")
        selected_topics = st.multiselect("Topics to include", TOPICS)

        difficulty_level = st.select_slider(
            "Difficulty Level",
            options=LEVELS,
        )

        question_format = st.selectbox("Question format", options=QUESTION_FORMATS)

        st.button(
            "Start Quiz",
            on_click=start_quiz,
            kwargs={
                "topics": selected_topics,
                "difficulty_level": difficulty_level,
                "question_format": question_format,
            },
        )

    else:
        for message in st.session_state.messages[
            st.session_state["current_question_number"] - 1
        ]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if user_input := st.chat_input(
            "Enter your response here."
        ):  # Add user message to chat history
            st.session_state.messages[
                st.session_state["current_question_number"] - 1
            ].append({"role": "human", "content": user_input})
            # Display user message in chat message container
            with st.chat_message("human"):
                st.markdown(user_input)
        if (
            len(
                st.session_state["messages"][
                    st.session_state["current_question_number"] - 1
                ]
            )
            == 0
        ):
            with st.spinner("Quiz-Bot is generating a new question..."):
                topic = random.choice(st.session_state["topics"])
                question = question_generation_chain.invoke(
                    input={
                        "question_format": st.session_state["question_format"],
                        "topic": topic,
                        "subtopic": get_subtopic(topic),
                        "question_number": st.session_state["current_question_number"],
                        "difficulty_level": st.session_state["difficulty_level"]
                    }
                )
            st.session_state.messages[
                st.session_state["current_question_number"] - 1
            ].append({"role": "ai", "content": question})

            full_response = output_ai_text(ai_response=question)

        else:
            if st.session_state["messages"][
                st.session_state["current_question_number"] - 1
            ][-1]["role"] in ["human"]:
                question = st.session_state["messages"][
                    st.session_state["current_question_number"] - 1
                ][0]["content"]
                user_input = st.session_state["messages"][
                    st.session_state["current_question_number"] - 1
                ][-1]["content"]

                if not question:
                    raise RuntimeError("No question found in session state")

                with st.spinner("QUIZ-BOT is at Work ..."):
                    response_evaluation = response_evaluation_chain.invoke(
                        input = {
                            "question": question,
                            "response": user_input,
                        },
                    )

                feedback = response_evaluation.feedback
                score = response_evaluation.score
                max_score = response_evaluation.max_score


                full_response = output_ai_text(ai_response=feedback)
                st.session_state.messages[
                    st.session_state["current_question_number"] - 1
                ].append({"role": "ai", "content": full_response})
            
                # Update Score
                if st.session_state["current_question_number"] not in st.session_state["scores"]:
                    st.session_state["scores"][st.session_state["current_question_number"]] = (score, max_score)
            
            if (st.session_state["current_question_number"] in st.session_state["scores"]):
                score = st.session_state["scores"][st.session_state["current_question_number"]]
                st.markdown(f"Score: {score[0]} / {score[1]}")


            if (
                st.session_state["current_question_number"]
                == len(st.session_state["messages"])
                and len(
                    st.session_state["messages"][
                        st.session_state["current_question_number"] - 1
                    ]
                )
                > 1
            ):
                st.button("Next Question", on_click=next_question)
