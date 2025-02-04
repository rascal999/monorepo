import json
import logging
import subprocess
import sys
import os
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ServerParameters:
    command: str
    args: Optional[List[str]] = None
    allowed_directory: Optional[str] = None
    env: Optional[Dict[str, str]] = None

@dataclass
class Tool:
    name: str
    description: str
    input_schema: Dict[str, Any]

class MCPClient:
    def __init__(self, server_params: ServerParameters):
        self.server_params = server_params
        self.process = None
        self.initialized = False
        self.available_tools = set()
        
    def connect(self) -> None:
        """Connect to the MCP server."""
        try:
            spawn_options = {
                'stdin': subprocess.PIPE,
                'stdout': subprocess.PIPE,
                'stderr': subprocess.PIPE,
                'text': True,
                'bufsize': 1  # Line buffered
            }
            
            if self.server_params.allowed_directory:
                spawn_options['cwd'] = self.server_params.allowed_directory
            
            if self.server_params.env:
                spawn_options['env'] = {**dict(os.environ), **self.server_params.env}
            
            logger.info("Starting MCP server process...")
            self.process = subprocess.Popen(
                [self.server_params.command] + (self.server_params.args or []),
                **spawn_options
            )
            
            # Wait for container to start
            logger.info("Waiting for MCP server to start...")
            time.sleep(5)  # Give container time to start
            
            # Check if process is still running
            if self.process.poll() is not None:
                stderr_output = self.process.stderr.read()
                raise Exception(f"MCP server process failed to start: {stderr_output}")
            
            # Initialize session
            init_message = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "0.1.0",
                    "capabilities": {
                        "tools": {
                            "call": True,
                            "list": True
                        }
                    },
                    "clientInfo": {
                        "name": "MCPLLMBridge",
                        "version": "1.0.0"
                    }
                },
                "id": 1
            }
            
            logger.info("Sending initialization message...")
            response = self._send_message(init_message)
            if not response or 'protocolVersion' not in response:
                raise Exception("Invalid initialization response")
                
            self.initialized = True
            logger.info("MCP server initialized successfully")
            
            self._update_available_tools()
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {str(e)}")
            if self.process and self.process.poll() is None:
                self.process.terminate()
                self.process.wait(timeout=5)
            raise

    def _send_message(self, message: Dict) -> Any:
        """Send a message to the MCP server and get response."""
        if not self.process:
            raise Exception("MCP server not connected")
            
        try:
            message_str = json.dumps(message) + "\n"
            logger.debug(f"Sending message: {message_str.strip()}")
            
            self.process.stdin.write(message_str)
            self.process.stdin.flush()
            
            # Read response with timeout
            for _ in range(10):  # Try for 10 seconds
                if self.process.poll() is not None:
                    stderr_output = self.process.stderr.read()
                    raise Exception(f"MCP server process terminated: {stderr_output}")
                    
                response_str = self.process.stdout.readline()
                if response_str:
                    logger.debug(f"Received response: {response_str.strip()}")
                    response = json.loads(response_str)
                    if 'error' in response:
                        raise Exception(f"MCP server error: {response['error']}")
                    return response.get('result')
                    
                time.sleep(1)
                
            raise Exception("No response from MCP server after 10 seconds")
            
        except Exception as e:
            logger.error(f"Error in _send_message: {str(e)}")
            raise

    def _update_available_tools(self) -> None:
        """Update the set of available tools."""
        tools = self.get_available_tools()
        self.available_tools = {tool.name for tool in tools}
        logger.info(f"Available tools: {', '.join(self.available_tools)}")

    def get_available_tools(self) -> List[Tool]:
        """Get list of available tools from the server."""
        if not self.initialized:
            raise Exception("Client not initialized")
            
        message = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 2
        }
        
        response = self._send_message(message)
        tools = []
        for tool_data in response.get('tools', []):
            tools.append(Tool(
                name=tool_data['name'],
                description=tool_data.get('description', f"Use the {tool_data['name']} tool"),
                input_schema=tool_data.get('inputSchema', {})
            ))
        return tools

    def call_tool(self, tool_name: str, tool_args: Dict) -> Any:
        """Call a tool with given arguments."""
        if not self.initialized:
            raise Exception("Client not initialized")
            
        if tool_name not in self.available_tools:
            raise Exception(f"Unknown tool '{tool_name}'")
            
        message = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": tool_args
            },
            "id": 3
        }
        
        return self._send_message(message)

    def close(self) -> None:
        """Close the connection to the MCP server."""
        if self.process:
            logger.info("Shutting down MCP server...")
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("MCP server did not terminate gracefully, forcing...")
                self.process.kill()
            self.process = None
        self.initialized = False
        self.available_tools.clear()
        logger.info("MCP server shut down")

class OllamaClient:
    def __init__(self, model: str = "llama2"):
        self.model = model
        self.base_url = "http://localhost:11434/api"
        self.tools = []
        
    def generate(self, prompt: str, tools: Optional[List[Dict]] = None, tool_responses: Optional[List[Dict]] = None) -> Dict:
        """Generate a response from Ollama with optional tool calls."""
        url = f"{self.base_url}/generate"
        
        # Format system message with tools if provided
        system_message = "You are a helpful assistant."
        if tools:
            system_message += "\nYou have access to the following tools:\n"
            for tool in tools:
                system_message += f"- {tool['function']['name']}: {tool['function']['description']}\n"
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "system": system_message,
            "stream": False
        }
        
        if tools:
            data["tools"] = tools
            
        if tool_responses:
            data["tool_responses"] = tool_responses
            
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()

class Bridge:
    def __init__(self, config_path: str):
        with open(config_path) as f:
            self.config = json.load(f)
            
        self.mcp_clients: Dict[str, MCPClient] = {}
        self.tool_to_mcp: Dict[str, MCPClient] = {}
        self.ollama_client = OllamaClient(self.config.get("model", "llama2"))
        self.tools = []
        
    def initialize(self) -> bool:
        """Initialize connections to MCP servers and set up tools."""
        try:
            # Connect to primary MCP server
            logger.info("Initializing primary MCP server...")
            primary_client = MCPClient(ServerParameters(**self.config["mcpServer"]))
            primary_client.connect()
            self.mcp_clients["primary"] = primary_client
            
            # Connect to additional MCP servers if configured
            if "mcpServers" in self.config:
                for name, server_config in self.config["mcpServers"].items():
                    if name != self.config.get("mcpServerName"):
                        logger.info(f"Initializing MCP server: {name}")
                        client = MCPClient(ServerParameters(**server_config))
                        client.connect()
                        self.mcp_clients[name] = client
            
            # Get and convert tools from all MCP servers
            for name, client in self.mcp_clients.items():
                logger.info(f"Getting tools from MCP server: {name}")
                mcp_tools = client.get_available_tools()
                for tool in mcp_tools:
                    self.tool_to_mcp[tool.name] = client
                    
                converted_tools = self._convert_mcp_tools_to_openai_format(mcp_tools)
                self.tools.extend(converted_tools)
                
            logger.info(f"Bridge initialized with {len(self.tools)} tools")
            return True
            
        except Exception as e:
            logger.error(f"Bridge initialization failed: {str(e)}")
            return False
            
    def _convert_mcp_tools_to_openai_format(self, mcp_tools: List[Tool]) -> List[Dict]:
        """Convert MCP tools to OpenAI function format."""
        converted = []
        for tool in mcp_tools:
            converted.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": tool.input_schema.get("properties", {}),
                        "required": tool.input_schema.get("required", [])
                    }
                }
            })
        return converted
        
    def process_message(self, message: str) -> str:
        """Process a message through Ollama and handle any tool calls."""
        try:
            # Get initial response from Ollama
            response = self.ollama_client.generate(message, self.tools)
            
            # Handle tool calls if present
            while "tool_calls" in response:
                tool_responses = []
                for tool_call in response["tool_calls"]:
                    try:
                        tool_name = tool_call["function"]["name"]
                        tool_args = json.loads(tool_call["function"]["arguments"])
                        
                        # Get appropriate MCP client and call tool
                        mcp_client = self.tool_to_mcp.get(tool_name)
                        if not mcp_client:
                            raise Exception(f"No MCP found for tool: {tool_name}")
                            
                        result = mcp_client.call_tool(tool_name, tool_args)
                        
                        tool_responses.append({
                            "tool_call_id": tool_call["id"],
                            "output": json.dumps(result) if isinstance(result, (dict, list)) else str(result)
                        })
                        
                    except Exception as e:
                        tool_responses.append({
                            "tool_call_id": tool_call["id"],
                            "output": f"Error: {str(e)}"
                        })
                
                # Get next response from Ollama with tool results
                response = self.ollama_client.generate(
                    message,
                    tool_responses=tool_responses
                )
            
            return response["response"]
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return f"Error processing message: {str(e)}"
            
    def close(self) -> None:
        """Close all MCP client connections."""
        for client in self.mcp_clients.values():
            client.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python bridge.py <config_file>")
        sys.exit(1)
        
    config_path = sys.argv[1]
    bridge = Bridge(config_path)
    
    if not bridge.initialize():
        print("Failed to initialize bridge")
        sys.exit(1)
        
    try:
        while True:
            message = input("Enter message (or 'quit' to exit): ")
            if message.lower() == 'quit':
                break
                
            response = bridge.process_message(message)
            print(f"Response: {response}")
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        bridge.close()

if __name__ == "__main__":
    main()