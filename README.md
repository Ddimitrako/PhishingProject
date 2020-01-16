# SBAM
Security Behaviour Analysis Module (EnergyShield)

## Installation Guide _(for developers)_
This installation is tailored to PyCharm IDE and Windows 10.

### Requirements
In order to contribute to the **development** of the Security Behaviour Analysis Module,
you shall need to create a workplace with the below requirements:
* VCS (Version Control System Client): **[Git](https://git-scm.com/downloads)**
* Python IDE: **[PyCharm](https://www.jetbrains.com/pycharm/download/#section=windows)**
* Database: **[PostgreSQL](https://www.postgresql.org/download/)**
* Database Client: **[pgAdmin](https://www.pgadmin.org/download/)** or 
**[DataGrid](https://www.jetbrains.com/datagrip/)**

### Installation Steps
1. Import project in PyCharm:
    * Use git to **clone** sbam repository from **[github](https://github.com/angeorg83/sbam.git)** 
    * Open the project in PyCharm: `File -> Open`
    
         **OR** 
    
    * Directly in PyCharm: `VCS -> Git -> Clone`
2. Create a new virtual environment:
    * Install python package for **virtualenv** on windows:
            
            pip install virtualenvwrapper-win
    * Create a new virtual environment for the project:
            
            mkvirtualenv <project_name>
    * Introduce the newly created virtual environment in PyCharm: `File-> Settings -> Project 
    -> Project Intepreter -> Add -> Existing Environment`
    
         **OR** 
    
    * Directly in PyCharm: `File-> Settings -> Project -> Project Intepreter -> Add -> New Environment` 
3. Install required packages:
        
        pip install -r requirements.txt
    
    **OR** 
    
    Navigate in PyCharm to file `requirements.txt` and accept recommended automatic installation hint 
    at the top of the editor.<br>
    **Note**: If package `psycopg2`, or any other, fail to install, download `pip` latest version from
     _Project Intepreter_.
4. Add Configuration:

        Name: sbam 
        Host: 127.0.0.1 
        Python intepreter: the newly created one
        Working Directory: Top directory of the project
5. In `sbam -> settings` create a new `.env` file by copying the `.env.example` file in the same directory:

        # Template file used to host environmental variables.
        #
        # Use it to generate a .env file in the same directory
        # with all necessary variables based on specific environment.
        #
        DEBUG=on
        SECRET_KEY=your-secret-key
        DATABASE_URL=psql://username:password@hostname:port/database
        SQLITE_URL=sqlite:///my-local-sqlite.db
        TIME_ZONE='UTC'
   **Note 1**: Make sure to create a dedicated **database schema** for the project 
   (e.g. `sbam`) to your PostgreSQL DB.<br>
   **Note 2**: DB user defined in `DATABASE_URL` needs to have proper **DML privileges**.
7. Migrate all committed migrations to properly update the database schema:
        
        py manage migrate
8. Run the project:

        py manage runserver
9. Enjoy developing!
