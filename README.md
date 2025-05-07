# CSI3335 Project Virtual Environment

### Python Version:

- Make sure the python version is either 3.12 or 3.13.1

## Description

This virtual environment contains essential Python libraries and frameworks required for the project. The `requirements.txt` file lists all the dependencies.

## Instructions


1. **Clone the Repository**:

```bash
git clone https://github.com/sanjelarun/csi3335-project-venv.git
cd csi3335-project-venv
```

2. **Create a Virtual Environment**

**For Windows**
```bash
python -m venv project_env
```
**For Linux/MacOs**
```bash
python3 -m venv project_env

```
3. **Activate the Virtual Environment**

**For Windows**
```bash
.\project_env\Scripts\activate
```
**For Linux/MacOs**
```bash
source project_env/bin/activate
```

4. **Install the dependencies**
```bash
pip install -r requirements.txt
```

5. **Set the FLASK_APP environment variable(This will be the sql dump):
```bash
export FLASK_APP=run.py

if this doesnt work then run 'python run.py' in the command line while mariadb is running.
Also make sure the baseball database is present in your maraiadb
```

6. **Running the flask development server
```bash
flask run
```

## Additional Info

1. **Admin information**
   - The information is preloaded into the database so you DO NOT need to register the admin account in the registration page. To log in as an admin, enter the admin username and password into the login page. These can be found below
     
   - Username: 'Admin'
   - Password: 'adminpassword'
     

2. **Divisions Extended**

- The divisions table now displays the teams and their divisions
- division_stint attribute number describes how many times the team switched divisions. If a division has a value of 2, hat means it's been in 2 divisions in its lifetime in baseball.


