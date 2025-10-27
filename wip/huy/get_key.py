import os

def get_key(file_name: str) -> str:
    """Read API key from a file (first line)."""
    with open(file_name, 'r', encoding='utf-8') as f:
        return f.readline().strip()

os.environ["OPENAI_API_KEY"] = get_key('key.txt')