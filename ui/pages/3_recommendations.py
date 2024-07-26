import asyncio
import os
from datetime import datetime
from typing import Dict

import streamlit as st
import requests
from langserve import RemoteRunnable

st.set_page_config(layout="wide", page_title='Recommendations')
st.title("Recommendations")
st.subheader("Increase Average Order Value with Customized Recommendations")
st.markdown(":gray[GraphRAG integrates graph embeddings of customer purchase behavior, "
            "user browsing history, and the creativity of LLMs "
            "to generate targeted recommendations.]")
st.markdown('___')

ADVERTISED_ADDRESS = os.getenv('ADVERTISED_ADDRESS')

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
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def new_token(self, token: str) -> None:
        self.text += token
        self.container.markdown(self.text, unsafe_allow_html=True)


async def get_chain_response(params: Dict, url: str, stream_handler: StreamHandler):
    remote_runnable = RemoteRunnable(url)
    async for data in remote_runnable.astream(params):
        stream_handler.new_token(data)


def generate_recommendations(product_code: int,
                             customer_name: str,
                             customer_interests: str,
                             time_of_year: str,
                             text_vector_only: bool = False):
    if text_vector_only:
        params = {
            'customer_name': customer_name,
            'product_description': f'{product["prodName"]}: {product["detailDesc"]}',
            'customer_interests': customer_interests,
            'time_of_year': time_of_year}
        url = "http://api:8080/generate-text-vector-only-recommendations/"
    else:
        params = {
            'product_code': product_code,
            'customer_name': customer_name,
            'product_description': f'{product["prodName"]}: {product["detailDesc"]}',
            'customer_interests': customer_interests,
            'time_of_year': time_of_year}
        url = "http://api:8080/generate-recommendations/"
    stream_handler = StreamHandler(st.empty())
    # Create an event loop: this is needed to run asynchronous functions
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Run the asynchronous function within the event loop
    loop.run_until_complete(get_chain_response(params, url, stream_handler))
    # Close the event loop
    loop.close()


product_code = get_query_param('product_code')
if product_code:
    customer_name = get_query_param("customer_name", "name unknown")
    customer_interests = get_query_param("interests")
    time_of_year = get_query_param("time_of_year", str(datetime.today()))

    product = get_product(product_code)
    if not customer_interests:
        customer_interests = product['detailDesc']
    with st.container():
        st.markdown(f" ### {product['prodName']}")
        st.markdown(f"{product['detailDesc']}")
        image_urls = []
        for article in product["articleVariants"][:5]:
            image_urls.append(
                f'https://storage.cloud.google.com/neo4j-app-images/hm-articles/images/{article["articleId"]}.jpg')
        st.image(image_urls, width=70)
    st.markdown('___')
    st.markdown('#### Product Recommendations')

    if 'generate' not in st.session_state:
        st.session_state.generate = False

    def generate_button():
        st.session_state.generate = True

    wcol1, wcol2, wcol3 = st.columns([0.2, 0.1, 0.8])
    with wcol1:
        compare_graph_rag = st.toggle("Compare Vector Only")
    with wcol2:
        st.button('Generate', on_click=generate_button)
    if st.session_state.generate:
        status = st.status("Generating recommendations🤖")
        col1, col2 = st.columns(2)
        if compare_graph_rag:
            with col1:
                st.subheader("Vector Only")
                generate_recommendations(product_code, customer_name, customer_interests, time_of_year, True)
            with col2:
                st.subheader("GraphRAG")
                generate_recommendations(product_code, customer_name, customer_interests, time_of_year)
        else:
            generate_recommendations(product_code, customer_name, customer_interests, time_of_year)
        status.update(label="Finished!", state="complete", expanded=False)
        st.markdown('---\nYou can generate recommendations for any other product and search context '
                    f'from the [search page]({ADVERTISED_ADDRESS}:8501/search). '
                    'Just click on the titles of any product in the search results.')
else:
    st.markdown('#### Product Recommendations')
    st.markdown('This page requires query parameters to generate recommendations. Below are some examples. '
                'Use these links to experiment. \n'
                f'* {ADVERTISED_ADDRESS}:8501/recommendations?product_code=842001&customer_name=Alex+Smith&interests'
                '=Oversized+Sweaters&time_of_year=Feb%2C+2024 \n'
                f'* {ADVERTISED_ADDRESS}:8501/recommendations?product_code=598423&customer_name=Robin+Fischer&interests'
                '=denim+jeans&time_of_year=July%2C+2024')
    st.markdown('You can also generate this page for any product and search context from the [search page]('
                f'{ADVERTISED_ADDRESS}:8501/search). Just click on the titles of any product in the search results.')
