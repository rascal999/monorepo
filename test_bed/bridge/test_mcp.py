import json
import subprocess
import time
import sys
import os
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPTester:
    def __init__(self):
        self.process = None
        self.message_id = 1
        self.workspace = "/home/user/tmp"
        self.port = 4000

    def setup_workspace(self):
        """Set up test workspace."""
        try:
            # Create workspace if it doesn't exist
            os.makedirs(self.workspace, exist_ok=True)

            # Create test files
            test_file = os.path.join(self.workspace, "test.txt")
            with open(test_file, "w") as f:
                f.write("Hello, MCP!")

            # Create test directory
            test_dir = os.path.join(self.workspace, "test_dir")
            os.makedirs(test_dir, exist_ok=True)
            with open(os.path.join(test_dir, "nested.txt"), "w") as f:
                f.write("Nested file content")

            logger.info("Workspace set up successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to set up workspace: {str(e)}")
            return False

    def start_server(self) -> bool:
        """Start the MCP server in a Docker container."""
        try:
            logger.info("Starting MCP server...")
            self.process = subprocess.Popen(
                [
                    "docker", "run", "--rm", "-i",
                    "--network", "host",
                    "-v", f"{self.workspace}:/workspace",
                    "-w", "/workspace",
                    "-e", "MCP_ALLOWED_PATHS=/workspace",
                    "-e", "NODE_ENV=production",
                    "-e", f"PORT={self.port}",
                    "node:20",
                    "sh", "-c",
                    "cd /workspace && npx -y @modelcontextprotocol/server-filesystem@latest /workspace"
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            # Wait for server to start
            logger.info("Waiting for server to start...")
            time.sleep(5)

            if self.process.poll() is not None:
                stderr = self.process.stderr.read()
                raise Exception(f"Server failed to start: {stderr}")

            # Initialize server
            response = self.send_message({
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
                        "name": "MCPTester",
                        "version": "1.0.0"
                    }
                },
                "id": self.message_id
            })

            if not response or 'protocolVersion' not in response:
                raise Exception("Invalid initialization response")

            logger.info("Server initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to start server: {str(e)}")
            if self.process and self.process.poll() is None:
                self.process.terminate()
                self.process.wait(timeout=5)
            return False

    def send_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send a message to the MCP server and get response."""
        if not self.process:
            raise Exception("Server not started")

        try:
            message_str = json.dumps(message) + "\n"
            logger.debug(f"Sending message: {message_str.strip()}")

            self.process.stdin.write(message_str)
            self.process.stdin.flush()

            # Read response with timeout
            for _ in range(10):
                if self.process.poll() is not None:
                    stderr = self.process.stderr.read()
                    raise Exception(f"Server process terminated: {stderr}")

                response_str = self.process.stdout.readline()
                if response_str:
                    logger.debug(f"Received response: {response_str.strip()}")
                    response = json.loads(response_str)
                    if 'error' in response:
                        raise Exception(f"Server error: {response['error']}")
                    return response.get('result')

                time.sleep(1)

            raise Exception("No response from server after 10 seconds")

        except Exception as e:
            logger.error(f"Error in send_message: {str(e)}")
            raise

    def test_list_directory(self) -> bool:
        """Test listing directory contents."""
        try:
            logger.info("Testing list_directory...")
            response = self.send_message({
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "list_directory",
                    "arguments": {
                        "path": "."
                    }
                },
                "id": self.message_id
            })
            
            if not response or not isinstance(response, list):
                raise Exception("Invalid response from list_directory")
                
            # Response is a list of entries
            for entry in response:
                if not isinstance(entry, dict) or 'type' not in entry or 'text' not in entry:
                    raise Exception("Invalid entry format in list_directory response")
            
            logger.info(f"Directory contents: {[entry['text'] for entry in response]}")
            return True
            
        except Exception as e:
            logger.error(f"list_directory test failed: {str(e)}")
            return False

    def test_read_file(self) -> bool:
        """Test reading a file."""
        try:
            logger.info("Testing read_file...")
            response = self.send_message({
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "read_file",
                    "arguments": {
                        "path": "test.txt"
                    }
                },
                "id": self.message_id
            })
            
            if not response or not isinstance(response, list):
                raise Exception("Invalid response from read_file")
                
            # Response is a list of content blocks
            for block in response:
                if not isinstance(block, dict) or 'type' not in block or 'text' not in block:
                    raise Exception("Invalid content block format in read_file response")
            
            logger.info(f"File content: {response}")
            return True
            
        except Exception as e:
            logger.error(f"read_file test failed: {str(e)}")
            return False

    def test_get_tools(self) -> bool:
        """Test getting available tools."""
        try:
            logger.info("Testing tools/list...")
            response = self.send_message({
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": self.message_id
            })
            
            if not response or 'tools' not in response:
                raise Exception("Invalid response from tools/list")
                
            tools = response['tools']
            logger.info(f"Available tools: {', '.join(t['name'] for t in tools)}")
            return True
            
        except Exception as e:
            logger.error(f"tools/list test failed: {str(e)}")
            return False

    def cleanup(self):
        """Clean up resources."""
        if self.process:
            logger.info("Shutting down server...")
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Server did not terminate gracefully, forcing...")
                self.process.kill()
            self.process = None

def main():
    tester = MCPTester()
    success = False
    
    try:
        # Set up workspace
        if not tester.setup_workspace():
            logger.error("Failed to set up workspace")
            sys.exit(1)
            
        # Start server
        if not tester.start_server():
            logger.error("Failed to start server")
            sys.exit(1)
            
        # Run tests
        tests = [
            ("Get Tools", tester.test_get_tools),
            ("List Directory", tester.test_list_directory),
            ("Read File", tester.test_read_file)
        ]
        
        all_passed = True
        for name, test in tests:
            logger.info(f"\nRunning test: {name}")
            if not test():
                all_passed = False
                logger.error(f"{name} test failed")
            else:
                logger.info(f"{name} test passed")
                
        success = all_passed
        
    except KeyboardInterrupt:
        logger.info("\nTests interrupted by user")
    except Exception as e:
        logger.error(f"Tests failed with error: {str(e)}")
    finally:
        tester.cleanup()
        
    if success:
        logger.info("\nAll tests passed successfully!")
        sys.exit(0)
    else:
        logger.error("\nSome tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()