import random
from typing import Dict, List, Optional
from datetime import datetime

from models import PastaInfo
from storage import PastaStorage
from validators import CustomPastaValidator


class PastaDatabase:
    """Manages pasta types and their cooking information"""
    
    def __init__(self):
        self._built_in_pasta = {
            "spaghetti": PastaInfo("spaghetti", 8, 10),
            "penne": PastaInfo("penne", 11, 13),
            "fusilli": PastaInfo("fusilli", 9, 11),
            "rigatoni": PastaInfo("rigatoni", 12, 14),
            "linguine": PastaInfo("linguine", 8, 10),
            "farfalle": PastaInfo("farfalle", 10, 12),
            "angel hair": PastaInfo("angel hair", 3, 5),
            "fettuccine": PastaInfo("fettuccine", 9, 11)
        }
        
        self._custom_pasta = {}
        self._storage = PastaStorage()
        self._load_custom_pasta()
        
        self._fun_facts = [
            "Did you know? The word 'pasta' comes from the Italian word for 'paste.'",
            "Tip: Always salt your pasta water for better flavor!",
            "Fact: There are over 600 shapes of pasta worldwide.",
            "Tip: Don't rinse your pasta after cooking; the starch helps sauce stick!",
            "Fact: Al dente means 'to the tooth' in Italian, describing pasta's ideal texture.",
            "Tip: Save a cup of pasta water to help thicken your sauce.",
            "Fact: Pasta was first referenced in Sicily in 1154.",
            "Tip: Stir pasta occasionally to prevent sticking.",
            "Fact: The average Italian eats 51 pounds of pasta per year!",
            "Tip: Pair pasta shapes with the right sauce for best results."
        ]
    
    def _load_custom_pasta(self) -> None:
        """Load custom pasta types from storage"""
        self._custom_pasta = self._storage.load_custom_pasta()
    
    def _save_custom_pasta(self) -> bool:
        """Save custom pasta types to storage"""
        return self._storage.save_custom_pasta(self._custom_pasta)
    
    def get_pasta_info(self, pasta_name: str) -> Optional[PastaInfo]:
        """Get pasta information by name"""
        name_lower = pasta_name.lower()
        
        # Check custom pasta first
        if name_lower in self._custom_pasta:
            return self._custom_pasta[name_lower]
        
        # Check built-in pasta
        return self._built_in_pasta.get(name_lower)
    
    def get_all_pasta_types(self) -> List[PastaInfo]:
        """Get all available pasta types (built-in + custom)"""
        all_pasta = list(self._built_in_pasta.values()) + list(self._custom_pasta.values())
        return sorted(all_pasta, key=lambda p: p.name)
    
    def get_built_in_pasta_types(self) -> List[PastaInfo]:
        """Get only built-in pasta types"""
        return list(self._built_in_pasta.values())
    
    def get_custom_pasta_types(self) -> List[PastaInfo]:
        """Get only custom pasta types"""
        return list(self._custom_pasta.values())
    
    def get_pasta_names(self) -> List[str]:
        """Get list of all pasta names"""
        return [p.name for p in self.get_all_pasta_types()]
    
    def add_custom_pasta(self, name: str, min_time: int, max_time: int) -> bool:
        """Add a custom pasta type"""
        # Validate input
        existing_names = self.get_pasta_names()
        is_valid_name, name_error = CustomPastaValidator.validate_pasta_name(name, existing_names)
        if not is_valid_name:
            raise ValueError(name_error)
        
        is_valid_time, time_error = CustomPastaValidator.validate_cooking_time(min_time, max_time)
        if not is_valid_time:
            raise ValueError(time_error)
        
        # Create pasta info
        pasta_info = PastaInfo(
            name=name.strip(),
            min_time=min_time,
            max_time=max_time,
            is_custom=True,
            usage_count=0,
            created_date=datetime.now().isoformat()
        )
        
        # Add to custom pasta and save
        self._custom_pasta[name.lower()] = pasta_info
        return self._save_custom_pasta()
    
    def remove_custom_pasta(self, name: str) -> bool:
        """Remove a custom pasta type"""
        name_lower = name.lower()
        if name_lower in self._custom_pasta:
            del self._custom_pasta[name_lower]
            return self._save_custom_pasta()
        return False
    
    def is_custom_pasta(self, name: str) -> bool:
        """Check if a pasta type is custom"""
        return name.lower() in self._custom_pasta
    
    def get_custom_pasta_count(self) -> int:
        """Get count of custom pasta types"""
        return len(self._custom_pasta)
    
    def increment_pasta_usage(self, pasta_name: str) -> None:
        """Increment usage count for a pasta type"""
        pasta_info = self.get_pasta_info(pasta_name)
        if pasta_info and pasta_info.is_custom:
            pasta_info.increment_usage()
            self._save_custom_pasta()
    
    def get_random_fact(self) -> str:
        """Get a random pasta fact"""
        return random.choice(self._fun_facts)
