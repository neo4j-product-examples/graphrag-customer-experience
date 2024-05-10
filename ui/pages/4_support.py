import asyncio
from typing import List, Optional, Tuple

import streamlit as st
from langserve import RemoteRunnable
from streamlit.logger import get_logger

logger = get_logger(__name__)


st.set_page_config(layout="wide")
st.title("Customer Support")
st.subheader("Reduce Cost to Serve with Well-Grounded, Fact-Based, AI Scripts")
st.markdown(":gray[GraphRAG provides explicit rules from a knowledge graph to improve the "
            "explainability, transparency, and accuracy of AI scripts and agents.]")
st.markdown('__AI Support:__')

class StreamHandler:
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def new_token(self, token: str) -> None:
        self.text += token
        self.container.markdown(self.text, unsafe_allow_html=True)


# Initialize chat history
if "generated" not in st.session_state:
    st.session_state["generated"] = []
if "user_input" not in st.session_state:
    st.session_state["user_input"] = []

# Display user message in chat message container
if st.session_state["generated"]:
    size = len(st.session_state["generated"])
    # Display only the last three exchanges
    for i in range(max(size - 3, 0), size):
        with st.chat_message("user"):
            st.markdown(st.session_state["user_input"][i])
        with st.chat_message("assistant"):
            st.markdown(st.session_state["generated"][i])


async def get_agent_response(
    input: str, stream_handler: StreamHandler, chat_history: Optional[List[Tuple]] = []
):
    url = "http://api:8080/support/"
    st.session_state["generated"].append("")
    remote_runnable = RemoteRunnable(url)
    async for data in remote_runnable.astream({"input": input, "chat_history": chat_history}):
        stream_handler.new_token(data)
        st.session_state["generated"][-1] += data


def generate_history():
    context = []
    # If any history exists
    if st.session_state["generated"]:
        # Add the last three exchanges
        size = len(st.session_state["generated"])
        for i in range(max(size - 3, 0), size):
            context.append(
                (st.session_state["user_input"][i], st.session_state["generated"][i])
            )
    return context


# Accept user input
prompt = st.chat_input("How can I help you today?")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        status = st.status(label="Generating answer🤖", state="running", expanded=False)
        stream_handler = StreamHandler(st.empty())
    chat_history = generate_history()
    # Create an event loop: this is needed to run asynchronous functions
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Run the asynchronous function within the event loop
    loop.run_until_complete(get_agent_response(prompt, stream_handler, chat_history))
    # Close the event loop
    loop.close()
    status.update(label="Finished!", state="complete", expanded=False)
    # Add user message to chat history
    st.session_state.user_input.append(prompt)
