import json
from collections import OrderedDict
from typing import Any, Dict, Tuple

from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.pydantic_v1 import BaseModel, Field

prompt = PromptTemplate.from_template("""
You are a personal assistant named Sally for a fashion, home, and beauty company called HRM.
Your customer, {customerName}, is currently browsing the website. 
Please write an engaging message to them recommending and summarizing products that pair well
with their interests and the item they are currently viewing given: 
- Item they are currently viewing: {productDescription}
- The current season / time of year: {timeofYear} 
- Recent searches: {customerInterests}

Please only mention the product candidates listed in the context below. 
Do not come up with or add any new products to the list.
The below candidates are recommended based on the purchase patterns of other customers in the HRM database.
Select the best 4 to 5 product subset from the context that best match the time of year: {timeofYear} and to pair 
with the current product being viewed.
Each product comes with an http `url` field. 
Make sure to provide that http url with descriptive name text in markdown for each product. Do not alter the url.

# Context:
{context}
""")

retrieval_query_template = """
MATCH(searchProduct:Product {productCode: $productCode})<-[:VARIANT_OF]-(searchArticle:Article)
WHERE  searchArticle.graphEmbedding IS NOT NULL
CALL db.index.vector.queryNodes('article_graph_embeddings', $vectorTopK, searchArticle.graphEmbedding) YIELD node, score
WHERE score < 1.0
MATCH (node)-[:VARIANT_OF]->(product)
RETURN product.`text` AS text, 
    max(score) AS score, 
    product {.*, `text`: Null, `textEmbedding`: Null, id: Null} AS metadata
ORDER by score DESC LIMIT $resTopK"""

vector_top_k = 30
res_top_k = 20
embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")
llm = ChatOpenAI(temperature=0, model_name='gpt-4', streaming=True)
graph = Neo4jGraph()


def format_res_dicts(d: Dict) -> Dict:
    res = OrderedDict()
    for k, v in d.items():
        if k != "metadata":
            res[k] = v
    for k, v in d['metadata'].items():
        if v is not None:
            res[k] = v
    return res


def retriever(product_code):
    params = {'productCode': product_code,
              'vectorTopK': vector_top_k,
              'resTopK': res_top_k}
    query_results = graph.query(retrieval_query_template, params=params)
    res = json.dumps([format_res_dicts(d) for d in query_results], indent=1)
    print("================== START CONTENT CONTEXT ==================")
    print(res)
    print("================== END CONTENT CONTEXT ==================")
    return res


class RecommendationChainInput(BaseModel):
    product_code: int
    customer_name: str
    product_description: str
    customer_interests: str
    time_of_year: str


class RecommendationChainOutput(BaseModel):
    output: Any


recommendation_chain = (
        RunnableParallel(
            {'context': (lambda x: x['product_code']) | RunnableLambda(retriever),
             'customerName': (lambda x: x['customer_name']),
             'productDescription': (lambda x: x['product_description']),
             'customerInterests': (lambda x: x['customer_interests']),
             'timeofYear': (lambda x: x['time_of_year']),
             })
        | prompt
        | llm
        | StrOutputParser()).with_types(
    input_type=RecommendationChainInput,
    output_type=RecommendationChainOutput)
