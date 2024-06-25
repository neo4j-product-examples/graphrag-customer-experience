# GraphRAG Customer Experience Example
### __:warning: This Repo is Work in Progress :warning:__

This project demonstrates how to implement GraphRAG for various touch points in the customer journey including:

1. __Discovery__: Improve click-through rate with personalized marketing
2. __Search__: Increase conversion with tailored semantic search
3. __Recommendations__: Boost average order value with customized recommendations
4. __Support__: Reduce cost to serve with well-grounded, fact-based, AI scripts

## Docker containers
To start the project, run the following command:

```
docker-compose up
```

Open `http://localhost:8501` in your browser to interact with the assistant.

## Environment Setup

You need to define the following environment variables in the `.env` file.

```
# Main Product Graph
NEO4J_URI=<YOUR_NEO4J_URI>
NEO4J_USERNAME=<YOUR_NEO4J_USERNAME>
NEO4J_PASSWORD=<YOUR_NEO4J_PASSWORD>
NEO4J_DATABASE=neo4j

#Customer Support Graph
SUPPORT_NEO4J_URI=<YOUR_NEO4J_URI>
SUPPORT_NEO4J_USERNAME=<YOUR_NEO4J_USERNAME>
SUPPORT_NEO4J_PASSWORD=<YOUR_NEO4J_PASSWORD>
SUPPORT_NEO4J_DATABASE=neo4j

#OpenAI
OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>
NEO4J_URI=<YOUR_NEO4J_URI>
NEO4J_USERNAME=<YOUR_NEO4J_USERNAME>
NEO4J_PASSWORD=<YOUR_NEO4J_PASSWORD>
```

## Docker containers

This project contains the following services wrapped as docker containers

1. **API**: Uses LangChain to retrieve messaging from Neo4j and call OpenAI LLM.
2. **UI**: Simple streamlit chat user interface. Available on `localhost:8501`.

## Populating Databases

For the main graph (powering Discovery, Search, and Recommendations)
you can load the database with [this notebook](https://github.com/neo4j-product-examples/graphrag-examples/blob/main/load-data/hm-data.ipynb). This uses the [H&M Personalized Fashion Recommendations Dataset](https://www.kaggle.com/competitions/h-and-m-personalized-fashion-recommendations/data), a sample of real customer purchase data that includes rich information around products including names, types, descriptions, department sections, etc.

Below is the graph data model we will use for the main graph:
<img src="images/hm-data-model.png" alt="summary" width="1000"/>

For the support graph you can use the database from this [customer-support-dummy-data.dump](customer-support-dummy-data.dump) dump file. It was created using the [LLM Graph Builder](https://neo4j.com/labs/genai-ecosystem/llm-graph-builder/) from some data scrapped off the web. 

## Contributions

Contributions are welcome!