import streamlit as st
from langserve import RemoteRunnable

remote_runnable = RemoteRunnable("http://api:8080/search/")

examples = [
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



with st.expander('User Context'):
    preset_example = st.selectbox("select an example case:", examples)
    customer_name_input = st.text_input("customer name:", value=preset_example[0], key='customer_name_input')
    customer_id_input = st.text_input("customerId:", value=preset_example[2], key='customer_id_input')
    time_of_year_input = st.text_input("time of year:", value=preset_example[3], key='time_of_year_input')

customer_interests_input = st.text_input("Search for products:", value=preset_example[1],
                                         key='customer_interests_input')

n_cards_per_row = 3
if customer_interests_input:
    search_results = remote_runnable.invoke({
        'customer_interests': customer_interests_input,
        'time_of_year': time_of_year_input,
        'customer_id': customer_id_input
    })
    for k in range(len(search_results)):
        row = search_results[k]
        i = k % n_cards_per_row
        if i == 0:
            st.write("---")
            cols = st.columns(n_cards_per_row, gap="large")
        # draw the card
        with cols[k % n_cards_per_row]:
            with st.container(height=500):
                inner_col1, inner_col2 = st.columns(2)
                with inner_col1:
                    st.markdown(f" Image to go here")
                    # st.image(f'img/{row["prodName"][:-4]}.jpg')
                with inner_col2:
                    st.markdown(f" ## {row['prodName'].strip()}")
                    st.markdown(f" ### {row['productTypeName'].strip()}")
                st.markdown(f"**{row['detailDesc']}**")
