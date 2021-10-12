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
    
         **or** 
    
    * Directly in PyCharm: `VCS -> Git -> Clone`
2. Create a new virtual environment:
    * Install python package for **virtualenv** on windows:
            
            pip install virtualenvwrapper-win
    * Create a new virtual environment for the project:
            
            mkvirtualenv <project_name>
    * Introduce the newly created virtual environment in PyCharm: `File-> Settings -> Project 
    -> Project Intepreter -> Add -> Existing Environment`
    
         **or** 
    
    * Directly in PyCharm: `File-> Settings -> Project -> Project Intepreter -> Add -> New Environment` 
3. Install required packages:
        
        pip install -r requirements/requirements_base.txt
        pip install -r requirements/requirements_dev.txt
    
    **_Note_**: If package `psycopg2`, or any other, fail to install, download `pip` latest version from
     _Project Intepreter_.
4. Add Configuration:

        Name: sbam 
        Host: 127.0.0.1 
        Python intepreter: the newly created one
        Working Directory: Top directory of the project
5. In `.env -> dev` create a new `.env_app_dev` file by copying the `.env_app_dev.template` and create a new `.env_db_dev` file by copying the `.env_db_dev.template` file in the same directory

   **_Note 1_**: Make sure to create a dedicated **database schema** for the project 
   (e.g. `sbam`) to your PostgreSQL DB.<br>
   
6. In order to use the development settings set DJANGO_DEVELOPMENT=True

8. Load data to the database using django **fixtures** directory:

        py manage.py loaddata sbam_app/fixtures/<json file>
        
   **_Note_**: Below you may find a brief presentation of the available fixtures. In 
   order to successfully import part or all of them, follow the suggested priority.
      
   | Priority | Fixture | Contents | 
   |---	|--- |--- |
   | 1 | `sbam_app/fixtures/security_culture_model.json` | **_Security Culture Model_** containing levels, dimensions & domains |
   | 2 | `sbam_app/fixtures/default_question_types.json` | Default question types (e.g. Yes/No, percentages) |
   | 3 | `py manage.py generate_default_question_types`| Command that generates default question options based on previously inserted question types |
   | 4 | `sbam_app/fixtures/sample_questionnaire.json` | Sample questionnaire (dummy) |
   | 5 | `sbam_app/fixtures/sample_data.json` | Sample data (including users, groups, questionnaires, questions types, etc.) |

9. Run the project:

        py manage runserver
   
10. Create ER Diagram:
    
         python manage.py graph_models -a -o SBAM_UML_DIAGRAM.png  settings=sbam.settings.base_settings


10. Enjoy developing!


## Kafka Installation Guide and  Testing _(for developers)_
STEP 1: Install JAVA 8 SDK

STEP 2: 

    Download Apache Kafka Binaries,   
    Create "kafka" folder in C directory,
	Paste all kafka binaries there

STEP 3: 

     Create Data folder for Zookeeper and Apache Kafka,	
	 Then Create “data” folder inside kafka folder,
	 and Kafka / Zookeeper directories inside data folder

STEP 4:Change the default configuration value

	A)Update zookeeper data directory path in “config/zookeeper.Properties” configuration file to -->	dataDir=C:\kafka\data\zookeeper
	B)Update Apache Kafka log file path in “config/server.properties” configuration file to --> log.dirs=C:\kafka\data\kafka

STEP 5:	Start Zookeeper Server
	
    open cmd - run as administrator
	cd to C:\kafka\bin\windows>
	type and run to start server--> zookeeper-server-start.bat  ../../config/zookeeper.properties

STEP 6:Start Kafka Server

    type and run to start server--> kafka-server-start.bat  ../../config/server.properties

To examine KAFKA messages:

    bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic KTOP04-0 --from-beginning
    or  download kafkamagic https://www.kafkamagic.com/download/?v2
    run on http://localhost:5000

TroubleShooting 

    Message -->Kafka - Broker fails because all log dirs have failed
    delete folders kafkadatakafka & kafkadatazookeeper (they will reproduce itselfs)

## How to generate encypted - shortened url links
STEP 1: 

    go to https://www.rebrandly.com/

STEP 2: 

    Create a free acount 
    Select Rebrand a new link
    Add the destination url
    Generate the shortened url 

STEP 3: 

    Go to .env->dev->.env_app_prod and .env_app_dev
    Replace encrypted_link from ENCRYPTED_ENDPOINT=encrypted_link
    with the result url

Note:

    If the ip and/or port changes it needs a new shortened url
    If "Stop! Deceptive page ahead!" when hitting url you need to 
    generate link after logging to step 1.
Example:
   
    for phishing email simulation in simavi vm 
    converting http://195.82.131.51:8080/sim_endpoint/ 
    generates --> https://rb.gy/mzomsd