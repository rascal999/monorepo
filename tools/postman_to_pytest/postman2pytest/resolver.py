"""
Dependency resolver module for determining test execution order.
"""

from typing import Dict, List, Set
from .parser import PostmanRequest, DependencyConfig

class DependencyResolver:
    """Resolves dependencies between tests and determines execution order."""
    
    def __init__(self, requests: List[PostmanRequest], config: DependencyConfig):
        self.requests = requests
        self.config = config
        self.request_map = {req.endpoint_id: req for req in requests}
        self.dependency_graph: Dict[str, Set[str]] = {}
        self._build_dependency_graph()

    def _build_dependency_graph(self):
        """Build a graph of test dependencies based on variable usage."""
        for request in self.requests:
            endpoint_id = request.endpoint_id
            self.dependency_graph[endpoint_id] = set()
            
            # Get variables used by this endpoint
            var_deps = self.config.get_variable_dependencies(endpoint_id)
            for var_name, var_info in var_deps.items():
                if var_info.get('type') == 'dynamic':
                    # Add dependencies for dynamically set variables
                    for setter in var_info.get('set_by', []):
                        if setter in self.request_map:
                            self.dependency_graph[endpoint_id].add(setter)

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

    def resolve_order(self) -> List[PostmanRequest]:
        """
        Resolve the order of test execution based on dependencies.
        Uses topological sort to order tests.
        """
        # Check for cycles
        cycles = self._detect_cycles()
        if cycles:
            cycle_str = '\n'.join([' -> '.join(cycle) for cycle in cycles])
            raise ValueError(f"Circular dependencies detected:\n{cycle_str}")
        
        # Perform topological sort
        visited = set()
        order = []
        
        def visit(node: str):
            if node in visited:
                return
            visited.add(node)
            
            # Visit all dependencies first
            for dep in self.dependency_graph[node]:
                visit(dep)
                
            order.append(self.request_map[node])
        
        # Visit all nodes
        for node in self.dependency_graph:
            if node not in visited:
                visit(node)
        
        return order

    def get_dependencies(self, request: PostmanRequest) -> List[PostmanRequest]:
        """Get the direct dependencies for a specific request."""
        deps = self.dependency_graph.get(request.endpoint_id, set())
        return [self.request_map[dep] for dep in deps]

    def get_dependents(self, request: PostmanRequest) -> List[PostmanRequest]:
        """Get the requests that depend on this request."""
        dependents = []
        for node, deps in self.dependency_graph.items():
            if request.endpoint_id in deps:
                dependents.append(self.request_map[node])
        return dependents
