import os
from typing import List, Tuple, Any

from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough

from neo4j_chains.condense_question_chain import condense_question
from neo4j_chains.utils import embedding_model, llm

template = (
    "You are an assistant that helps customers with their questions. "
    "You work for for XYZBrands, a fashion, home, and beauty company. "
    "If you require follow up questions, "
    "make sure to ask the user for clarification. Make sure to include any "
    "available options that need to be clarified in the follow up questions. "
    "Embed url links as sources when made available. "
    "Answer the question based only on the below Rules and AdditionalContext. "
    "The rules should be respected as absolute fact, never provide advise that contradicts the rules. "
    """
    # Rules
    {rules}
    
    # AdditionalContext
    {additionalContext}
    
    # Question: 
    {question}
        
    # Answer:
    """
)

neo4j_url = os.getenv('SUPPORT_NEO4J_URI')
neo4j_username = os.getenv('SUPPORT_NEO4J_USERNAME')
neo4j_password = os.getenv('SUPPORT_NEO4J_PASSWORD')
neo4j_database_name = os.getenv('SUPPORT_NEO4J_DATABASE')

vector_index_name = 'TBD'
graph_retrieval_query = 'TBD'
vector_top_k = 20
res_top_k = 20

support_graph = Neo4jGraph(
    url=neo4j_url,
    username=neo4j_username,
    password=neo4j_password,
    database=neo4j_database_name
)

vector_store = Neo4jVector.from_existing_index(
    embedding=embedding_model,
    url=neo4j_url,
    username=neo4j_username,
    password=neo4j_password,
    database=neo4j_database_name,
    index_name=vector_index_name,
    retrieval_query=graph_retrieval_query
)


class ChainInput(BaseModel):
    input: str
    chat_history: List[Tuple[str, str]] = Field(
        ..., extra={"widget": {"type": "chat", "input": "input", "output": "output"}}
    )


class Output(BaseModel):
    output: Any


def print_pass(x):
    print(x)
    print(type(x))
    return x


prompt = ChatPromptTemplate.from_template(template)

qa_chain = (
        RunnableParallel(
            {
                "context": condense_question | vector_store.as_retriever(search_kwargs={'k': vector_top_k}),
                "question": RunnablePassthrough(),
            }
        )
        | prompt
        | llm
        | StrOutputParser()
).with_types(input_type=ChainInput, output_type=Output)
