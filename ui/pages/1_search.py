from urllib.parse import quote_plus

import streamlit as st
from langserve import RemoteRunnable

st.set_page_config(layout="wide")
st.title("Search")
st.subheader("Increase Conversion with Tailored Semantic Search")
st.markdown(":gray[Similar to Discovery, "
            "GraphRAG integrates customer purchasing patterns with "
            "unstructured product descriptions for "
            "personalized semantic search.]")

customer_examples = [
    [
        'Alex Smith',
        'denim jeans',
        'daae10780ecd14990ea190a1e9917da33fe96cd8cfa5e80b67b4600171aa77e0',
        'July, 2024',
    ],
    [
        'Robin Fischer',
        'denim jeans',
        '819f4eab1fd76b932fd403ae9f427de8eb9c5b64411d763bb26b5c8c3c30f16f',
        'July, 2024',
    ],
    [
        'Alex Smith',
        'western boots',
        'daae10780ecd14990ea190a1e9917da33fe96cd8cfa5e80b67b4600171aa77e0',
        'July, 2024',
    ],
    [
        'Chris Johnson',
        'Oversized Sweaters',
        '44b0898ecce6cc1268dfdb0f91e053db014b973f67e34ed8ae28211410910693',
        'Feb, 2024',
    ],
    [
        'Robin Fischer',
        'denim jeans',
        '819f4eab1fd76b932fd403ae9f427de8eb9c5b64411d763bb26b5c8c3c30f16f',
        'Feb, 2024',
    ],
    [
        'Alex Smith',
        'oversized sweaters',
        'daae10780ecd14990ea190a1e9917da33fe96cd8cfa5e80b67b4600171aa77e0',
        'Feb, 2024',
    ],
]

remote_runnable = RemoteRunnable("http://api:8080/search/")

col1, col2 = st.columns([0.35, 0.65])

with col1:
    st.markdown('#### Product Search:')
    with st.form('input_form'):
        with st.expander('User Context'):
            preset_example = st.selectbox("select an example case:", customer_examples)
            customer_name_input = st.text_input("customer name:", value=preset_example[0], key='customer_name_input')
            customer_id_input = st.text_input("customerId:", value=preset_example[2], key='customer_id_input')
            time_of_year_input = st.text_input("time of year:", value=preset_example[3], key='time_of_year_input')

        customer_interests_input = st.text_input("search prompt:", value=preset_example[1],
                                                 key='customer_interests_input')
        gen_content = st.form_submit_button('search')

with col2:
    n_cards_per_row = 2
    if gen_content:
        st.write("#### Results: ")
        search_results = remote_runnable.invoke({
            'customer_interests': customer_interests_input,
            'time_of_year': time_of_year_input,
            'customer_id': customer_id_input
        })
        for k in range(len(search_results)):
            row = search_results[k]
            i = k % n_cards_per_row
            if i == 0:
                cols = st.columns(n_cards_per_row)
            # draw the card
            with cols[k % n_cards_per_row]:
                with st.container(height=400):
                    product_page_url = 'http://localhost:8501/recommendations?' + \
                                       '&'.join([f'product_code={row["productCode"]}',
                                                 f'customer_name={quote_plus(customer_name_input)}',
                                                 f'interests={quote_plus(customer_interests_input)}',
                                                 f'time_of_year={quote_plus(time_of_year_input)}'
                                                 ])
                    st.markdown(f"## [{row['prodName']}]({product_page_url})")
                    image_urls = []
                    for article in row["articleVariants"][:3]:
                        image_urls.append(
                            f'https://storage.cloud.google.com/neo4j-app-images/hm-articles/images/{article["articleId"]}.jpg')
                    st.image(image_urls, width=70)
                    st.markdown(f"{row['detailDesc']}")

