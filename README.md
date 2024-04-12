# CAD to Graph

This project extracts data from Fusion360 CAD files, transforms it into a structured format, and loads it into a Neo4j graph database.

## Installation

1. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```
    > TODO: Understand requirements management in Fusion360 scripts

2. Create a `.env` file with the following content:
    ```env
    NEO4J_URI=bolt://localhost:7687
    NEO4J_USER=neo4j
    NEO4J_PASSWORD=password
    ```

## Usage

Run the main script follow instruction


#### `requirements.txt`

```plaintext
neo4j
python-dotenv
adsk
```