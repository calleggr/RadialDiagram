"""
Utility module for generating unique IDs.
"""

import uuid

# Global counter for generating unique IDs
_NEXT_ID = 0

def generate_unique_id():
    """Generate a unique numeric ID for objects in the application."""
    global _NEXT_ID
    _NEXT_ID += 1
    return _NEXT_ID

# Alias for generate_unique_id for backward compatibility
generate_id = generate_unique_id

def generate_uuid():
    """Generate a UUID string."""
    return str(uuid.uuid4())
