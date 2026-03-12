# Group Project

contact Shaan if any questions.

## Tech Stack

- **Python** 3.12+
- **Django** 5.2.x
- **Git**
- **SQLite** for local development

---

## 1. First-Time Setup 

### Install Required Software

Install the following tools first:

- Python
- Git
- Visual Studio Code

After installing Python, open **PowerShell** and check that it works:

```powershell
py --version
```

If that does not work, try:

```powershell
python --version
```

Check that Git is installed:

```powershell
git --version
```

---

## 2. Clone the Project

```powershell
git clone https://github.com/shaanUni/Software-Group-Project.git
cd group-proj
```

---

## 3. Create and Activate a Virtual Environment

Create the virtual environment:

```powershell
py -m venv .venv
```

If `py` does not work, use:

```powershell
python -m venv .venv
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run this once:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate it again:

```powershell
.\.venv\Scripts\Activate.ps1
```

You should now see `(.venv)` at the start of the terminal line.

---

## 4. Install Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If `requirements.txt` does not exist yet, install Django manually:

```powershell
pip install "Django>=5.2,<5.3"
```

Then generate the file with:

```powershell
pip freeze > requirements.txt
```

---

## 5. Run the Project

Apply database migrations:

```powershell
python manage.py migrate
```

Start the development server:

```powershell
python manage.py runserver
```

Open the app in your browser:

```text
http://127.0.0.1:8000/
```
