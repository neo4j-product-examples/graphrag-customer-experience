from typing import List, Tuple, Any
from langchain.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from neo4j_chains.retrievers import retrieve
from neo4j_chains.condense_question_chain import condense_question

llm = ChatOpenAI(temperature=0, model="gpt-4", streaming=True)


template = (
    "You are an assistant that helps customers with their truck vehicle questions. "
    "If you require follow up questions, "
    "make sure to ask the user for clarification. Make sure to include any "
    "available options that need to be clarified in the follow up questions. "
    "Embed url links as sources when made available. "
    "Answer the question based only on the following context:"
    """{context}
    
        Question: {question}
        Use natural language and be concise.
        Answer:
    """
)

def print_pass(x):
    print(x)
    print(type(x))
    return x

class ChainInput(BaseModel):
    input: str
    chat_history: List[Tuple[str, str]] = Field(
        ..., extra={"widget": {"type": "chat", "input": "input", "output": "output"}}
    )

class Output(BaseModel):
    output: Any

prompt = ChatPromptTemplate.from_template(template)

qa_chain = (
    RunnableParallel(
        {
            "context": RunnableLambda(print_pass) | condense_question | RunnableLambda(print_pass) | retrieve,
            "question": RunnablePassthrough(),
        }
    )
    | prompt
    | llm
    | StrOutputParser()
).with_types(input_type=ChainInput, output_type=Output)



