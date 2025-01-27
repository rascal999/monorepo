import re

class JQLValidator:
    # Reserved JQL words that need to be quoted
    RESERVED_WORDS = {
        'EMPTY', 'NULL', 'IN', 'IS', 'CF', 'ON'
    }

    @classmethod
    def validate_and_fix(cls, query):
        """Validate and fix common JQL issues"""
        # Split query into words while preserving quotes
        parts = cls._split_preserving_quotes(query)
        fixed_parts = []
        
        i = 0
        while i < len(parts):
            part = parts[i]
            
            # Skip already quoted strings
            if part.startswith('"') or part.startswith("'"):
                fixed_parts.append(part)
                i += 1
                continue
            
            # Check if word is reserved
            if part.upper() in cls.RESERVED_WORDS:
                fixed_parts.append(f'"{part}"')
            # Check if it's a value that might need quoting
            elif '=' in part and i + 1 < len(parts):
                fixed_parts.append(part)  # Keep the operator
                next_part = parts[i + 1]
                # Quote the value if it contains spaces or special chars and isn't already quoted
                if (not next_part.startswith('"') and not next_part.startswith("'") and
                    (' ' in next_part or cls._needs_quoting(next_part))):
                    fixed_parts.append(f"'{next_part}'")
                    i += 1  # Skip the next part since we've handled it
                else:
                    fixed_parts.append(next_part)
                    i += 1
            else:
                fixed_parts.append(part)
            i += 1
        
        return ' '.join(fixed_parts)

    @staticmethod
    def _split_preserving_quotes(query):
        """Split query into parts while preserving quoted strings"""
        pattern = r'["\'].*?["\']|\S+'
        return re.findall(pattern, query)

    @staticmethod
    def _needs_quoting(value):
        """Check if a value needs to be quoted"""
        # Add any special characters or patterns that should trigger quoting
        special_chars = r'[,\(\)\{\}\[\]\/\\\s]'
        return bool(re.search(special_chars, value))

    @classmethod
    def fix_maxResults(cls, query):
        """Remove LIMIT clause for manual handling"""
        # Remove any existing LIMIT clause
        query = re.sub(r'\s+LIMIT\s+\d+', '', query, flags=re.IGNORECASE)
        return query