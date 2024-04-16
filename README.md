# README.md for COMP 6741 Project-1: Roboprof

## Team AK_G_04: 
Aryan Saxena - 40233170

Benjamin Douglas - 40264251

## Overview
The Roboprof project aims to transform educational datasets into a semantic web format using RDF (Resource Description Framework). This allows for advanced querying and interlinking of data, reflecting the complex structure of academic institutions.

## Data Structure

### CSVs
Our project utilizes CSV files derived from Concordia University's open data portal. These files form the foundation of our RDF framework:

- `data.csv`: Course information including IDs, titles, units, descriptions, prerequisites, and equivalents.
- `lectures.csv`: Details of individual lectures like IDs, numbers, names, and content.
- `students.csv`: Student records, including names, ID numbers, emails, courses taken, grades, and competencies.
- `topics.csv`: Topics covered in lectures and courses with respective IDs, names, and resource links.

### Turtle Files
We convert the CSV files into Turtle (.ttl) format for RDF:

- `courses.ttl`
- `lectures.ttl`
- `students.ttl`
- `universities.ttl`
- `topics.ttl`

## Implementation Steps

1. **Environment Setup:**
   - Libraries: pandas, rdflib, SPARQLWrapper.
   - Path definitions for CSV sources and TTL destinations.

2. **RDF Graph Creation:**
   - Instantiate RDF Graphs for each TTL file.
   - Bind necessary namespaces for RDF triples.

3. **Data Population and Serialization:**
   - Convert CSV data to RDF triples and serialize them into TTL files.
   - Ensure data integrity and handle missing values.
   - Validate URIs to prevent RDF issues.

4. **Error Handling:**
   - Graceful handling of missing data and errors.
   - Validation of URIs for RDF triples.

5. **RDF Store Integration:**
   - The TTL files are ready for integration with RDF stores or other semantic applications.

## Execution

- Run `DataGeneration.ipynb` to populate and serialize Turtle files.
- Use `queries.py` with predefined SPARQL queries to fetch and manipulate RDF data.

## Repositories and File Management

- CSVs and TTL files are stored in corresponding directories.
- Queries are saved individually as `.csv` files for transparency and ease of access.

## Rasa Chatbot Integration

- The RDF data can be integrated with Rasa chatbots for conversational querying.
- The chatbot can fetch data from RDF stores and provide answers to user queries.
- Chatbot can answer all the queries related to the RDF data, it is done using Actions.py.
- Actions.py has all the functions to fetch the data from the RDF files and return the response to the user.
- The chatbot can answer queries related to courses, lectures, students, universities, and topics.

### Files updated in Chatbot
- `actions.py`
- `domain.yml`
- `data_generation.py`
- `config.yml`
- `credentials.yml`
- `endpoints.yml`
- `nlu.yml`
- `stories.yml`

## Conclusion
The Roboprof project demonstrates the transformation of educational datasets into RDF format for advanced querying and integration with semantic web applications. The RDF data can be used for various purposes, including chatbots, recommendation systems, and data analysis.
