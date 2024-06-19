from typing import Tuple, List, Dict

from neo4j_chains.utils import embedding_model, graph, format_res_dicts

search_query_template = """CALL db.index.vector.queryNodes('product_text_embeddings', $vectorTopK, $embedding)
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


def search_retriever(search_input: Tuple[str, str], vector_top_k: int, res_top_k: int) -> List[Dict]:
    search_prompt = search_input[0]
    customer_id = search_input[1]
    query_vector = embedding_model.embed_query(search_prompt)
    params = {'vectorTopK': vector_top_k,
              'resTopK': res_top_k,
              'embedding': query_vector,
              'customerId': customer_id}
    query_results = graph.query(search_query_template, params=params)
    res = [format_res_dicts(d) for d in query_results]
    print("================== START SEARCH CONTEXT ==================")
    print(res)
    print("================== END SEARCH CONTEXT ==================")
    return res


def fetch_product(product_code: int) -> Dict:
    """
    Fetches a product by product code.
    """
    data = graph.query("""
    MATCH (p:Product {productCode:$productCode})<-[:VARIANT_OF]-(a:Article)
    WITH p, collect({colourGroup: a.colourGroupName, graphicalAppearance: a.graphicalAppearanceName, 
            articleId:a.articleId}) AS articleVariants
    RETURN p {.*, `text`: Null, `textEmbedding`: Null, id: Null, articleVariants} AS product
    """, params={'productCode': product_code})
    return data[0]
