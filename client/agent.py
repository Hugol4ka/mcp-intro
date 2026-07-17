import asyncio
import os
import sys
import json
from fastmcp import Client
from openai import OpenAI

# 1. On initialise le client MCP local pour charger nos outils
mcp_client = Client("server/learning_server.py")

# 2. On configure le client pour qu'il cible ton Ollama local
# Ollama expose une API identique à celle d'OpenAI sur le port 11434
local_client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # Requis par la bibliothèque mais ignoré par Ollama
)

async def run_agent():
    print("Démarrage de l'agent 100% local (Ollama + MCP)...")

    # Récupération du sujet demandé en argument de ligne de commande
    if len(sys.argv) <= 1:
        print("Erreur : sujet manquant.")
        print("Utilisation : python client/agent.py \"<votre sujet>\"")
        sys.exit(1)

    user_prompt = " ".join(sys.argv[1:])
    
    # 3. On ouvre la session MCP
    async with mcp_client as session:
        mcp_tools = await session.list_tools()
        
        # Adaptation des outils MCP pour Ollama
        ollama_tools = []
        for tool in mcp_tools:
            ollama_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            })

        print(f"Envoi de la requête à Ollama : '{user_prompt}'...")

        messages = [
            {
                "role": "system",
                "content": (
                    "Tu es un tuteur en programmation. Tu dois aider l'utilisateur à apprendre "
                    "la programmation. Tu dois obligatoirement utiliser tes outils pour chercher "
                    "des sujets et obtenir leurs détails. N'invente aucun détail absent des outils."
                )
            },
            {"role": "user", "content": user_prompt}
        ]

        # 4. Premier appel à Ollama avec qwen3:14b
        response = local_client.chat.completions.create(
            model="qwen3:14b",
            messages=messages,
            tools=ollama_tools,
            tool_choice="auto"
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            print("Ollama a décidé d'appeler un outil MCP...")
            messages.append(response_message)

            topic_not_found = False

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)
                
                print(f"-> Exécution de l'outil local : {function_name} avec {arguments}")
                
                # Appel de l'outil sur ton serveur MCP
                tool_result = await session.call_tool(function_name, arguments)
                result_str = str(tool_result)

                # Vérification : le serveur n'a rien trouvé pour ce sujet
                if function_name == "search_topics" and "No programming topics found" in result_str:
                    topic_not_found = True
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": result_str
                })

            if topic_not_found:
                print("Aucun sujet correspondant trouvé dans la base locale.")
                response_text = (
                    f"Aucun sujet correspondant à '{user_prompt}' n'a été trouvé dans la base locale. "
                    "Merci de reformuler votre demande ou de choisir un sujet disponible."
                )
            else:
                # Deuxième appel à Ollama pour rédiger la réponse finale
                print("Génération de la réponse finale...")
                final_response = local_client.chat.completions.create(
                    model="qwen3:14b",
                    messages=messages
                )
                response_text = final_response.choices[0].message.content
        else:
            response_text = response_message.content

        print("\n=== Réponse de l'Agent Local ===\n")
        print(response_text)

        # 6. Sauvegarde du résultat
        os.makedirs("output", exist_ok=True)
        with open("output/sample_agent_response.md", "w", encoding="utf-8") as f:
            f.write(response_text)
        print("\n[Succès] Fichier sauvegardé dans output/sample_agent_response.md !")

if __name__ == "__main__":
    asyncio.run(run_agent())
