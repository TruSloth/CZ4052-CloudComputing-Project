import streamlit as st
from app.components.quiz_history import quiz_history


def restart_quiz():
    for key in st.session_state.keys():
        del st.session_state[key]


def sidebar():
    with st.sidebar:
        st.markdown("# About")
        st.markdown(
            "📖 Welcome to Cloud Computing QuizBot, an LLM-powered quiz application designed to test your cloud computing concepts."
        )
        st.divider()

        with st.expander("**Instructions**"):
            st.markdown("1. Enter the settings you would like to use for your quiz.")
            st.markdown("2. Click on `Start Quiz` to begin.")
            st.markdown(
                "3. You will be presented with a question. Answer it by entering your response, which will be evaluated."
            )
            st.markdown(
                "4. After your response is evaluated, you may continue to ask questions or clarify the provided feedback using the chat interface."
            )
            st.markdown("5. When you are ready to proceed, click `Next Question`.")

        quiz_history()

        if "quiz_started" in st.session_state and st.session_state["quiz_started"]:
            st.button("Restart Quiz", on_click=restart_quiz)
