# MCP Servers in Python

## Description

Ce projet met en place un serveur **MCP (Model Context Protocol)** en Python, ainsi qu'un agent IA local capable de l'interroger. Le serveur expose une base de sujets de programmation (`data/topics.json`) via des outils et une ressource MCP. L'agent, connecté à un modèle local via **Ollama**, utilise ces outils pour répondre à des questions d'apprentissage en s'appuyant uniquement sur les données exposées par le serveur, sans dépendre d'une API cloud payante.

## MCP Architecture Summary

Le MCP (*Model Context Protocol*) est un protocole open-source qui permet de connecter une IA à des systèmes externes ou à des données locales, de manière standardisée.

Il repose sur 3 composants :

- **Host** : gère les connexions vers un ou plusieurs serveurs MCP.
- **Client** : composant généralement intégré à l'application hôte, qui communique avec un serveur MCP.
- **Server** : attend des requêtes et y répond en exposant des **outils (tools)**, des **ressources**, et éventuellement des **prompts**.

Différence entre outils et ressources — le point clé est le **contrôle d'exécution** :

- Un **outil (tool)** est contrôlé par le modèle d'IA (LLM) → c'est une **action** (lecture avec logique, écriture, exécution).
- Une **ressource** est contrôlée par l'application hôte (le client) → c'est du **contexte en lecture seule**.

Un serveur ne doit exposer que le strict nécessaire : c'est un point de sécurité important pour prévenir les injections/abus et protéger les données.

Dans ce projet, le serveur communique avec le client en local via le transport **stdio** (le serveur est lancé comme sous-processus par le client, sans réseau).

## Requirements

- **Python 3.10+**
- **Node.js** (fournit `npx`, nécessaire pour MCP Inspector)
- **Ollama** installé localement, avec le modèle `qwen3:14b` téléchargé
- Dépendances Python listées dans `requirements.txt` :
  - `fastmcp`
  - `openai` *(utilisé comme client HTTP compatible, pointé vers l'API locale d'Ollama — pas d'appel à l'API cloud d'OpenAI)*

> Le package `groq` n'est pas utilisé dans ce projet et n'est pas requis.

## Setup

**1. Créer l'environnement virtuel**

- macOS / Linux : `python3 -m venv .venv`
- Windows : `python -m venv .venv`

**2. Activer l'environnement virtuel** (à faire à chaque ouverture de terminal)

- macOS / Linux : `source .venv/bin/activate`
- Windows : `.venv\Scripts\activate`

**3. Installer les dépendances**

```bash
pip install -r requirements.txt
```

**4. Installer Node.js** (pour `npx`, utilisé par MCP Inspector)

- Vérification : `node -v` et `npx -v`
- Installation si absent : [nodejs.org](https://nodejs.org/) (version LTS) ou via un gestionnaire de paquets (ex : `brew install node` sur macOS)

**5. Installer Ollama et récupérer le modèle**

```bash
ollama pull qwen3:14b
```

## How to Run the Server

Pour démarrer le serveur MCP en mode production, via le transport `stdio` (utilisé par des clients comme Claude Desktop ou notre agent local) :

```bash
python server/learning_server.py
```

Le serveur ne tourne pas de façon autonome en arrière-plan : il est conçu pour être lancé comme sous-processus par un client MCP (l'agent ou MCP Inspector s'en chargent automatiquement).

## How to Test the Server

L'**MCP Inspector** est l'outil visuel officiel d'Anthropic pour inspecter les schémas de données, exécuter des outils et lire des ressources en mode `stdio`. Il permet d'isoler les tests du serveur avant de le connecter à un agent.

Depuis la racine du projet (environnement virtuel actif) :

```bash
npx @modelcontextprotocol/inspector python server/learning_server.py
```

Une fois connecté, l'interface affiche les outils et ressources exposés par le serveur :

<img width="1920" height="997" alt="Capture d'écran de l'MCP Inspector" src="https://github.com/user-attachments/assets/9669af88-853f-4285-a616-cd40fb4943b3" />

## How to Run the Agent

L'agent démarre automatiquement le serveur MCP en arrière-plan, envoie la requête au modèle local, et exécute la recherche. Vérifiez qu'Ollama tourne bien en tâche de fond (`ollama list`), puis lancez :

```bash
python client/agent.py "Python Generators"
```

Le sujet est **obligatoire** et se passe en argument de ligne de commande, entre guillemets. Sans argument, le script affiche une erreur et s'arrête :

```bash
python client/agent.py
```
```
Erreur : sujet manquant.
Utilisation : python client/agent.py "<votre sujet>"
```

La réponse générée s'affiche dans le terminal et est également sauvegardée dans `output/sample_agent_response.md`.

## Available Tools

Le serveur MCP (`server/learning_server.py`) expose deux outils :

- **`search_topics(query: str)`** — recherche dans `data/topics.json` les sujets dont l'id, le titre, le résumé ou les concepts clés contiennent la requête (recherche par sous-chaîne, insensible à la casse). Retourne la liste des sujets correspondants, ou un message d'absence de résultat.
- **`get_topic_details(topic_id: str)`** — retourne l'intégralité des informations d'un sujet à partir de son `id` exact (prérequis, concepts clés, erreurs courantes, idée d'exercice pratique).

## Available Resources

- **`topics://catalog`** — ressource en lecture seule qui retourne la liste de tous les sujets disponibles (id + titre uniquement), sous forme de JSON. Elle sert de catalogue rapide, sans charger le détail complet de chaque sujet.

## Third-Party MCP Server Review

Dans le cadre de l'évaluation des risques liés à l'utilisation de serveurs MCP développés par des tiers, j'ai inspecté le serveur officiel **Filesystem** (`@modelcontextprotocol/server-filesystem`), issu du dépôt de référence `modelcontextprotocol/servers`.

**1. Ce que fait le serveur**
Il expose des opérations sur le système de fichiers local (lecture, écriture, listing, déplacement de fichiers/dossiers, récupération de métadonnées) à un client MCP.

**2. Local ou distant**
Local — il tourne sur la machine de l'utilisateur, lancé via `npx` (ou Docker), et communique en `stdio`, comme notre `learning_server.py`.

**3. Outils et ressources exposés**
- `read_text_file` : lecture du contenu d'un fichier texte.
- `list_directory` : liste les fichiers/dossiers d'un répertoire.
- `get_file_info` : métadonnées d'un fichier (taille, dates, permissions).
- `list_allowed_directories` : indique les répertoires que le serveur est autorisé à lire/écrire.
- Des outils d'écriture/déplacement de fichiers sont également disponibles.

**4. Permissions et identifiants requis**
Aucune clé API ni compte. En revanche, les **répertoires autorisés** doivent être définis explicitement au démarrage (arguments en ligne de commande ou mécanisme MCP "Roots"). Sans cela, aucune opération n'est possible.

**5. Risque identifié**
Si le périmètre des répertoires autorisés est trop large (ex : tout le disque), un modèle qui interprète mal une requête, ou un prompt malveillant injecté via un fichier lu par l'agent, pourrait modifier, déplacer ou supprimer des fichiers sensibles hors du périmètre réellement nécessaire.

**6. Mesure de sécurité appliquée**
Limiter l'accès à un unique dossier dédié au projet plutôt qu'à l'ensemble du disque, et utiliser un montage en lecture seule dès que l'écriture n'est pas strictement requise.

## Example Output

### Cas 1 — Sujet présent dans la base de données (`data/topics.json`)

Commande exécutée :

```bash
python client/agent.py "Python Generators"
```

Contenu généré automatiquement dans `output/sample_agent_response.md` :

> Here's a structured overview of **Python Generators**:
>
> ---
>
> ### **What Are Python Generators?**
> Generators are a special type of iterable in Python that allow you to generate values **on-the-fly** instead of storing them all in memory at once. They are created using **functions** and the `yield` keyword.
>
> ---
>
> ### **Key Concepts**
> 1. **`yield` Keyword**
>    - Replaces `return` in generator functions.
>    - Pauses the function's execution and returns a value.
>    - Resumes execution when the next value is requested.
>
> 2. **Lazy Evaluation**
>    - Values are generated only when needed (not precomputed).
>    - Saves memory for large datasets or infinite sequences.
>
> 3. **Generator Objects**
>    - Created by calling a generator function.
>    - Can be iterated over using `for` loops or `next()`.
>
> 4. **Memory Efficiency**
>    - Ideal for handling large files or streams (e.g., reading a file line-by-line without loading it all into RAM).
>
> ---
>
> ### **Example: Generator Function**
> ```python
> def read_large_file(file_path):
>     with open(file_path, 'r') as file:
>         for line in file:
>             yield line.strip()  # Yield one line at a time
> ```
>
> **Usage:**
> ```python
> for line in read_large_file("massive_data.txt"):
>     process(line)  # Process each line as it's read
> ```
>
> ---
>
> ### **Common Mistakes**
> - ❌ Using `return` instead of `yield` to produce multiple values.
> - ❌ Trying to reuse an exhausted generator (once a generator is done, it cannot be reset).
>
> ---
>
> ### **Practice Idea**
> Write a generator that streams a massive text file line-by-line without loading the entire file into RAM. Example use case: processing logs or datasets that are too large for memory.

Ici, le sujet `"Python Generators"` correspond exactement à un `title` présent dans `data/topics.json` : l'outil `search_topics` a trouvé une correspondance, et la réponse générée par le modèle s'appuie sur les données réelles du fichier (concepts clés, erreurs courantes, idée d'exercice).

### Cas 2 — Sujet absent de la base de données (`data/topics.json`)

Commande exécutée :

```bash
python client/agent.py "async await in Python"
```

Sortie terminal :

```
-> Exécution de l'outil local : search_topics avec {'query': 'async await in Python'}
Aucun sujet correspondant trouvé dans la base locale.

=== Réponse de l'Agent Local ===

Aucun sujet correspondant à 'async await in Python' n'a été trouvé dans la base locale. Merci de reformuler votre demande ou de choisir un sujet disponible.
```

Ici, `"async await in Python"` n'existe pas dans `data/topics.json`. L'outil `search_topics` renvoie un résultat vide, ce qui est détecté par le code de l'agent : le second appel au modèle est court-circuité, et un message d'erreur clair est renvoyé directement — sans que le modèle n'invente une explication à partir de ses connaissances générales.

## Known Limitations

- **Recherche par sous-chaîne stricte** : `search_topics` ne matche que si la requête est une sous-chaîne exacte de l'id, du titre, du résumé ou d'un concept clé. Un tiret vs. un espace (`python-decorators` vs `python decorators`), une faute de frappe, ou une reformulation trop différente du titre exact peuvent empêcher de trouver un sujet pourtant présent dans `topics.json`.
- **Le modèle peut halluciner si on ne contrôle pas la réponse côté code** : sans vérification explicite en Python du contenu retourné par l'outil, `qwen3:14b` a généré une réponse complète et détaillée sur un sujet absent de la base (`async/await`), malgré la consigne du system prompt *"N'invente aucun détail absent des outils"*. La consigne textuelle seule n'est pas suffisante ; il a fallu ajouter une vérification explicite dans `agent.py` (détection du message `"No programming topics found"`) pour garantir le comportement.
- **Un seul sujet à la fois** : l'agent traite une seule requête par exécution ; pas de mode conversationnel avec historique.
- **Base de données limitée** : `data/topics.json` ne contient que 5 sujets pour le moment (decorators, inheritance, list comprehensions, context managers, generators).
- **Pas de gestion d'erreur réseau/Ollama** : si Ollama n'est pas lancé ou que le modèle `qwen3:14b` n'est pas téléchargé, le script plante sans message d'erreur explicite dédié à ce cas.

## Reflection

**1. Quel problème le MCP résout-il ?**
Le MCP standardise la façon dont une IA accède à des données ou systèmes externes. Sans lui, chaque intégration (fichiers, bases de données, API...) demanderait un connecteur sur-mesure. Le MCP fournit une interface commune (outils, ressources, prompts) réutilisable par n'importe quel client compatible, ce qui découple le développement des serveurs de données de celui des agents IA qui les consomment.

**2. Quelle est la différence entre un outil et une ressource MCP ?**
Un outil est une action déclenchée et contrôlée par le modèle d'IA (il décide quand l'appeler, avec quels arguments) ; il peut avoir des effets (lecture avec logique, écriture, calcul). Une ressource est une donnée exposée en lecture seule, contrôlée par l'application hôte plutôt que par le modèle — elle sert de contexte, pas d'action.

**3. Que expose mon serveur MCP ?**
Il expose deux outils (`search_topics`, `get_topic_details`) permettant de chercher et consulter des sujets de programmation, ainsi qu'une ressource (`topics://catalog`) donnant la liste complète des sujets disponibles en lecture seule.

**4. Comment mon agent utilise-t-il le serveur MCP ?**
L'agent se connecte au serveur en local via `stdio`, récupère la liste des outils disponibles, les transmet au modèle Ollama sous forme de function calling. Si le modèle décide d'appeler `search_topics`, l'agent exécute l'appel via la session MCP, réinjecte le résultat dans la conversation, puis (sauf si aucun sujet n'a été trouvé) redemande au modèle de rédiger la réponse finale à partir de ces données.

**5. Que faut-il vérifier avant d'utiliser un serveur MCP tiers ?**
Ce qu'il expose exactement (outils/ressources), s'il tourne en local ou à distance, quelles permissions ou identifiants il requiert, et le périmètre d'accès qu'on lui accorde (ex : quels répertoires, quelles API). Il faut privilégier le principe du moindre privilège : n'autoriser que le strict nécessaire, éviter d'utiliser des identifiants personnels, et lire la documentation avant de lancer le serveur.

**6. Quelle limitation ai-je observée dans mon implémentation ?**
Le system prompt seul ne suffit pas à empêcher le modèle d'inventer une réponse quand l'outil ne trouve rien : `qwen3:14b` a généré une explication complète sur `async`/`await` alors que ce sujet n'existe pas dans `data/topics.json`, malgré la consigne explicite de ne pas inventer. Il a fallu ajouter un contrôle explicite côté code (vérifier si le résultat de `search_topics` contient un message d'absence de résultat) pour garantir ce comportement de façon fiable, plutôt que de compter sur l'obéissance du modèle à une instruction textuelle.