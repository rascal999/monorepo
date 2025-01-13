"""Test generation utility functions."""

def parse_markdown_link(text: str) -> str:
    """Extract the text part from a Markdown link."""
    if not text:
        return "No description provided."
    import re
    match = re.match(r'\[(.*?)\]\((.*?)\)', text.strip())
    if match:
        return match.group(1)
    return text


def format_dict(d: dict, indent_level: int = 2) -> str:
    """Format a dictionary as a Python literal with proper indentation."""
    lines = []
    indent = ' ' * (indent_level * 4)
    lines.append('{')
    for i, (key, value) in enumerate(d.items()):
        comma = ',' if i < len(d) - 1 else ''
        if isinstance(value, dict):
            value_str = format_dict(value, indent_level + 1)
            lines.append(f"{indent}'{key}': {value_str}{comma}")
        elif isinstance(value, str):
            if '{' in value and '}' in value:
                lines.append(f"{indent}'{key}': f'{value}'{comma}")
            else:
                lines.append(f"{indent}'{key}': '{value}'{comma}")
        else:
            lines.append(f"{indent}'{key}': '{value}'{comma}")
    lines.append(' ' * ((indent_level - 1) * 4) + '}')
    return '\n'.join(lines)
