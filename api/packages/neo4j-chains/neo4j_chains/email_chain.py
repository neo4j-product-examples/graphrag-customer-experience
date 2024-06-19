import json
from typing import Any, Dict, Tuple

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel
from langchain.pydantic_v1 import BaseModel

from neo4j_chains.queries import search_retriever
from neo4j_chains.utils import llm

prompt = PromptTemplate.from_template("""
You are a personal assistant named Sally for a fashion, home, and beauty company called HRM.
write an email to {customerName}, one of your customers, to recommend and summarize products based on: 
- the current season / time of year: {timeofYear} 
- Their recent searches & interests: {customerInterests}

Please only mention the products listed in the context below. Do not come up with or add any new products to the list.
The below candidates are recommended based on the purchase patterns of other customers in the HRM database.
Select the best 4 to 5 product subset from the context that best match 
the time of year: {timeofYear} and the customers interests.
Each product comes with an https `url` field. 
Make sure to provide that https url with descriptive name text in markdown for each product.

# Context:
{context}
""")

vector_top_k = 20
res_top_k = 20


def retriever(search_input: Tuple[str, str]):
    res_list = search_retriever(search_input, vector_top_k, res_top_k)
    res = json.dumps(res_list, indent=1)
    return res


class ContentChainInput(BaseModel):
    customer_interests: str
    customer_id: str
    customer_name: str
    time_of_year: str


class ContentChainOutput(BaseModel):
    output: Any


content_chain = (
        RunnableParallel(
            {'context': (lambda x: (x['customer_interests'], x['customer_id'])) | RunnableLambda(retriever),
             'customerName': (lambda x: x['customer_name']),
             'customerInterests': (lambda x: x['customer_interests']),
             'timeofYear': (lambda x: x['time_of_year']),
             })
        | prompt
        | llm
        | StrOutputParser()).with_types(input_type=ContentChainInput, output_type=ContentChainOutput)
