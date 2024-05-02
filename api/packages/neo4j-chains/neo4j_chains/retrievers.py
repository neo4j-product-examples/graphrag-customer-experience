from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from neo4j_chains.entity_extraction_chain import extraction_chain

# general graph queries. Credentials read from env
graph = Neo4jGraph()

# vector index + graph traversal queries. Credentials read from env
graph_vector_store = Neo4jVector.from_existing_index(
    embedding=SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2"),
    index_name="vector")


def remove_lucene_chars(text: str) -> str:
    """Remove Lucene special characters"""
    special_chars = [
        "+",
        "-",
        "&",
        "|",
        "!",
        "(",
        ")",
        "{",
        "}",
        "[",
        "]",
        "^",
        '"',
        "~",
        "*",
        "?",
        ":",
        "\\",
    ]
    for char in special_chars:
        if char in text:
            text = text.replace(char, " ")
    return text.strip()


def generate_full_text_query(query_str: str) -> str:
    """
    Generate a full-text search query for a given input string.

    This function constructs a query string suitable for a full-text search.
    It processes the input string by splitting it into words and appending a
    similarity threshold (~2 changed characters) to each word, then combines
    them using the AND operator. Useful for mapping entities from user questions
    to database values, and allows for some misspelings.
    """
    full_text_query = ""
    words = [el for el in remove_lucene_chars(query_str).split() if el]
    for word in words[:-1]:
        full_text_query += f" {word}~2 AND"
    full_text_query += f" {words[-1]}~2"
    return full_text_query.strip()


# Fulltext index query
def retrieve_structured_info(prompt: str) -> str:
    """
    Collects the neighborhood of entities mentioned
    in the prompt
    """
    result = ""
    objects = extraction_chain.invoke({"question": prompt})
    for obj in objects.names:
        response = graph.query(
            """CALL db.index.fulltext.queryNodes('entity', $query, {limit:2})
            YIELD node,score
            CALL {
              MATCH (d:Document)<-[:PART_OF]-(:Chunk)-[:HAS_ENTITY]->(node)-[r:!PART_OF]->(neighbor)
              RETURN node.id + ' - ' + type(r) + ' -> ' + neighbor.id + ' source: ' + d.url AS output
              UNION
              MATCH (d:Document)<-[:PART_OF]-(:Chunk)-[:HAS_ENTITY]->(node)<-[r:!HAS_ENTITY]-(neighbor)
              RETURN neighbor.id + ' - ' + type(r) + ' -> ' +  node.id + ' source: ' + d.url AS output
            }
            RETURN output LIMIT 50
            """,
            {"query": generate_full_text_query(obj)},
        )
        result += "\n".join([el['output'] for el in response])
    return result


def retrieve(question: str):
    print(f"Search query: {question}")
    structured_data = retrieve_structured_info(question)
    unstructured_data = [el.page_content for el in graph_vector_store.similarity_search(question)]
    final_data = f"""Structured data:
{structured_data}
Unstructured data:
{"#Document ".join(unstructured_data)}
    """
    print("============== Start Context =================")
    print(final_data)
    print("============== End Context =================")
    return final_data
