# Group Project

contact Shaan if any questions.

## Tech Stack

- **Python** 3.12+
- **Django** 5.2.x
- **Git**
- **SQLite** for local development

---

## PROJECT SETUP ON WINDOWS MACHINE

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

## 3. Run this command to allow scripts to run

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

## 4. Run the Setup Script

```powershell
.\win_setup.ps1
```

Open the app in your browser:

```text
http://127.0.0.1:8000/
```

## PROJECT SETUP ON MACOS
### Follow these steps:

#### 1. Make sure you have python installed on your machine
Run the following command:
```
python3 --version
```
If you don't have python installed, google how to install it on mac.
I would suggest using homebrew.


#### 2. Clone the project in your local machine
```
git clone https://github.com/shaanUni/Software-Group-Project.git
```

#### 3. Find the mac_setup.sh file and set the right permissions using terminal
```
chmod +x mac_setup.sh
```

#### 4. Run the setup script
```
./mac_setup.sh
```

#### 5. You're good to go!
Visit http://localhost:8000/

## Front end team

I have made a folder called mockups. This will be seperate to the backend, so you can do front end work as you please here:
http://localhost:8000/mockups/

