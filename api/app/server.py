from typing import Dict

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes
from neo4j_chains.queries import fetch_product
from neo4j_chains.email_chain import content_chain
from neo4j_chains.search_chain import search_chain
from neo4j_chains.recommender_chain import recommendation_chain
from neo4j_chains.support_chain import qa_chain
app = FastAPI()


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


@app.get("/product/")
def get_product(product_code: int) -> Dict:
    return fetch_product(product_code)


# Edit this to add the chain you want to add
add_routes(app, content_chain, path="/generate-email")
add_routes(app, search_chain, path="/search")
add_routes(app, recommendation_chain, path="/generate-recommendations")
add_routes(app, qa_chain, path="/support")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
