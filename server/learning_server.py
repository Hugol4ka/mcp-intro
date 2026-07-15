from fastmcp import FastMCP
import json

mcp = FastMCP("Programming Learning Server")

@mcp.tool()
@mcp.tool()
def search_topics(query: str) -> list:
    """Search for topics in the topics.json file that match the query."""

    with open("data/topics.json", "r") as f:
        donnees = json.load(f)
    
    resultats = []

    for topics, details in donnees.items():

        if not isinstance(details, dict):
            continue

        titre_match = query.lower() in topics.lower()

        concept_match = False

        if "key_concepts" in details and isinstance(details["key_concepts"], list):
            for concept in details["key_concepts"]:
                if query.lower() in concept.lower():
                    concept_match = True
                    break

        if titre_match or concept_match:
            resultats.append(details)

    if not resultats:
        return [{"message": f"No programming topics found matching '{query}'."}]

    return resultats


if __name__ == "__main__":
    mcp.run()
