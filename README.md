# SBAM
Security Behaviour Analysis Module (EnergyShield)

# Installation Guide
This installation is tailored to the Pycharm IDE and Windows 10.

## Pre Install steps
1. Install Git - https://git-scm.com/downloads
2. Install Pycharm - https://www.jetbrains.com/pycharm/download/#section=windows
3. Install PG admin and postgre - https://www.pgadmin.org/download/

## Installation Steps - Pycharm
1. Import project from CVS or Github
2.Create new virtual environment - Settings -> Project -> Project Intepreter -> Add local
3.Go to requirements.txt - Install requirements (If psycopg2 or any other install fail , make sure to download latest version of pip from Project Intepreter)
4. Add Configuration - Name: sbam , Host: 127.0.0.1 , Python intepreter: make sure it is the newly created one, Working Directory: Should be the top directory of the project
5. Makemigrations(May not be needed)
6. Migrate
7. All set
