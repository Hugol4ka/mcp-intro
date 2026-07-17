# MCP - Introduction

Le terme **MCP** signifie *Model Context Protocol*. Il s'agit d'un protocole open-source qui permet de connecter une IA à des systèmes externes ou à des données locales.

Le MCP se divise en 3 catégories :

- **Host**
- **Client**
- **Server**

- **Hôte MCP** : gère les connexions vers un ou plusieurs serveurs MCP.
- **Client MCP** : composant généralement intégré à une application hôte.
- **Serveur MCP** : attend des requêtes et y répond en exposant des outils, des ressources, et éventuellement des prompts.

### Outils vs Ressources

Une fonction Python devient un **outil (tool)** MCP lorsqu'elle est exposée/déclarée par le serveur lui-même.
Une **ressource** est une donnée exposée à l'agent en lecture seule.

La différence entre les outils et les ressources réside dans le contrôle d'exécution :

- Les **outils** sont contrôlés par le modèle d'IA (LLM) → action (écriture/exécution)
- Les **ressources** sont contrôlées par l'application hôte (le client) → contexte (lecture seule)

### Sécurité

Un serveur ne doit exposer que le strict nécessaire, ce qui constitue un point de sécurité important pour :

- la prévention des injections et des abus
- la sécurisation des données

---

## Mode d'emploi du serveur MCP

### Lancement en mode production (stdio)

Pour démarrer le serveur en arrière-plan via le transport `stdio` (utilisé par des clients comme Claude Desktop ou un futur agent) :

```bash
python server/learning_server.py
```

---

## Procédure de test MCP

Ce guide documente la configuration des prérequis ainsi que la procédure de test pour valider le bon fonctionnement de votre serveur MCP.

### 1. Prérequis système

#### Node.js & npx

L'inspecteur officiel d'Anthropic nécessite l'outil `npx`, fourni avec Node.js.

- **Vérification** : `node -v` et `npx -v`
- **Installation** (si absent) : téléchargez la version LTS sur [nodejs.org](https://nodejs.org/), ou utilisez votre gestionnaire de paquets (ex : `brew install node` sur macOS).

#### Environnement virtuel Python

Le serveur utilise les dépendances du dossier local `.venv`.

**1. Création de l'environnement virtuel :**

- macOS / Linux : `python3 -m venv .venv`
- Windows : `python -m venv .venv`

**2. Activation du `.venv`** (à faire à chaque ouverture de terminal) :

- macOS / Linux : `source .venv/bin/activate`
- Windows : `.venv\Scripts\activate`

**3. Installation des dépendances :**

Assurez-vous que le fichier `requirements.txt` (contenant `fastmcp`, `groq`, `openai`) est présent à la racine de votre projet, puis lancez :

```bash
pip install -r requirements.txt
```

---

### 2. Phase de tests du serveur MCP

L'**MCP Inspector** est l'outil visuel officiel d'Anthropic pour inspecter les schémas de données, exécuter des outils et lire des ressources en mode `stdio`. Il permet d'isoler les tests du serveur avant de le connecter à un agent comme Claude Desktop ou notre script client.

#### Lancer l'inspecteur

Depuis la racine de votre projet (avec votre environnement virtuel actif), exécutez la commande suivante :

```bash
npx @modelcontextprotocol/inspector python server/learning_server.py
```

#### Résultat des tests

Une fois connecté, vous pouvez apercevoir les outils et les ressources qui ont été implantés dans le serveur MCP :

<img width="1920" height="997" alt="Capture d'écran de l'MCP Inspector" src="https://github.com/user-attachments/assets/9669af88-853f-4285-a616-cd40fb4943b3" />

---

## 🚀 Utilisation de l'agent IA client

Une fois que le serveur MCP est fonctionnel, vous pouvez lancer l'agent IA autonome qui va interroger le serveur.

### 1. Prérequis - modèle local (Ollama)

Afin d'exécuter l'agent sans dépendre d'une API cloud payante, nous utilisons un modèle local via Ollama.

1. Téléchargez et installez Ollama depuis [ollama.com](https://ollama.com).
2. Récupérez le modèle optimisé pour l'appel d'outils (Tool Calling) :

```bash
ollama pull qwen3:14b
```

### 2. Exécution de l'agent

L'agent va automatiquement démarrer le serveur MCP en arrière-plan, envoyer la requête au modèle local, et exécuter la recherche.

Vérifiez qu'Ollama tourne bien en tâche de fond (vous pouvez tester avec `ollama list`), puis lancez :

```bash
python client/agent.py
```

### 3. Résultat généré

Une fois le script terminé :

- La réponse générée par l'IA (basée sur vos données locales) s'affiche dans le terminal.
- Une copie propre au format Markdown est automatiquement enregistrée dans le dossier de rendu : `output/sample_agent_response.md`.

---

## 📄 Exemple de sortie (`output/sample_agent_response.md`)

Voici un exemple de fichier généré automatiquement par l'agent suite à une requête :

> To study Python decorators effectively, you should first review these foundational topics (based on general programming knowledge, as the tool didn't return specific results):
>
> 1. **Functions as First-Class Citizens**
>    - Understand how functions can be assigned to variables, passed as arguments, and returned from other functions.
>
> 2. **Higher-Order Functions**
>    - Learn how functions can accept other functions as parameters or return them (e.g., `map()`, `filter()`).
>
> 3. **Closures**
>    - Study nested functions and how they can capture variables from their enclosing scope.
>
> 4. **Basic Syntax of Decorators**
>    - Familiarize yourself with the `@decorator` syntax and how it modifies functions.
>
> 5. **The `functools` Module**
>    - Learn about `functools.wraps` to preserve metadata (e.g., `__name__`, `__doc__`) when using decorators.
>
> 6. **Classes and Objects (Optional but Helpful)**
>    - Decorators can also be implemented as classes (class decorators), so basic OOP knowledge is useful.
>
> Start with functions and closures, then progress to the `@` syntax and `functools`. Let me know if you'd like examples!

## 🔍 Revue d'un serveur MCP tiers

Dans le cadre de l'évaluation des risques liés à l'utilisation de serveurs MCP développés par des tiers, j'ai inspecté le serveur officiel **Filesystem** (`@modelcontextprotocol/server-filesystem`), issu du dépôt de référence `modelcontextprotocol/servers`.

### 1. Ce que fait le serveur

Ce serveur expose des opérations sur le système de fichiers local (lecture, écriture, listing, déplacement de fichiers/dossiers, récupération de métadonnées) à un client MCP, dans le but de permettre à une IA de manipuler des fichiers via un ensemble d'outils standardisés.

### 2. Local ou distant

Le serveur tourne **en local**, sur la machine de l'utilisateur. Il est lancé via `npx` (ou dans un conteneur Docker) et communique avec le client par le transport `stdio`, exactement comme notre `learning_server.py`.

### 3. Outils et ressources exposés

Parmi les outils principaux :

- `read_text_file` : lecture du contenu d'un fichier texte.
- `list_directory` : liste les fichiers et dossiers d'un répertoire.
- `get_file_info` : renvoie les métadonnées d'un fichier (taille, dates de création/modification, permissions).
- `list_allowed_directories` : indique quels répertoires le serveur est autorisé à lire/écrire.
- Des outils d'écriture/déplacement de fichiers sont également disponibles.

### 4. Permissions et identifiants requis

Aucune clé API ni compte utilisateur n'est nécessaire. En revanche, le serveur exige que les **répertoires autorisés** soient explicitement définis au démarrage, soit via des arguments en ligne de commande, soit dynamiquement via le mécanisme MCP "Roots". Sans cette configuration, aucune opération sur le système de fichiers n'est possible.

### 5. Risque identifié

Si le périmètre des répertoires autorisés est configuré trop largement (par exemple l'intégralité du disque ou du dossier utilisateur), un modèle qui interprète mal une requête, ou un prompt malveillant injecté via un fichier lu par l'agent, pourrait entraîner la modification, le déplacement ou la suppression de fichiers sensibles situés en dehors du périmètre réellement nécessaire au projet.

### 6. Mesure de sécurité appliquée

Avant toute utilisation, je limiterais l'accès du serveur à un **unique dossier dédié au projet** (ex : `./workspace`) plutôt qu'à l'ensemble du disque, et j'utiliserais un montage en **lecture seule** dès que l'écriture n'est pas strictement requise pour la tâche demandée. Cela réduit fortement la surface d'attaque en cas de comportement inattendu du modèle.
