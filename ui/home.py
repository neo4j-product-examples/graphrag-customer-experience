import os

import streamlit as st

ADVERTISED_ADDRESS = os.getenv('ADVERTISED_ADDRESS')

st.title("GenAI for Customer Experience")
st.subheader("Example Applications Built With Neo4j")
st.markdown(f'''
1. __[Discovery]({ADVERTISED_ADDRESS}:8501/discovery)__: Improve click-through rate with personalized marketing
2. __[Search]({ADVERTISED_ADDRESS}:8501/search)__: Increase conversion with tailored semantic search
3. __[Recommendations]({ADVERTISED_ADDRESS}:8501/recommendations)__: Boost average order value with customized recommendations
4. __[Support]({ADVERTISED_ADDRESS}:8501/support)__: Reduce cost to serve with well-grounded, fact-based, AI scripts
''')
