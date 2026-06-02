# AI StudyMate

AI StudyMate is an AI-powered LeetCode study assistant for Windows. It tracks solved problems, syncs progress to **Google Sheets** and **Notion**, analyzes your weak topics with **Coral SQL**, recommends problems with **Gemini**, and can schedule study sessions into **Google Calendar**.

Built for learners and hackathons: no Docker required, no paid platforms required, and the repo is ready for GitHub.

---

## Project workflow

1. Configure backend credentials and integration secrets.
2. Start the backend and frontend.
3. Use the UI to mark problems solved and view AI recommendations.
4. Connect Google Calendar to schedule study sessions automatically.

---

## Quick start

### 1. Open the project

Open `d:/mystudymate` in VS Code or your editor.

### 2. Configure environment variables

Copy the example file:

```powershell
copy backend\.env.example backend\.env
```

Edit `backend/.env` and add your values.

### 3. Add Google Sheets credentials

Save your Google service account key as:

```text
backend/credentials.json
```

### 4. Optional: Add Google Calendar OAuth client

Save your OAuth client file as:

```text
backend/google_oauth_client.json
```

And add any calendar-specific configuration to `.env` if needed.

### 5. Start the project

Run the launcher:

```powershell
start_project.bat
```

This will:

- create a Python virtual environment
- install backend dependencies
- download Coral into `backend/coral/`
- start the backend on `http://127.0.0.1:8000`
- start the frontend on `http://127.0.0.1:5173`

---

## What to configure

Copy `backend/.env.example` to `backend/.env` and fill in the keys.

| Variable | Purpose |
|----------|---------|
| `NOTION_API_KEY` | Notion integration token ([create integration](https://www.notion.so/my-integrations)) |
| `NOTION_DATABASE_ID` | Notion database ID for LeetCode progress |
| `GOOGLE_SHEET_NAME` | Google Sheets title (default: `AI StudyMate LeetCode Progress`) |
| `GEMINI_API_KEY` | Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey) |
| `GOOGLE_CREDENTIALS_PATH` | Path to service account JSON (default: `credentials.json`) |

> Note: Google Sheets integration uses a service account JSON file, not a plain API key.

---

## Google Sheets setup

1. In Google Cloud Console, create a project.
2. Enable APIs: Google Sheets API and Google Drive API.
3. Create a service account and download the JSON key.
4. Save it as `backend/credentials.json`.
5. Run:

```powershell
python scripts\setup_google_sheet.py
```

6. If necessary, open the spreadsheet URL printed by the script and share the sheet with the service account email as Editor.

### Auto-created sheet columns

- `problem`
- `topic`
- `difficulty`
- `status`
- `time_taken`
- `weakness_score`
- `date_solved`

---

## Notion setup

1. Create a Notion integration at https://www.notion.so/my-integrations.
2. Create a database with these properties:
   - **Problem Name** (title)
   - **Topic** (text)
   - **Difficulty** (select: Easy, Medium, Hard)
   - **Status** (select: Solved, Unsolved, In Progress)
   - **Time Taken** (number)
   - **Date** (date)
   - **Platform** (select: LeetCode)
3. Share the database with your integration.
4. Put the database ID into `NOTION_DATABASE_ID`.
5. Verify the integration:

```powershell
python scripts\setup_notion.py
```

---

## Google Calendar setup

1. Create an OAuth client in Google Cloud Console.
2. Add `http://127.0.0.1:8000/calendar/oauth2callback` as an authorized redirect URI.
3. Download the OAuth client JSON and save it as:

```text
backend/google_oauth_client.json
```

4. In the app, click **Connect Google Calendar** and complete the consent flow.
5. Refresh calendar status in the UI, then click **Schedule to Calendar** to create study sessions.

---

## Application workflow

### Backend

- `backend/app/main.py` starts a FastAPI server.
- Routes include:
  - `POST /solve` — log solved problems and sync to Sheets, Notion, and Coral
  - `GET /recommend` — return AI recommendations and weak topics
  - `GET /stats` — summary stats
  - `POST /calendar/schedule` — schedule recommended study sessions
  - `GET /calendar/auth_url` — start Google Calendar auth flow
  - `GET /calendar/status` — check if calendar is connected

### Frontend

- Uses React, Vite, and Tailwind.
- Displays AI recommendations and an option to connect Google Calendar.
- Schedules recommended problems as calendar events.

---

## Coral SQL

Coral is installed at `backend/coral/coral.exe`.

Configure it with:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\configure_coral.ps1
```

Queries can analyze weak topics and unsolved problems.

Example:

```sql
SELECT topic, AVG(weakness_score) AS avg_weak
FROM sheets.leetcode_progress
GROUP BY topic
ORDER BY avg_weak DESC;
```

Run Coral tests:

```powershell
powershell -File scripts\test_coral_sql.ps1
```

---

## Repository structure

```text
mystudymate/
├── backend/          # FastAPI backend, services, Coral files
├── frontend/         # React + Vite frontend
├── scripts/          # setup and helper scripts
├──  # project bootstrapper
└── README.md   # this documentation
```

---

## GitHub-ready notes

- Keep `backend/.env`, `backend/credentials.json`, and `backend/google_oauth_client.json` out of version control.
- Use `.gitignore` to exclude generated files, tokens, and local secrets.
- Commit only source code, scripts, and documentation.

---

## Troubleshooting

- If the frontend cannot connect: verify the backend is running at `http://127.0.0.1:8000`.
- If Google Calendar auth fails: confirm the redirect URI is registered.
- If Notion sync fails: ensure `NOTION_API_KEY` and `NOTION_DATABASE_ID` are correct.
- If Google Sheets setup fails: ensure the service account has Editor access to the spreadsheet.
- If PowerShell scripts are blocked:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

---

## License

MIT License — free to use for learning, hackathons, and personal projects.
