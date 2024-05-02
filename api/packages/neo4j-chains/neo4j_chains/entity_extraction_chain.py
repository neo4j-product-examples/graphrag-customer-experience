from typing import List
from langchain_openai import ChatOpenAI
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

small_llm = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo', streaming=True)


class Entities(BaseModel):
    """Identifying information about Objects."""

    names: List[str] = Field(
        ...,
        description=("All the Components, Objects, Tools, "
                     "Processes, Products, Concepts, and Issues that appear in the text")
    )


extraction_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are extracting organization and person entities from the text.",
        ),
        (
            "human",
            "Use the given format to extract information from the following "
            "input: {question}",
        ),
    ]
)

extraction_chain = extraction_prompt | small_llm.with_structured_output(Entities)
