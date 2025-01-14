#!/usr/bin/env python3
"""
Postman Dependency Graph Viewer
Shows dependency relationships between API endpoints based on variable usage.
"""

import sys
import yaml
from pathlib import Path
from typing import Dict, Set, List, Any, Optional

class DependencyGraphViewer:
    def __init__(self, yaml_path: str, target_endpoint: str, exclude_folders: Optional[List[str]] = None):
        """Initialize with YAML file path and target endpoint."""
        self.yaml_path = yaml_path
        self.target_endpoint = target_endpoint
        self.exclude_folders = exclude_folders or []
        self.dependencies = self._load_dependencies()
        
    def _load_dependencies(self) -> Dict:
        """Load and validate dependencies from YAML file."""
        if not Path(self.yaml_path).exists():
            raise FileNotFoundError(f"YAML file not found: {self.yaml_path}")
            
        with open(self.yaml_path) as f:
            dependencies = yaml.safe_load(f)
            
        endpoints = dependencies.get('postman_collection_dependencies', {}).get('endpoints', {})
        if not endpoints:
            raise ValueError("No endpoints found in dependencies")
            
        if self.target_endpoint not in endpoints:
            available = "\n  ".join(sorted(endpoints.keys()))
            raise ValueError(f"Endpoint not found: {self.target_endpoint}\n\nAvailable endpoints:\n  {available}")
            
        return self._filter_dependencies(dependencies)
    
    def _filter_dependencies(self, dependencies: Dict) -> Dict:
        """Filter out excluded endpoints and their references."""
        if not self.exclude_folders:
            return dependencies
            
        filtered = dependencies.copy()
        endpoints = filtered['postman_collection_dependencies']['endpoints']
        
        # Get all endpoints that should be kept
        keep_endpoints = {
            ep: data for ep, data in endpoints.items() 
            if not self._should_exclude(ep)
        }
        
        # Create new filtered dependencies with only kept endpoints
        filtered['postman_collection_dependencies']['endpoints'] = {}
        
        # Process each kept endpoint
        for ep, data in keep_endpoints.items():
            new_data = data.copy()
            
            # Filter uses_variables to only reference kept endpoints
            if 'uses_variables' in new_data:
                new_uses = {}
                for var, var_data in new_data['uses_variables'].items():
                    if var_data['type'] == 'dynamic':
                        # Only keep setters that aren't excluded
                        new_setters = [
                            setter for setter in var_data['set_by']
                            if setter in keep_endpoints
                        ]
                        if new_setters:
                            new_uses[var] = {
                                'type': 'dynamic',
                                'set_by': new_setters
                            }
                    else:
                        new_uses[var] = var_data
                new_data['uses_variables'] = new_uses
            
            filtered['postman_collection_dependencies']['endpoints'][ep] = new_data
        
        return filtered
    
    def _should_exclude(self, endpoint: str) -> bool:
        """Check if endpoint should be excluded."""
        # Split into verb and path
        parts = endpoint.split(" ", 1)
        if len(parts) != 2:
            return False
            
        # Get path without verb
        path = parts[1]
        path_parts = [p.strip() for p in path.split('/') if p.strip()]
        
        # Check if any excluded folder appears as a complete path component
        for folder in self.exclude_folders:
            folder = folder.strip()
            if folder in path_parts:
                return True
        return False
    
    def _get_endpoint_info(self, endpoint: str) -> Dict[str, Any]:
        """Get endpoint's variable usage and setting info."""
        endpoint_data = self.dependencies['postman_collection_dependencies']['endpoints'][endpoint]
        info = {'endpoint': endpoint, 'uses': [], 'sets': [], 'dependencies': []}
        
        # Get variables used by endpoint
        if 'uses_variables' in endpoint_data:
            for var, data in endpoint_data['uses_variables'].items():
                var_type = data['type']
                info['uses'].append((var, var_type))
                
                # Track dependencies for dynamic variables
                if var_type == 'dynamic':
                    info['dependencies'].extend(data.get('set_by', []))
        
        # Get variables set by endpoint
        if 'sets_variables' in endpoint_data:
            info['sets'].extend(sorted(endpoint_data['sets_variables']))
        
        return info
    
    def _build_dependency_chain(self, endpoint: str, visited: Optional[Set[str]] = None, seen_endpoints: Optional[Set[str]] = None) -> List[Dict[str, Any]]:
        """Build complete dependency chain for endpoint."""
        if visited is None:
            visited = set()
        if seen_endpoints is None:
            seen_endpoints = set()
            
        if endpoint in visited or self._should_exclude(endpoint):
            return []
            
        visited.add(endpoint)
        chain = []
        
        # Get endpoint info
        info = self._get_endpoint_info(endpoint)
        
        # Process dependencies first
        for dep_endpoint in info['dependencies']:
            if dep_endpoint not in visited and not self._should_exclude(dep_endpoint):
                chain.extend(self._build_dependency_chain(dep_endpoint, visited, seen_endpoints))
        
        # Add this endpoint's info if we haven't seen it before
        if endpoint not in seen_endpoints:
            seen_endpoints.add(endpoint)
            chain.append({
                'endpoint': endpoint,
                'uses': sorted(info['uses']),
                'sets': sorted(info['sets'])
            })
        
        return chain
    
    def _format_chain(self, chain: List[Dict[str, Any]], indent: str = "  ") -> List[str]:
        """Format dependency chain for display."""
        lines = []
        current_level = 0
        prev_endpoint = None
        
        for item in chain:
            endpoint = item['endpoint']
            
            # Update indentation level
            if prev_endpoint != endpoint:
                if prev_endpoint is not None:
                    current_level += 1
                prev_endpoint = endpoint
            
            # Format uses variables
            if item['uses']:
                uses_vars = ", ".join(f"{var} ({type})" for var, type in item['uses'])
                lines.append(f"{indent * current_level}{endpoint} -> uses {uses_vars}")
            
            # Format sets variables
            if item['sets']:
                sets_vars = ", ".join(item['sets'])
                lines.append(f"{indent * current_level}{endpoint} -> sets {sets_vars}")
        
        return lines
    
    def display(self):
        """Display formatted dependency graph."""
        print(f"\nDependency graph for: {self.target_endpoint}")
        if self.exclude_folders:
            print(f"Excluding folders: {', '.join(self.exclude_folders)}")
        print("=" * 50)
        
        chain = self._build_dependency_chain(self.target_endpoint)
        lines = self._format_chain(chain)
        print("\n".join(lines))

def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: python graph_viewer.py <dependency_file.yml> <endpoint> [--exclude-folder <folder>...]")
        print("Example: python graph_viewer.py deps.yml 'GET Workflows/View Card' --exclude-folder 'tutorials' 'examples'")
        print("Options:")
        print("  --exclude-folder  Exclude requests from specified folders (can be used multiple times)")
        sys.exit(1)
    
    yaml_path = sys.argv[1]
    target_endpoint = sys.argv[2]
    
    # Get excluded folders
    exclude_folders = []
    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == "--exclude-folder":
            i += 1
            while i < len(sys.argv) and not sys.argv[i].startswith("--"):
                exclude_folders.append(sys.argv[i])
                i += 1
        else:
            i += 1
    
    try:
        viewer = DependencyGraphViewer(yaml_path, target_endpoint, exclude_folders)
        viewer.display()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
