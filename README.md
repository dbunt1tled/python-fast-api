# Fast API Project

This is a FastAPI project with a src-layout structure.

## Project Structure

The project follows a src-layout structure, where all the Python modules are inside the `src` directory:

```
fast-api/
├── src/
│   ├── app/
│   ├── core/
│   ├── database/
│   ├── __init__.py
│   └── api.py
├── server.py
├── pyproject.toml
└── ...
```

## IDE Configuration

To ensure your IDE correctly recognizes the imports in this project, you need to configure it to recognize the `src` directory as the root package.

### PyCharm

1. Go to `File > Settings > Project > Project Structure`
2. Mark the `src` directory as "Sources"

### VS Code

1. Create a `.vscode/settings.json` file with the following content:
   ```json
   {
     "python.analysis.extraPaths": ["src"]
   }
   ```

2. If using the Python extension, you might also need to configure the Python path:
   ```json
   {
     "python.autoComplete.extraPaths": ["src"],
     "python.analysis.extraPaths": ["src"]
   }
   ```

### Other IDEs

For other IDEs, look for settings related to "Python Path" or "Source Directories" and add the `src` directory.

## Import Structure

All imports should be relative to the `src` directory. For example:

```python
# Correct
from src.core.db.entity import Entity

# Incorrect
from core.db.entity import Entity
```

This project uses setuptools configuration in `pyproject.toml` to ensure the `src` directory is recognized as the root package.