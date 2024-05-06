import json
from collections import OrderedDict
from typing import Any, Dict, List, Tuple

from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.pydantic_v1 import BaseModel, Field

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

retrieval_query_template = """CALL db.index.vector.queryNodes('product_text_embeddings', $vectorTopK, $embedding)
YIELD node, score

WITH node AS product, score AS searchScore
OPTIONAL MATCH(product)<-[:VARIANT_OF]-(:Article)<-[:PURCHASED]-(:Customer)
-[:PURCHASED]->(a:Article)<-[:PURCHASED]-(:Customer {customerId: $customerId})

WITH count(a) AS purchaseScore, product, searchScore
OPTIONAL MATCH (product)<-[:VARIANT_OF]-(a:Article)

RETURN (1+purchaseScore)*searchScore AS score, 
    collect({colourGroup: a.colourGroupName, graphicalAppearance: a.graphicalAppearanceName, 
        articleId:a.articleId}) AS articleVariants,
    product {.*, `text`: Null, `textEmbedding`: Null, id: Null} AS metadata
ORDER BY score DESC LIMIT $resTopK"""

vector_top_k = 20
res_top_k = 20
embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")
llm = ChatOpenAI(temperature=0, model_name='gpt-4', streaming=True)
graph = Neo4jGraph()


def format_res_dicts(d: Dict) -> Dict:
    res = dict()
    for k, v in d.items():
        if k != "metadata":
            res[k] = v
    for k, v in d['metadata'].items():
        if v is not None:
            res[k] = v
    return res


def retriever(search_input: Tuple[str, str]):
    search_prompt = search_input[0]
    customer_id = search_input[1]
    query_vector = embedding_model.embed_query(search_prompt)
    params = {'vectorTopK': vector_top_k,
              'resTopK': res_top_k,
              'embedding': query_vector,
              'customerId': customer_id}
    query_results = graph.query(retrieval_query_template, params=params)
    # res = json.dumps([format_res_dicts(d) for d in query_results], indent=1)
    res = [format_res_dicts(d) for d in query_results]
    print("================== START SEARCH CONTEXT ==================")
    print(res)
    print("================== END SEARCH CONTEXT ==================")
    return res


class SearchChainInput(BaseModel):
    customer_interests: str
    time_of_year: str
    customer_id: str


class ArticleVariant(BaseModel):
    """Variants of products based on color Design"""
    colourGroup: str
    graphicalAppearance: str
    articleId: int


class Product(BaseModel):
    """A product from the online store"""
    score: float
    productCode: str
    prodName: str
    productCode: int
    garmentGroupName: str
    garmentGroupNo: int
    productTypeName: str
    productTypeNo: int
    detailDesc: str
    productGroupName: str
    url: str
    articleVariants: List[Dict]


class SearchChainOutput(BaseModel):
    output: List[Any]


search_chain0 = (
        RunnableParallel(
            {'context': (lambda x: (x['customer_interests'], x['customer_id'])) | RunnableLambda(retriever),
             'customerInterests': (lambda x: x['customer_interests']),
             'timeofYear': (lambda x: x['time_of_year']),
             })
        # | prompt
        # | llm.with_structured_output(SearchChainOutput)
        | StrOutputParser()).with_types(input_type=SearchChainInput, output_type=SearchChainOutput)



search_chain = ((lambda x: (x['customer_interests'], x['customer_id']))
                | RunnableLambda(retriever)).with_types(input_type=SearchChainInput)
