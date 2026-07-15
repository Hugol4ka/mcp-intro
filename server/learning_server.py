from fastmcp import FastMCP
import json

mcp = FastMCP("Programming Learning Server")

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

@mcp.tool()
def get_topic_details(topic_id: str) -> dict:
    """Return full information for a topic by id."""
    try:
        with open("data/topics.json", "r") as f:
            donnees = json.load(f)

        if isinstance(donnees, dict):
            sujets = [donnees]
        else:
            sujets = donnees

        # Recherche du sujet correspondant à l'ID
        for sujet in sujets:
            if sujet.get("id") == topic_id:
                return sujet

        # Si l'ID n'a pas été trouvé
        return {"error": f"Topic with id '{topic_id}' not found."}

    except FileNotFoundError:
        return {"error": "The data file 'data/topics.json' was not found."}
    except json.JSONDecodeError:
        return {"error": "Failed to parse 'data/topics.json'. Invalid JSON structure."}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

@mcp.resource("topics://catalog")
def get_topic_catalog() -> str:
    """Return the list of available topic ids and titles."""
    with open("data/topics.json", "r") as f:
        donnees = json.load(f)
    
    if isinstance(donnees, dict):
        sujets = [donnees]
    else:
        sujets = donnees
    
    catalog = []
    for sujet in sujets:
        catalog.append({
            "id": sujet.get("id"),
            "title": sujet.get("title")
            })
    return json.dumps(catalog, indent=2)

if __name__ == "__main__":
    mcp.run()
