from fastmcp import FastMCP
import json

mcp = FastMCP("Programming Learning Server")

@mcp.tool()
def search_topics(query: str) -> list:
    """Search for topics in the topics.json file that match the query."""

    with open("data/topics.json", "r") as f:
        donnees = json.load(f)
    
    # Assurer que donnees soit traité comme une liste
    sujets = [donnees] if isinstance(donnees, dict) else donnees
    
    resultats = []

    for topic in sujets:
        # On extrait les champs textuels en gérant les valeurs absentes
        topic_id = topic.get("id", "")
        title = topic.get("title", "")
        summary = topic.get("summary", "")

        # Correspondance dans l'id, le titre ou le résumé
        match_texte = (
            query.lower() in topic_id.lower() or
            query.lower() in title.lower() or
            query.lower() in summary.lower()
        )

        # Correspondance dans les concepts clés (key_concepts)
        match_concept = False
        key_concepts = topic.get("key_concepts", [])
        if isinstance(key_concepts, list):
            for concept in key_concepts:
                if query.lower() in concept.lower():
                    match_concept = True
                    break

        if match_texte or match_concept:
            resultats.append(topic)

    if not resultats:
        return [{"message": f"No programming topics found matching '{query}'."}]

    return resultats

@mcp.tool()
def get_topic_details(topic_id: str) -> dict:
    """Return full information for a topic by id."""
    try:
        with open("data/topics.json", "r") as f:
            donnees = json.load(f)

        sujets = [donnees] if isinstance(donnees, dict) else donnees

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
    
    sujets = [donnees] if isinstance(donnees, dict) else donnees
    
    catalog = []
    for sujet in sujets:
        catalog.append({
            "id": sujet.get("id"),
            "title": sujet.get("title")
            })
    return json.dumps(catalog, indent=2)

if __name__ == "__main__":
    mcp.run()
