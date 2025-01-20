#!/usr/bin/env python3

import argparse
import importlib
import sys
import os

# Get the list of available credential types by checking the modules directory
def get_available_modules():
    modules_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modules')
    available_modules = [
        f[:-3] for f in os.listdir(modules_dir)
        if f.endswith('.py') and not f.startswith('__')
    ]
    return available_modules

# Dynamically load module help lines in a concise format
def get_module_help_lines():
    help_lines = {}
    available_modules = get_available_modules()
    max_length = 0  # Track the maximum line length for alignment

    for module_name in available_modules:
        try:
            module = importlib.import_module(f'modules.{module_name}')
            if hasattr(module, 'add_arguments'):
                # Create a parser and add the arguments from the module
                parser = argparse.ArgumentParser(description=f'{module_name.capitalize()} Credentials Tester', add_help=False)
                module.add_arguments(parser)

                # Get the positional and optional arguments as a single-line string
                options = []
                for action in parser._actions:
                    if action.option_strings:
                        # Optional argument
                        options.append(f"[{' '.join(action.option_strings)} {action.metavar or ''}]".strip())
                    else:
                        # Positional argument
                        options.append(action.metavar or action.dest)

                # Concatenate the options to form a single-line representation of the usage
                usage_line = f"{module_name} " + " ".join(options)
                help_lines[module_name] = (usage_line, parser.description)

                # Update max_length for comment alignment
                max_length = max(max_length, len(usage_line))

        except Exception as e:
            help_lines[module_name] = (f"{module_name}: Error loading module", str(e))

    return help_lines, max_length

# Main function to handle argument parsing and module loading
def main():
    # If -h or --help is requested without a specific module, show the global help
    if '-h' in sys.argv[1:] or '--help' in sys.argv[1:]:
        print("Usage: cred_tester.py <credential_type> [options]\n")
        print("Available credential types:\n")

        # Dynamically load help information for all modules
        help_lines, max_length = get_module_help_lines()
        
        for module_name, (usage_line, description) in help_lines.items():
            # Print each module's usage, followed by a right-aligned comment for the description
            print(f"{usage_line.ljust(max_length + 1)} # {description}")

        sys.exit(0)

    # Ensure the user provided a credentials type
    if len(sys.argv) < 2:
        print("Error: Please provide a credentials type (e.g., 'aws').")
        sys.exit(1)

    # Get the credentials type from the first positional argument
    cred_type = sys.argv[1]

    # Get the absolute path of the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Add the current directory to sys.path
    sys.path.insert(0, current_dir)

    # Dynamically load the corresponding module from the 'modules' directory
    try:
        module = importlib.import_module(f'modules.{cred_type}')
    except ModuleNotFoundError as e:
        print(f"Error: No module found for credentials type '{cred_type}'.")
        print(f"Exception: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while importing module '{cred_type}': {e}")
        sys.exit(1)

    # Create a new argument parser and delegate the rest to the module
    parser = argparse.ArgumentParser(description=f'{cred_type.capitalize()} Credentials Tester')

    # Add help from the module itself
    if hasattr(module, 'add_arguments'):
        module.add_arguments(parser)
    else:
        print(f"Error: Module '{cred_type}' does not have an 'add_arguments' function.")
        sys.exit(1)

    # Parse the arguments
    args = parser.parse_args(sys.argv[2:])

    # Call the test function from the loaded module
    if hasattr(module, 'test_credentials'):
        success = module.test_credentials(args)
        sys.exit(0 if success else 1)
    else:
        print(f"Error: Module '{cred_type}' does not have a 'test_credentials' function.")
        sys.exit(1)

if __name__ == "__main__":
    main()
