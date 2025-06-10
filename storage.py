import os
import json
from typing import Dict
from datetime import datetime

from models import PastaInfo


class PastaStorage:
    """Handles persistent storage of custom pasta types"""
    
    def __init__(self, filename: str = "custom_pasta.json"):
        self.filename = filename
        self.backup_filename = f"{filename}.backup"
    
    def load_custom_pasta(self) -> Dict[str, PastaInfo]:
        """Load custom pasta types from file"""
        try:
            if not os.path.exists(self.filename):
                return {}
            
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            custom_pasta = {}
            pasta_data = data.get('custom_pasta', {})
            
            for name, info in pasta_data.items():
                custom_pasta[name] = PastaInfo(
                    name=info['name'],
                    min_time=info['min_time'],
                    max_time=info['max_time'],
                    is_custom=True,
                    usage_count=info.get('usage_count', 0),
                    created_date=info.get('created_date')
                )
            
            return custom_pasta
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Warning: Could not load custom pasta data: {e}")
            return {}
    
    def save_custom_pasta(self, custom_pasta: Dict[str, PastaInfo]) -> bool:
        """Save custom pasta types to file"""
        try:
            # Create backup of existing file
            if os.path.exists(self.filename):
                try:
                    with open(self.filename, 'r') as src, open(self.backup_filename, 'w') as dst:
                        dst.write(src.read())
                except Exception:
                    pass  # Backup failed, but continue with save
            
            # Prepare data for saving
            pasta_data = {}
            for name, info in custom_pasta.items():
                pasta_data[name] = {
                    'name': info.name,
                    'min_time': info.min_time,
                    'max_time': info.max_time,
                    'usage_count': info.usage_count,
                    'created_date': info.created_date
                }
            
            data = {
                'custom_pasta': pasta_data,
                'metadata': {
                    'version': '1.0',
                    'last_updated': datetime.now().isoformat()
                }
            }
            
            # Save to file
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Error saving custom pasta data: {e}")
            return False
