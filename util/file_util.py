import yaml
import os

def load_config():
    """Load agent configuration from YAML file."""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'agent.yaml')
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)