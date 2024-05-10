import asyncio

import streamlit as st
from langserve import RemoteRunnable

st.set_page_config(layout="wide")
st.title("Discovery")
st.subheader("Improve Click-Through Rate with Personalized Marketing")
st.markdown(":gray[GraphRAG combines structured customer data with "
            "unstructured search and text descriptions to customize "
            "AI-generated content for every customer.]")

st.markdown('__GraphRAG Email Generation:__')
customer_examples = [
    [
        'Alex Smith',
        'Oversized Sweaters',
        'daae10780ecd14990ea190a1e9917da33fe96cd8cfa5e80b67b4600171aa77e0',
        'Feb, 2024',
    ],
    [
        'Robin Fischer',
        'Oversized Sweaters',
        '819f4eab1fd76b932fd403ae9f427de8eb9c5b64411d763bb26b5c8c3c30f16f',
        'Feb, 2024'
    ],
    [
        'Chris Johnson',
        'Oversized Sweaters',
        '44b0898ecce6cc1268dfdb0f91e053db014b973f67e34ed8ae28211410910693',
        'Feb, 2024'
    ],
    [
        'Robin Fischer',
        'denim jeans',
        '819f4eab1fd76b932fd403ae9f427de8eb9c5b64411d763bb26b5c8c3c30f16f',
        'Feb, 2024'
    ]
]


class StreamHandler:
    def __init__(self, container, status, initial_text=""):
        self.status = status
        self.container = container
        self.text = initial_text

    def new_token(self, token: str) -> None:
        self.text += token
        self.container.markdown(self.text, unsafe_allow_html=True)

    def new_status(self, status_update: str) -> None:
        status.update(label="Generating answer🤖", state="running", expanded=True)
        with status:
            st.write(status_update)


async def get_chain_response(customer_interests: str,  customer_id: str, customer_name: str, time_of_year: str,
                             stream_handler: StreamHandler):
    url = "http://api:8080/generate-email/"
    remote_runnable = RemoteRunnable(url)
    async for chunk in remote_runnable.astream_log(
            {
                'customer_interests': customer_interests,
                'customer_id': customer_id,
                'customer_name': customer_name,
                'time_of_year': time_of_year
            }
    ):
        log_entry = chunk.ops[0]
        value = log_entry.get("value")
        if isinstance(value, dict) and isinstance(value.get("steps"), list):
            for step in value.get("steps"):
                stream_handler.new_status(step["action"].log.strip("\n"))
        elif isinstance(value, str) and "ChatOpenAI" in log_entry["path"]:
            stream_handler.new_token(value)


with st.form('input_form'):
    with st.expander('Customer Context'):
        preset_example = st.selectbox("select an example case:", customer_examples)
        customer_name_input = st.text_input("customer name:", value=preset_example[0], key='customer_name_input')
        customer_id_input = st.text_input("customerId:", value=preset_example[2], key='customer_id_input')
        time_of_year_input = st.text_input("time of year:", value=preset_example[3], key='time_of_year_input')

    customer_interests_input = st.text_input("customer interests:", value=preset_example[1],
                                             key='customer_interests_input')
    gen_content = st.form_submit_button('Generate')

if gen_content:
    status = st.status("Generating email 🤖")
    stream_handler = StreamHandler(st.empty(), status)
    # Create an event loop: this is needed to run asynchronous functions
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Run the asynchronous function within the event loop
    loop.run_until_complete(get_chain_response(
        customer_interests_input,
        customer_id_input,
        customer_name_input,
        time_of_year_input,
        stream_handler))
    # Close the event loop
    loop.close()
    status.update(label="Finished!", state="complete", expanded=False)
