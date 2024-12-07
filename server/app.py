from flask import Flask, request, jsonify
from rdflib import Graph

app = Flask(__name__)

# Load the ontology
ontology_graph = Graph()
ontology_graph.parse("ontology.rdf", format="xml")  # Adjust format if using Turtle or another serialization

@app.route("/query", methods=["GET"])
def query_ontology():
    """
    API endpoint to query the ontology using SPARQL.
    Accepts a `query` parameter.
    """
    sparql_query = request.args.get("query")
    if not sparql_query:
        return jsonify({"error": "No SPARQL query provided"}), 400

    try:
        # Execute the SPARQL query
        results = ontology_graph.query(sparql_query)

        # Format the results
        response_data = []
        for row in results:
            response_data.append({str(var): str(row[var]) for var in row.labels})
        
        return jsonify({"results": response_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return jsonify({"message": "Ontology API is running. Use the /query endpoint to make SPARQL queries."})

if __name__ == "__main__":
    app.run(debug=True)
