# GraphRAG Customer Experience Example

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

To start and rebuild (after changing env variables or code), run

```
docker-compose up --build
```

To stop the app, run

```
docker-compose down
```

Open `http://localhost:8501` in your browser to interact with the app.

## Environment Setup

You need to define the following environment variables in the `.env` file.

```
#Main Product Graph
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

# Other
# change to public IP address when deploying
ADVERTISED_ADDRESS="http://localhost"
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


## Databricks / Spark Loading Scripts
*\[TODO\]: Update to most recent schema and source files to work with demo.*

See [here](https://github.com/neo4j-product-examples/ds-spark-examples/tree/main/spark-databricks-delta-lake) for scripts to stage & load H&M data from Databricks.


## Deploying in the Cloud

These directions are written for GCP VMs but should be repeatable with minor changes on other cloud providers.

### 1 Create Instance
* Create a Google Cloud VM instance.
* Then create firewall rules to allow traffic on ports 8080 and 8501
* Next resize the disk with the below command (often defaults or for 10GB disk which will cause problems).
`gcloud compute disks resize <boot disk name> --size 100`
Then restart the instance for the boot disk change to take effect

### 2 Setup & Config
Easiest with root access for demo purposes, so first:

    sudo su

Then you'll need to install git and clone this repo:

    apt install -y git
    mkdir -p /app
    cd /app
    git clone https://github.com/neo4j-product-examples/graphrag-customer-experience.git
    cd graphrag-customer-experience

Let's install python & pip:

    apt install -y python
    apt install -y pip

Now, install docker [per these directions](https://docs.docker.com/engine/install/debian/#install-using-the-repository)

Then install docker-compose
    
    apt install docker-compose

Now update the configs in a `.env` file as documented above


### 3 Run
build and run the container with below command (the first time can take a while to build)

    docker-compose up

Optionally, you can run in a detached state to ensure the app continues even if you disconnect from the vm instance:

    docker-compose up -d

To stop the app run

    docker-compose down
## Contributions

Contributions are welcome!