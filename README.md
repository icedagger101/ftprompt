# ftprompt

[![GitHub Repo stars](https://img.shields.io/github/stars/icedagger101/ftprompt?style=social)](https://github.com/icedagger101/ftprompt)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/github/license/icedagger101/ftprompt)](LICENSE)
[![Requirements Status](https://img.shields.io/badge/requirements-txt-green)](requirements.txt)

`ftprompt` is a lightweight Python tool designed to recursively traverse a directory, concatenate all text files into a single output file (`out.txt`), and format them with clear delimiters for easy use in AI prompts, documentation, or code reviews. It respects `.gitignore` patterns (or custom rules files) to exclude unwanted files, supports additional ignore patterns, and handles hidden directories/files intelligently.

The tool is particularly useful for:
- Creating "file tree prompts" for LLMs (e.g., feeding entire project structures into Grok or GPT for code analysis/generation).
- Generating portable project snapshots without sensitive or temporary files.
- Automating repo dumps for documentation or backups.

It includes a bash manager script (`mngr.sh`) for handling multiple projects via a `config.json` file, making it easy to switch between repositories.

## Features

- **Smart Ignoring**: Parses `.gitignore` files (project-specific or script-local) or custom rules files using the `gitignore_parser` library.
- **Custom Exclusions**: Add extra patterns (e.g., `*.log`, `.env`) via CLI flags.
- **Directory Pruning**: Skips ignored/hidden directories early to optimize traversal.
- **Error-Resilient Reading**: Uses UTF-8 with `errors="ignore"` to handle encoding issues.
- **Verbose Logging**: Optional detailed output for debugging inclusions/exclusions.
- **Multi-Project Support**: Use `mngr.sh` to select from predefined projects in `config.json`.
- **Delimiter Formatting**: Outputs files wrapped in `----file start <relative_path>----` and `----file end <relative_path>----` for parseable structure.
- **Virtual Environment Ready**: Integrates with `venv` for isolated dependencies.

## Installation

1. **Clone the Repo**:
   ```bash
   git clone https://github.com/icedagger101/ftprompt.git
   cd ftprompt
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   Use the provided `requirements.txt` for reproducible setup:
   ```bash
   pip install -r requirements.txt
   ```
   This installs `gitignore-parser` (and any future additions) with pinned versions.

4. **Make Scripts Executable** (Unix-like systems):
   ```bash
   chmod +x mngr.sh
   ```

5. **Install `jq`** (for `mngr.sh` multi-project support):
   - Ubuntu/Debian: `sudo apt install jq`
   - macOS: `brew install jq`
   - Windows: Download from [stedolan.github.io/jq](https://stedolan.github.io/jq/download/)

## Usage

### Direct Python Usage

Run the script directly on a directory:

```bash
# Basic usage (processes current directory)
python main.py

# Specify a directory
python main.py /path/to/your/project

# Add custom ignore patterns
python main.py /path/to/project --ignore "*.log" ".env" "node_modules"

# Use a custom rules file (e.g., a modified .gitignore)
python main.py /path/to/project --rules-file /path/to/custom-rules.txt

# Verbose mode for logging
python main.py /path/to/project -v
```

- **Output**: Always generates `out.txt` in the current working directory.
- **Ignores by Default**: The script itself (`main.py`) and generated `out.txt` are auto-ignored.

### Multi-Project Management with `mngr.sh`

1. **Create `config.json`** in the repo root (example below):
   ```json
   [
     {
       "name": "My Web App",
       "absolute_path": "/absolute/path/to/webapp",
       "rules_file_path": "/absolute/path/to/webapp/.gitignore"
     },
     {
       "name": "Data Science Project",
       "absolute_path": "/absolute/path/to/ds-project",
       "rules_file_path": "./ignore_templates/ignore_example"
     }
   ]
   ```

2. **Run the Manager**:
   ```bash
   ./mngr.sh
   ```
   - It activates the `venv` automatically.
   - Displays a menu of projects from `config.json`.
   - Select one (or `q` to quit), and it runs `python main.py` with the project's path and rules.
   - Verbose mode (`-v`) is enabled by default in the manager.

### Example Output in `out.txt`

```
----file start src/main.py----
# Your Python code here...
def hello_world():
    print("Hello, ftprompt!")
----file end src/main.py----

----file start README.md----
# Project Title
...content...
----file end README.md----
```

## Configuration

- **`config.json`**: Array of project objects with:
  - `name` (string): Display name for the menu.
  - `absolute_path` (string): Full path to the project directory.
  - `rules_file_path` (string): Path to a `.gitignore`-style rules file (optional; falls back to project's `.gitignore`).

- **Ignore Templates**: Check `ignore_templates/ignore_example` for sample patterns. These work just like Git's `.gitignore`.

- **Fallback Rules**: If no `--rules-file` is specified:
  1. Uses `<project>/.gitignore` if present.
  2. Falls back to `./.gitignore` in the script's directory.

- **`requirements.txt`**: Lists pinned dependencies (e.g., `gitignore-parser>=0.0.4`). Regenerate with `pip freeze > requirements.txt` after updates.

## Examples

### Quick Project Dump
```bash
python main.py ~/my-repo -v --ignore "tests/" "*.pyc"
```
- Verbose output shows skipped/included files.
- Skips all test dirs and Python cache files.

### AI Prompt Prep
1. Run `./mngr.sh` to select your repo.
2. Copy `out.txt` contents into an LLM prompt: "Analyze this codebase: [paste here]".

### Custom Rules File
Create `my-rules.txt`:
```
# Ignore logs and secrets
*.log
.env
# But include docs
!docs/
```
Then: `python main.py . --rules-file my-rules.txt`

## Troubleshooting

- **Encoding Errors**: Files are read with `errors="ignore"`, but binary/non-text files may still cause issues—add patterns to ignore them.
- **No Projects in Menu**: Ensure `config.json` is valid JSON with at least one project.
- **Venv Not Found**: Run `source venv/bin/activate` manually.
- **jq Missing**: Install as noted in Installation.
- **Large Dirs**: For huge repos, add aggressive ignores (e.g., `node_modules/`) to speed up.
- **Dependency Issues**: If `pip install -r requirements.txt` fails, check Python version (3.8+) or update pip (`pip install --upgrade pip`).

## Contributing

1. Fork the repo and create a feature branch (`git checkout -b feature/amazing-feature`).
2. Commit changes (`git commit -m 'Add amazing feature'`).
3. Push to the branch (`git push origin feature/amazing-feature`).
4. Open a Pull Request.

Ideas welcome: Add support for non-text files (base64?), parallel processing, or a web UI! Also, help maintain `requirements.txt` for new deps.

## License

This project is licensed under the MIT License—see the [LICENSE](LICENSE) file for details. (Add one if missing!)

---

*Built with ❤️ for efficient code sharing. Questions? Open an issue!*
