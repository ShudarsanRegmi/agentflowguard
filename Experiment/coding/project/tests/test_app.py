import sys
sys.path.append('src')
from utils import load_config

def test_load_config():
    config = load_config()
    assert config['port'] == 8080
