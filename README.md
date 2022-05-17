# Audit Trail Service

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg?style=for-the-badge)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.7](https://img.shields.io/badge/python-3.7-green?style=for-the-badge)](https://www.python.org/)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/PilotDataPlatform/audit-trail/ci?style=for-the-badge)


## About

Service for managing audit logs.

### Start

1. Install [Docker](https://www.docker.com/get-started/).
2. Start container with project application.

       docker compose up

3. Visit http://127.0.0.1:5078/v1/api-doc for API documentation.

### Development

1. Install [Poetry](https://python-poetry.org/docs/#installation).
2. Install dependencies.

       poetry install

3. Add environment variables into `.env` taking in consideration `.env.schema`.
4. Run application.

       poetry run python run.py
