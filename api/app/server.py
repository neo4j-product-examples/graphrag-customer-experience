from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes
from neo4j_chains.content_generator import content_chain
app = FastAPI()


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


# Edit this to add the chain you want to add
add_routes(app, content_chain, path="/generate-email")
#add_routes(app, question_answer_chain, path="/search-assist")
#add_routes(app, question_answer_chain, path="/support")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
