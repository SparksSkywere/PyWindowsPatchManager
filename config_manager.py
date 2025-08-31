# Prevent __pycache__ creation
import os
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

import json
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = Path(config_file)
        self._config = None
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            else:
                self._config = self._get_default_config()
                self.save_config()
        except Exception as e:
            self._config = self._get_default_config()
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            pass
    
    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation (e.g., 'general.auto_check_updates')"""
        try:
            keys = key_path.split('.')
            value = self._config
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """Set configuration value using dot notation"""
        try:
            keys = key_path.split('.')
            config = self._config
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            config[keys[-1]] = value
            self.save_config()
        except Exception as e:
            pass
    
    def get_excluded_programs(self):
        """Get list of programs to exclude from updates"""
        programs = self.get('exclusions.programs', [])
        publishers = self.get('exclusions.publishers', [])
        keywords = self.get('exclusions.keywords', [])
        return {
            'programs': programs,
            'publishers': publishers,
            'keywords': keywords
        }
    
    def is_program_excluded(self, program_name: str, publisher: str = "") -> bool:
        """Check if a program should be excluded from updates"""
        exclusions = self.get_excluded_programs()
        
        # Check program name
        if program_name.lower() in [p.lower() for p in exclusions['programs']]:
            return True
        
        # Check publisher
        if publisher and publisher.lower() in [p.lower() for p in exclusions['publishers']]:
            return True
        
        # Check keywords
        program_lower = program_name.lower()
        for keyword in exclusions['keywords']:
            if keyword.lower() in program_lower:
                return True
        
        return False
    
    def _get_default_config(self):
        """Get default configuration"""
        return {
            "general": {
                "auto_check_updates": True,
                "check_interval_hours": 24,
                "create_backups": True,
                "backup_directory": "backups"
            },
            "update_sources": {
                "winget": {
                    "enabled": True,
                    "priority": 1
                },
                "chocolatey": {
                    "enabled": True,
                    "priority": 2
                },
                "custom": {
                    "enabled": True,
                    "priority": 3
                }
            },
            "exclusions": {
                "programs": [
                    "Windows Security",
                    "Microsoft Edge WebView2",
                    "Microsoft Visual C++ Redistributable"
                ],
                "publishers": [
                    "Microsoft Corporation"
                ],
                "keywords": [
                    "driver",
                    "codec"
                ]
            },
            "update_behavior": {
                "require_confirmation": True,
                "update_all_at_once": False,
                "max_concurrent_updates": 3,
                "restart_if_required": False,
                "download_only": False
            },
            "notifications": {
                "show_update_available": True,
                "show_update_complete": True,
                "show_errors": True
            }
        }

# Global config instance
_config = None

def get_config():
    global _config
    if _config is None:
        _config = ConfigManager()
    return _config
