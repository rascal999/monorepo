# Postman Dependency Graph Generator

A simple tool to analyze Postman collections and generate a text-based dependency graph showing relationships between API endpoints based on variable usage.

## Features

- Analyzes Postman collection JSON files
- Identifies variables from multiple sources:
  * Pre-request and test scripts:
    - Variables set using pm.environment.set or pm.variables.set
    - Variables used with pm.environment.get or pm.variables.get
    - Direct variable references using {{variable}} syntax
  * Request components:
    - URL path variables
    - Query parameters
    - Request body (raw JSON, form data, urlencoded)
    - Dynamic URL segments
- Shows dependencies between endpoints based on variable flow
- Generates text-based output showing endpoint relationships

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Generate Dependencies YAML:
```bash
python src/main.py path/to/postman_collection.json > deps.yml
```

2. View Dependency Graph for an Endpoint:
```bash
# Show all dependencies
python src/graph_viewer.py deps.yml "GET Workflows/View Card"

# Exclude specific folders (space-separated list after --exclude-folder)
python src/graph_viewer.py deps.yml "GET Workflows/View Card" --exclude-folder "tutorials" "examples" "Mocks"
```

Example Output:

All dependencies:
```
Dependency graph for: GET Workflows/View Card
==================================================
POST Users/Create User -> sets USER_ID
  POST Workflows/Create Card -> uses USER_ID (dynamic)
  POST Workflows/Create Card -> sets CARD_ID
    GET Workflows/View Card -> uses CARD_ID (dynamic)
```

Excluding folders:
```
Dependency graph for: GET Workflows/View Card
Excluding folders: tutorials, examples, Mocks
==================================================
POST Workflows/Create Card -> sets CARD_ID
  GET Workflows/View Card -> uses CARD_ID (dynamic)
```

The tool shows:
- Complete dependency chain for an endpoint
- Variables used and set by each request
- Proper request execution order
- Variable sources (environment or other endpoints)

## Output Format

```yaml
postman_collection_dependencies:
  endpoints:
    "GET Workflows/View Card":
      uses_variables:
        CARD_ID:
          type: dynamic
          set_by:
            - "POST Workflows/Create Card"
    
    "POST Workflows/Create Card":
      uses_variables:
        USER_ID:
          type: dynamic
          set_by:
            - "POST Users/Create User"
      sets_variables:
        - CARD_ID
```

## Limitations

Current version:
- Basic parsing of JavaScript code
- Simple text output format
- May miss complex variable usage patterns
- Environment variables not validated
- Limited handling of nested variable references
- JSON body parsing assumes string format
