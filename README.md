# Personal AI System

![PyPI version](https://img.shields.io/pypi/v/personal_ai_system.svg)

Personalised Multi Agents

* [GitHub](https://github.com/Natasha3101/personal_ai_system/) | [PyPI](https://pypi.org/project/personal_ai_system/) | [Documentation](https://Natasha3101.github.io/personal_ai_system/)
* Created by [Natasha Saldanha](https://audrey.feldroy.com/) | GitHub [@Natasha3101](https://github.com/Natasha3101) | PyPI [@Natasha3101](https://pypi.org/user/Natasha3101/)
* MIT License

## Features

* TODO

## Documentation

Documentation is built with [Zensical](https://zensical.org/) and deployed to GitHub Pages.

* **Live site:** https://Natasha3101.github.io/personal_ai_system/
* **Preview locally:** `just docs-serve` (serves at http://localhost:8000)
* **Build:** `just docs-build`

API documentation is auto-generated from docstrings using [mkdocstrings](https://mkdocstrings.github.io/).

Docs deploy automatically on push to `main` via GitHub Actions. To enable this, go to your repo's Settings > Pages and set the source to **GitHub Actions**.

## Development

To set up for local development:

```bash
# Clone your fork
git clone git@github.com:your_username/personal_ai_system.git
cd personal_ai_system

# Install in editable mode with live updates
uv tool install --editable .
```

This installs the CLI globally but with live updates - any changes you make to the source code are immediately available when you run `personal_ai_system`.

Run tests:

```bash
uv run pytest
```

Run quality checks (format, lint, type check, test):

```bash
just qa
```

## Author

Personal AI System was created in 2026 by Natasha Saldanha.

Built with [Cookiecutter](https://github.com/cookiecutter/cookiecutter) and the [audreyfeldroy/cookiecutter-pypackage](https://github.com/audreyfeldroy/cookiecutter-pypackage) project template.
