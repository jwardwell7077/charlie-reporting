# Charlie Reporting

A modern, extensible Python ETL/reporting tool for automating daily CSV/Excel data transformation and reporting.

## Features
- Modular OOP design (easy to extend)
- TOML-based config (no YAML)
- Column mapping by name
- Robust logging
- Pytest-based tests with sample data
- Ready for Python 3.13+

## Authors & Credits
- Jonathan Wardwell
- GitHub Copilot (AI code assistant)
- Prompt inspiration: GPT-4o

## License
MIT License (see LICENSE file)

## Quickstart
1. Clone the repo and create a virtual environment:
   ```sh
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```
2. Edit `config/config.toml` to match your data and reporting needs.
3. Run the main pipeline:
   ```sh
   python src/main.py
   ```
4. Run tests:
   ```sh
   python -m pytest --maxfail=3 --disable-warnings -v
   ```

## Project Structure
```
charlie-reporting/
├── src/                # Main source code
├── config/             # TOML config
├── tests/              # Unit tests & sample data
├── docs/               # Documentation
├── .vscode/            # VS Code settings
├── requirements.txt    # Python dependencies
├── pyproject.toml      # Build system & metadata
├── README.md           # This file
├── LICENSE             # MIT License
└── .gitignore
```

## Extending
- Add new report types or data sources by subclassing and updating the config.
- All config and column mapping is TOML-based for clarity and future DB integration.

---

*Built with ❤️ by Jonathan Wardwell, Copilot, and GPT-4o inspiration.*
# charlie-reporting