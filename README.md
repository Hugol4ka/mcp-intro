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

## Mode d'emploi du Serveur MCP

### Lancement en mode Production (stdio)
Pour démarrer le serveur de programmation en arrière-plan via le transport stdio (utilisé par les clients comme Claude Desktop ou un futur agent) :
```bash
python server/learning_server.py
```

# 📑 Programming Learning Server — Procédure de Test MCP

Ce guide documente la configuration des prérequis, l'écriture du script automatisé ainsi que les procédures de test pour valider le bon fonctionnement de votre serveur MCP.

---

## 📋 1. Prérequis système

Avant de pouvoir lancer les tests, assurez-vous que votre environnement dispose des outils suivants :

### Node.js & npx
L'inspecteur officiel d'Anthropic nécessite l'outil `npx` fourni avec Node.js.
* **Vérification** : `node -v` et `npx -v`
* **Installation** (si absent) : Téléchargez la version LTS sur [nodejs.org](https://nodejs.org/) ou utilisez votre gestionnaire de paquets (ex: `brew install node` sur macOS).

### Environnement Virtuel Python
Le serveur utilise les dépendances du dossier local `.venv`. Pensez à l'activer dans votre terminal :
* **macOS / Linux** : `source .venv/bin/activate`
* **Windows** : `.venv\Scripts\activate`

---

L'**MCP Inspector** est l'outil visuel officiel d'Anthropic pour inspecter les schémas de données, exécuter des outils et lire des ressources en mode `stdio`. Il permet d'isoler les tests du serveur avant de le connecter à un agent comme Claude Desktop.

### Lancer l'inspecteur
Depuis la racine de votre projet (avec votre environnement virtuel actif), exécutez la commande suivante :
```bash
npx @modelcontextprotocol/inspector python server/learning_server.py
```
---
