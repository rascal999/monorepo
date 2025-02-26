# Calculator Skill for AnythingLLM

A custom skill that enables basic arithmetic calculations in AnythingLLM conversations.

## Features

- Basic arithmetic operations (+, -, *, /)
- Parentheses support for complex expressions
- Natural language formatting of results
- Input sanitization for security

## Implementation

The skill follows AnythingLLM's agent skill format:

### plugin.json
Defines skill metadata and parameters:
```json
{
  "hubId": "calculator",
  "name": "Calculator",
  "version": "1.0.0",
  "description": "Perform basic arithmetic calculations",
  "active": true,
  "entrypoint": {
    "params": {
      "expression": {
        "type": "string",
        "description": "The arithmetic expression to evaluate"
      }
    }
  }
}
```

### handler.js
Implements the calculation logic:
```javascript
const runtime = {
  async handler({ expression }, { introspect }) {
    // Sanitize and evaluate expression
    const result = eval(sanitizedExpression);
    return {
      success: true,
      message: `The result of ${formattedExpression} is ${result}`
    };
  }
};
```

## Installation

The skill is automatically deployed by the AnythingLLM NixOS module:
1. Mounted from: `/home/user/git/github/monorepo/tools/anythingllm/agent-skills`
2. To: `/app/server/storage/plugins/agent-skills`
3. With read-only access for security

## Usage

The skill can be invoked in conversations using natural language:

```
User: Calculate 2 + 2
Assistant: The result of 2 plus 2 is 4

User: What is 10 * (5 + 3)?
Assistant: The result of 10 times (5 plus 3) is 80
```

## Security

- Input is sanitized to only allow numbers and basic arithmetic operators
- Invalid or malicious expressions return an error message
- No access to JavaScript objects or functions beyond basic arithmetic
- Read-only mount in Docker container prevents modifications

## Integration

The skill is integrated via the NixOS module in:
`github/monorepo/maxos/modules/tools/llm/anythingllm.nix`