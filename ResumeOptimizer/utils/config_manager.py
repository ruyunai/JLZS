import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._config is None:
            self.load_config()

    def get_config_path(self) -> Path:
        app_dir = Path(os.environ.get('APPDATA', '.')) / 'ResumeOptimizer'
        app_dir.mkdir(parents=True, exist_ok=True)
        return app_dir / 'config.json'

    def load_config(self) -> Dict[str, Any]:
        config_path = self.get_config_path()
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        else:
            default_config_path = Path(__file__).parent.parent / 'config.json'
            if default_config_path.exists():
                with open(default_config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                self.save_config()
            else:
                self._config = self._get_default_config()
        return self._config

    def save_config(self, config: Optional[Dict[str, Any]] = None):
        if config:
            self._config = config
        config_path = self.get_config_path()
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, ensure_ascii=False, indent=2)

    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        return self._config.get('agents', {}).get(agent_name, {})

    def update_agent_config(self, agent_name: str, config: Dict[str, Any]):
        if 'agents' not in self._config:
            self._config['agents'] = {}
        self._config['agents'][agent_name] = config
        self.save_config()

    def get_output_config(self) -> Dict[str, Any]:
        return self._config.get('output', {})

    def update_output_config(self, config: Dict[str, Any]):
        self._config['output'] = config
        self.save_config()

    def _get_default_config(self) -> Dict[str, Any]:
        return {
            "agents": {
                "agent1_analyze": {
                    "provider": "siliconflow",
                    "model": "Qwen/Qwen2.5-72B-Instruct",
                    "api_base": "https://api.siliconflow.cn/v1",
                    "api_key": ""
                },
                "agent2_optimize": {
                    "provider": "siliconflow",
                    "model": "Qwen/Qwen2.5-72B-Instruct",
                    "api_base": "https://api.siliconflow.cn/v1",
                    "api_key": ""
                }
            },
            "ui": {
                "theme": "light",
                "language": "zh-CN"
            },
            "output": {
                "directory": "",
                "naming_template": "{name}_{position}_{date}",
                "auto_open_folder": True,
                "show_preview": True
            }
        }
