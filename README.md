# RANGISHA

RANGISHA is a Flask-based lost-and-found web app. People can report lost or found documents, browse registered found documents, and send questions to the help desk. The interface supports English and Kinyarwanda.

## Features

- Report lost documents and submit found-document reports.
- Browse found documents; owners' names are masked in the public listing.
- Send questions through the help desk form.
- Manage reports and add found-document listings through the admin page.
- Store submitted entries in a local SQLite database.

## Requirements

- Python 3.9 or newer
- pip

## Run locally on Windows

Open PowerShell in the project folder and run:

```powershell
.\.venv\Scripts\Activate.ps1
cd .\rangisha
python -m pip install -r requirements.txt
python app.py
```

If PowerShell says script execution is disabled, activate the environment using:

```powershell
.\.venv\Scripts\python.exe -m pip install -r .\rangisha\requirements.txt
Push-Location .\rangisha
..\.venv\Scripts\python.exe app.py
```

## Project layout

```text
.
├── .venv/                 # Local Python virtual environment
├── .vscode/               # VS Code launch configuration
├── rangisha/
│   ├── app.py             # Flask routes and application logic
│   ├── requirements.txt   # Python dependencies
│   ├── translations.py    # English and Kinyarwanda text
│   ├── rangisha.db        # Local SQLite database (created/used at runtime)
│   ├── static/            # CSS and JavaScript
│   └── templates/         # HTML templates
└── README.md
```
