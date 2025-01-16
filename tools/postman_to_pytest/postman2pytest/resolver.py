"""
Dependency resolver module for determining test execution order.
"""

from typing import Dict, List, Set, Tuple
from .parser import PostmanRequest, DependencyConfig
from .name_utils import sanitize_name

class DependencyResolver:
    """Resolves dependencies between tests and determines execution order."""
    
    def __init__(self, requests: List[PostmanRequest], config: DependencyConfig):
        self.requests = requests
        self.config = config
        # Create bidirectional mappings between endpoint_id and test_name
        self.endpoint_to_test_name = {
            req.endpoint_id: req.test_name for req in requests
        }
        self.test_name_to_endpoint = {
            req.test_name: req.endpoint_id for req in requests
        }
        # Map both endpoint_id and test_name to requests for easier lookup
        self.request_map = {
            req.endpoint_id: req for req in requests
        }
        self.test_name_map = {
            req.test_name: req for req in requests
        }
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.variable_groups: Dict[str, Set[str]] = {}  # Group tests by shared variables
        self._build_dependency_graph()

    def _build_dependency_graph(self):
        """Build a graph of test dependencies based on variable usage."""
        # First, build variable groups
        for request in self.requests:
            test_name = request.test_name
            var_deps = self.config.get_variable_dependencies(request.endpoint_id)
            
            # Group tests by variables they set or use
            for var_name, var_info in var_deps.items():
                if var_info.get('type') == 'dynamic':
                    if var_name not in self.variable_groups:
                        self.variable_groups[var_name] = set()
                    self.variable_groups[var_name].add(test_name)
        
        # Then build dependency graph
        for request in self.requests:
            test_name = request.test_name
            self.dependency_graph[test_name] = set()
            
            # Get variables used by this endpoint
            var_deps = self.config.get_variable_dependencies(request.endpoint_id)
            for var_name, var_info in var_deps.items():
                if var_info.get('type') == 'dynamic':
                    # Only add the first setter as a dependency
                    set_by = var_info.get('set_by', [])
                    if set_by:  # Check if there are any setters
                        setter_name = f"test_{sanitize_name(set_by[0])}"
                        if setter_name in self.test_name_map:
                            self.dependency_graph[test_name].add(setter_name)

    def _detect_cycles(self) -> List[List[str]]:
        """Detect cycles in the dependency graph."""
        cycles = []
        visited = set()
        path = []
        
        def dfs(node: str):
            if node in path:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            if node in visited:
                return
                
            visited.add(node)
            path.append(node)
            
            for dep in self.dependency_graph[node]:
                dfs(dep)
                
            path.pop()
        
        for node in self.dependency_graph:
            if node not in visited:
                dfs(node)
                
        return cycles

    def resolve_order(self) -> Tuple[List[PostmanRequest], List[List[str]]]:
        """
        Resolve the order of test execution based on dependencies.
        Uses topological sort to order tests.
        
        Returns:
            tuple: (ordered_requests, cycles)
            - ordered_requests: List of requests in dependency order
            - cycles: List of cycles found, each cycle is a list of endpoint IDs
        """
        # Check for cycles
        cycles = self._detect_cycles()
        
        # Get set of all endpoints involved in cycles
        cyclic_endpoints = set()
        if cycles:
            for cycle in cycles:
                cyclic_endpoints.update(cycle)
            cycle_str = '\n'.join([' -> '.join(cycle) for cycle in cycles])
            print(f"Warning: Skipping tests with circular dependencies:\n{cycle_str}")
        
        # Perform topological sort, excluding cyclic endpoints
        visited = set()
        order = []
        
        def visit(node: str):
            if node in visited or node in cyclic_endpoints:
                return
            visited.add(node)
            
            # Visit all dependencies first
            for dep in self.dependency_graph[node]:
                if dep not in cyclic_endpoints:  # Skip cyclic dependencies
                    visit(dep)
                
            order.append(self.test_name_map[node])
        
        # Visit all nodes, starting with those that have no dependencies
        no_deps = [node for node in self.dependency_graph if not self.dependency_graph[node]]
        for node in no_deps:
            if node not in visited and node not in cyclic_endpoints:
                visit(node)
                
        # Then visit remaining nodes
        for node in self.dependency_graph:
            if node not in visited and node not in cyclic_endpoints:
                visit(node)
        
        # Add any requests that aren't in the dependency graph
        standalone = [req for req in self.requests if req.test_name not in self.dependency_graph]
        return order + standalone, cycles

    def get_dependencies(self, request: PostmanRequest) -> List[PostmanRequest]:
        """Get the direct dependencies for a specific request."""
        deps = self.dependency_graph.get(request.test_name, set())
        return [self.test_name_map[dep] for dep in deps]
        
    def get_related_tests(self, request: PostmanRequest) -> List[PostmanRequest]:
        """Get all tests that share variables with this request."""
        related = set()
        var_deps = self.config.get_variable_dependencies(request.endpoint_id)
        
        # Add tests that share any variables
        for var_name in var_deps:
            if var_name in self.variable_groups:
                related.update(self.variable_groups[var_name])
        
        # Convert test names to requests
        return [self.test_name_map[test_name] for test_name in related]

    def get_dependents(self, request: PostmanRequest) -> List[PostmanRequest]:
        """Get the requests that depend on this request."""
        dependents = []
        for node, deps in self.dependency_graph.items():
            if request.test_name in deps:
                dependents.append(self.test_name_map[node])
        return dependents
