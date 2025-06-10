from typing import List, Tuple


class CustomPastaValidator:
    """Validates custom pasta input data"""
    
    @staticmethod
    def validate_pasta_name(name: str, existing_names: List[str]) -> Tuple[bool, str]:
        """Validate pasta name. Returns (is_valid, error_message)"""
        if not name or not name.strip():
            return False, "Pasta name cannot be empty"
        
        name = name.strip()
        if len(name) < 2:
            return False, "Pasta name must be at least 2 characters long"
        
        if len(name) > 50:
            return False, "Pasta name must be 50 characters or less"
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not all(c.isalpha() or c in " -'" for c in name):
            return False, "Pasta name can only contain letters, spaces, hyphens, and apostrophes"
        
        # Check for uniqueness (case-insensitive)
        if name.lower() in [n.lower() for n in existing_names]:
            return False, f"A pasta type named '{name}' already exists"
        
        return True, ""
    
    @staticmethod
    def validate_cooking_time(min_time: int, max_time: int) -> Tuple[bool, str]:
        """Validate cooking times. Returns (is_valid, error_message)"""
        if not isinstance(min_time, int) or not isinstance(max_time, int):
            return False, "Cooking times must be whole numbers"
        
        if min_time < 1 or max_time < 1:
            return False, "Cooking times must be at least 1 minute"
        
        if min_time > 60 or max_time > 60:
            return False, "Cooking times must be 60 minutes or less"
        
        if min_time > max_time:
            return False, "Minimum time cannot be greater than maximum time"
        
        return True, ""
