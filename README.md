# mcp-intro

## MCP Architecture Summary
Le therme MCP signifie, Model Context Protocol, c'est un open-source qui va connecter une IA a des systèmes externe, ou a des donées locale.
Le MCP se divise en 3 catégorie: 
- Host
- Client
- Server
Un hôte MCP, c'est celui qui va gérer les connecions vers un ou plusieurs serveurs MCP.
Le Client MCP lui est un composant, généralement intégré a une application hôte. 
Le serveur MCP, lui, il attend des requêtes et y répond en exposant des outils, des ressources, et éventuellement des prompts.

Une fonction Python devient un outil(tool) MCP quand il exposé/déclaré par le serveur lui-même. 
La ressource, c'est une donnée exposé pour l'agent en lecture seule.

La différence entre les outils (tools) et les ressouces dans le MCP réside dans le contrôle d'exécution.
les outils sont contrôlés par le modèle d'IA (LLM) alors que les ressources sont controlées par l'application hôte (le client)
Pour résumé, les outils (tools) c'est une action (écriture/exécution)
et les ressources, c'est le contexte (lecture seulement)

Un serveur ne doit exposer le strict nécessaire car c'est un point de sécurité important pour:
-la prévention d'injection et abus
-sécurisation des donées