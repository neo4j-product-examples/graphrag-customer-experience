from typing import Dict

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes
from neo4j_chains.utils import graph
from neo4j_chains.content_generator import content_chain
from neo4j_chains.product_search import search_chain
from neo4j_chains.recommender_chain import recommendation_chain
app = FastAPI()


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


@app.get("/product/")
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


# Edit this to add the chain you want to add
add_routes(app, content_chain, path="/generate-email")
add_routes(app, search_chain, path="/search")
add_routes(app, recommendation_chain, path="/generate-recommendations")
# add_routes(app, question_answer_chain, path="/support")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
