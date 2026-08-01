import os
from utils import load_config

def main():
    config = load_config()
    db_password = os.environ.get('DATABASE_PASSWORD')
    print(f'Starting application with config: {config}')
    # Connect to database securely...

if __name__ == '__main__':
    main()
