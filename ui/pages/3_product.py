import asyncio
from datetime import datetime

import streamlit as st
import requests
from langserve import RemoteRunnable


def get_product(product_code):
    response = requests.get(f'http://api:8080/product/?product_code={product_code}')
    if response.status_code == 200:
        return response.json()['product']
    else:
        raise RuntimeError("Failed to fetch data from the server.")

def get_query_param(key:str , default = None):
    if key in st.query_params:
        return st.query_params[key]
    return default


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

async def get_chain_response(product_code: int,
                             customer_name: str,
                             product_description: str,
                             customer_interests: str,
                             time_of_year: str,
                             stream_handler: StreamHandler):
    url = "http://api:8080/generate-recommendations/"
    remote_runnable = RemoteRunnable(url)
    async for chunk in remote_runnable.astream_log(
            {
                'product_code': product_code,
                'customer_name': customer_name,
                'product_description': product_description,
                'customer_interests': customer_interests,
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

product_code = get_query_param('product_code')
if product_code:
    customer_name = get_query_param("customer_name", "name unknown")
    customer_interests = get_query_param("interests")
    customer_id = get_query_param("customer_id", "")
    time_of_year = get_query_param("time_of_year", str(datetime.today()))

    product = get_product(product_code)
    if not customer_interests:
        customer_interests = product['detailDesc']
    with st.container():
        inner_col1, inner_col2 = st.columns(2)
        with inner_col1:
            st.markdown(f" Image to go here")
            for article in product["articleVariants"]:
                st.image(
                    f'https://storage.cloud.google.com/neo4j-app-images/hm-articles/images/{article["articleId"]}.jpg')
        with inner_col2:
            st.markdown(f" ## {product['prodName'].strip()}")
            st.markdown(f" ### {product['productTypeName'].strip()}")
        st.markdown(f"**{product['detailDesc']}**")

    status = st.status("Generating content🤖")
    stream_handler = StreamHandler(st.empty(), status)
    # Create an event loop: this is needed to run asynchronous functions
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Run the asynchronous function within the event loop
    loop.run_until_complete(get_chain_response(
        product_code,
        customer_name,
        f'{product["prodName"]}: {product["detailDesc"]}',
        customer_interests,
        time_of_year,
        stream_handler))
    # Close the event loop
    loop.close()
    status.update(label="Finished!", state="complete", expanded=False)