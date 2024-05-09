from typing import Any, List, Tuple

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel
from langchain.pydantic_v1 import BaseModel, Field

from neo4j_chains.post_filter_search_retriever import search_retriever

prompt = PromptTemplate.from_template("""
You are a personal assistant named Sally for a fashion, home, and beauty company called HRM.
provide a list of recommended products for a customer given
- the current season / time of year: {timeofYear} 
- Recent purchases / searches: {customerInterests}

Please only use the products listed in the context below. Do not come up with or add any new products to the list.
The below candidates are recommended based on the purchase patterns of other customers in the HRM database.
Select the best 4 to 5 product subset from the context that best match the time of year: {timeofYear} and to pair with recent purchases.

# Context:
{context}
""")

vector_top_k = 20
res_top_k = 20


def retriever(search_input: Tuple[str, str]):
    res = search_retriever(search_input, vector_top_k, res_top_k)
    return res


class SearchChainInput(BaseModel):
    customer_interests: str
    time_of_year: str
    customer_id: str


class SearchChainOutput(BaseModel):
    output: List[Any]


search_chain0 = (
        RunnableParallel(
            {'context': (lambda x: (x['customer_interests'], x['customer_id'])) | RunnableLambda(retriever),
             'customerInterests': (lambda x: x['customer_interests']),
             'timeofYear': (lambda x: x['time_of_year']),
             })
        | StrOutputParser()).with_types(input_type=SearchChainInput, output_type=SearchChainOutput)

search_chain = ((lambda x: (x['customer_interests'], x['customer_id']))
                | RunnableLambda(retriever)).with_types(input_type=SearchChainInput)
