"""Variable processing utilities for test generation."""

import logging
from pathlib import Path
from typing import Dict, List, Union, Optional

from .parser import PostmanItem, PostmanItemGroup
from .variable_handler import (
    collect_variables_from_request,
    Variable,
    VariableType,
    generate_env_file,
    generate_variable_registry
)

# Configure logging
logger = logging.getLogger(__name__)

class VariableProcessor:
    """Processes and manages variables from Postman collections."""

    def __init__(self, output_dir: Path, project_root: Path):
        """Initialize the variable processor.
        
        Args:
            output_dir: Directory where test files will be generated
            project_root: Root directory of the project
        """
        self.output_dir = output_dir
        self.project_root = project_root
        self.variables: Dict[str, Variable] = {}

    def process_items(self, items: List[Union[PostmanItem, PostmanItemGroup]], 
                     auth_config=None, 
                     parent_path: Optional[Path] = None) -> Dict[str, Variable]:
        """Process a list of Postman items recursively to collect variables.
        
        Args:
            items: List of PostmanItem or PostmanItemGroup objects
            auth_config: Optional authentication configuration
            parent_path: Optional parent path for nested items
            
        Returns:
            Dict mapping variable names to Variable objects
        """
        logger.debug(f"Processing {len(items)} items")
        all_variables = {}
        
        # First pass: collect all variables and identify dependencies
        for item in items:
            if isinstance(item, PostmanItem) and item.request:
                logger.debug(f"Processing request item: {item.name}")
                
                # Collect variables from this request
                request_vars = collect_variables_from_request(item)
                logger.debug(f"Collected {len(request_vars)} variables from request {item.name}")
                
                # Identify path variables
                url = item.request.url.raw if isinstance(item.request.url, str) else item.request.url.raw
                for var_name, var in request_vars.items():
                    if '/{{' + var_name + '}}' in url:
                        var.type = VariableType.PATH
                        logger.debug(f"Identified path variable: {var_name}")
                
                all_variables.update(request_vars)
                
            elif hasattr(item, 'item') and item.item:
                logger.debug(f"Processing item group: {item.name}")
                current_path = parent_path / item.name if parent_path else Path(item.name)
                group_vars = self.process_items(item.item, auth_config, current_path)
                all_variables.update(group_vars)
        
        return all_variables

    def generate_variable_files(self, collection_name: str = "", collection_version: str = "", env_file: bool = True) -> None:
        """Generate variable-related files.
        
        Args:
            collection_name: Name of the Postman collection
            collection_version: Version of the Postman collection
            env_file: Whether to generate an environment file
        """
        # Generate variable registry in project root
        registry_path = self.project_root / 'variable_registry.json'
        logger.info(f"Generating/updating variable registry at: {registry_path}")
        generate_variable_registry(
            self.variables,
            registry_path,
            collection_name=collection_name,
            collection_version=collection_version,
            overwrite=False
        )
        logger.debug(f"Generated/updated variable registry: {registry_path}")
        
        # Generate environment file if requested and .env doesn't exist
        if env_file:
            env_path = self.output_dir / '.env'
            if not env_path.exists():
                logger.info(f"Generating new environment file at: {env_path}")
                generate_env_file(self.variables, env_path)
                logger.debug(f"Generated environment file: {env_path}")

    def validate_path_variables(self, items: List[Union[PostmanItem, PostmanItemGroup]]) -> None:
        """Validate path variables have proper source tests.
        
        Args:
            items: List of PostmanItem or PostmanItemGroup objects
        """
        for item in items:
            if isinstance(item, PostmanItem) and item.request:
                # Check if path contains variables
                url = item.request.url.raw if isinstance(item.request.url, str) else item.request.url.raw
                path_vars = [var for var in self.variables if '/{{' + var + '}}' in url]
                
                if path_vars:
                    logger.debug(f"Found path variables in URL: {path_vars}")
                    # Ensure all path variables have proper source tests defined
                    for var_name in path_vars:
                        if var_name in self.variables:
                            var = self.variables[var_name]
                            if var.type == VariableType.PATH and not var.source_test:
                                logger.warning(f"Path variable {var_name} missing source test")
                
            elif hasattr(item, 'item') and item.item:
                self.validate_path_variables(item.item)
