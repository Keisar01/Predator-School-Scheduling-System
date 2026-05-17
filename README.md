# School-Schedule-System

Flask-based school scheduling system with user, admin, and superadmin roles.

## Prerequisites

- Python 3.10+ (you are using Python 3.14, which is fine)
- PowerShell

## How to Run (Windows / PowerShell)

1. Open PowerShell in the project root:

```powershell
cd "D:\3-6\IntegrativePrograming\Predator's Event Planner\School-Schedule-System-main"
```

2. Create and activate a virtual environment:

```powershell
C:/Python314/python.exe -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

4. Run the app:

```powershell
python ".\Predator System\app.py"
```



## Default Superadmin

The app auto-creates/restores this account on startup:

- Username: `superadmin`
- Password: `1234`


## Default Admin
- Username: `Supabase`
- Password: `1234`

## Default User
- Username: `supa`
- Password: `1234`
