"""File operations for variable management."""

from pathlib import Path
from typing import Dict
from .variable_types import Variable, VariableType
from .variable_registry import VariableRegistry

def generate_env_file(variables: Dict[str, Variable], output_path: Path) -> None:
    """Generate .env file template with extracted variables."""
    env_content = []
    
    # Group variables by type
    by_type = {}
    for var in variables.values():
        if var.type not in by_type:
            by_type[var.type] = []
        by_type[var.type].append(var)
    
    # Generate sections by type
    for var_type in VariableType:
        if var_type in by_type:
            env_content.append(f"\n# {var_type.value.upper()} Variables")
            for var in sorted(by_type[var_type], key=lambda x: x.name):
                if var.description:
                    env_content.append(f"# {var.description}")
                default = f"={var.default_value}" if var.default_value else ""
                env_content.append(f"{var.name.upper()}{default}")
    
    # Write to file
    output_path.write_text("\n".join(env_content))

def generate_variable_registry(variables: Dict[str, Variable], 
                             output_path: Path,
                             collection_name: str = "",
                             collection_version: str = "",
                             overwrite: bool = False) -> None:
    """Generate variable registry JSON file."""
    # Try to load existing registry
    registry = VariableRegistry.load(output_path)
    if registry:
        # Merge new variables with existing registry
        registry.merge_variables(variables)
    else:
        # Create new registry
        registry = VariableRegistry.from_variables(variables, collection_name, collection_version)
    
    # Save registry
    registry.save(output_path, overwrite)

def copy_variable_registry(src_path: Path, dest_path: Path) -> None:
    """Copy variable registry to destination if source exists."""
    if src_path.exists():
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(src_path.read_text())

def replace_variables(text: str, variables: Dict[str, Variable], sanitize_func) -> str:
    """Replace Postman variables with Python format strings."""
    result = text
    for var_name, var in variables.items():
        if var_name.startswith('$random'):  # Postman dynamic variable
            result = result.replace(
                var_name,  # Direct replacement without {{...}}
                "{" + var_name[1:] + "}"  # Remove $ prefix for Python identifiers
            )
        else:  # Regular Postman variable
            result = result.replace(
                f"{{{{{var_name}}}}}",  # Use original case from collection
                "{" + sanitize_func(var_name) + "}"  # Keep original case
            )
    return result
