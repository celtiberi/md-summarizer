import re
from pathlib import Path

def increment_version():
    pyproject_path = Path("pyproject.toml")
    init_path = Path("src/md_summarizer/__init__.py")
    
    # Read current version from pyproject.toml
    content = pyproject_path.read_text()
    match = re.search(r'version = "(\d+)\.(\d+)\.(\d+)"', content)
    if not match:
        raise ValueError("Version not found in pyproject.toml")
    
    major, minor, patch = map(int, match.groups())
    new_version = f'{major}.{minor}.{patch + 1}'
    
    # Update pyproject.toml
    new_content = re.sub(
        r'version = "\d+\.\d+\.\d+"',
        f'version = "{new_version}"',
        content
    )
    pyproject_path.write_text(new_content)
    
    # Update __init__.py
    init_content = init_path.read_text()
    new_init_content = re.sub(
        r'__version__ = "\d+\.\d+\.\d+"',
        f'__version__ = "{new_version}"',
        init_content
    )
    init_path.write_text(new_init_content)
    
    print(f"Version bumped to {new_version}")
    return new_version

if __name__ == "__main__":
    increment_version() 