import streamlit as st


def view_question(question_number):
    st.session_state["current_question_number"] = question_number


def quiz_history():
    if "messages" in st.session_state:
        st.markdown("## History")
        st.markdown(
            "Use the buttons below to navigate through past questions. The current question being shown is highlighted in :blue[blue]."
        )
        st.divider()
        for i in range(len(st.session_state["messages"])):
            button_text = (
                f":blue[Question {i + 1}]"
                if i == st.session_state["current_question_number"] - 1
                else f"Question {i + 1}"
            )
            button_disabled = (
                True if i == st.session_state["current_question_number"] - 1 else False
            )
            st.button(
                button_text,
                disabled=button_disabled,
                on_click=view_question,
                kwargs={"question_number": i + 1},
                use_container_width=True,
            )
