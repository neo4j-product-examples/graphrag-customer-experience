import asyncio
from datetime import datetime

import streamlit as st
import requests
from langserve import RemoteRunnable


st.set_page_config(layout="wide", page_title='Recommendations')
st.title("Recommendations")
st.subheader("Increase Average Order Value with Customized Recommendations")
st.markdown(":gray[GraphRAG integrates graph embeddings of customer purchase behavior, "
            "user browsing history, and the creativity of LLMs "
            "to generate targeted recommendations.]")
st.markdown('__Product Recommendations:__')


def get_product(product_code):
    response = requests.get(f'http://api:8080/product/?product_code={product_code}')
    if response.status_code == 200:
        return response.json()['product']
    else:
        raise RuntimeError("Failed to fetch data from the server.")


def get_query_param(key: str, default=None):
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
    time_of_year = get_query_param("time_of_year", str(datetime.today()))

    product = get_product(product_code)
    if not customer_interests:
        customer_interests = product['detailDesc']
    with st.container():
        st.markdown(f" ## {product['prodName']}")
        st.markdown(f"{product['detailDesc']}")
        image_urls = []
        for article in product["articleVariants"][:5]:
            image_urls.append(
                f'https://storage.cloud.google.com/neo4j-app-images/hm-articles/images/{article["articleId"]}.jpg')
        st.image(image_urls, width=70)

    status = st.status("Generating recommendations🤖")
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
    st.markdown('---\n:green[You can generate recommendations for any other product and search context '
                'from the] :blue[[search page](http://localhost:8501/search)]:green[. '
                'Just click on the titles of any product in the search results.]')
else:
    st.markdown('This page requires query parameters to generate recommendations. Below are some examples. '
                'Use these links to experiment. \n'
                '* http://localhost:8501/product?product_code=842001&customer_name=Alex+Smith&interests=Oversized'
                '+Sweaters&time_of_year=Feb%2C+2024 \n'
                '* http://localhost:8501/product?product_code=598423&customer_name=Robin+Fischer&interests=denim'
                '+jeans&time_of_year=Feb%2C+2024')
    st.markdown('You can also generate this page for any product and search context from the [search page]('
                'http://localhost:8501/search). Just click on the titles of any product in the search results.')

