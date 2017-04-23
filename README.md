## Installation
Install python 2.7
Install pip
Install virtualenv:
```
$ pip install virtualenv
```

## Setup
Download the repository either manually or with git.

Configure IntelliServer's database connection by creating a .db_config file in the api folder with the following contents:
```
[database_user]
[database_password]
[host]
[database_name]
```
IntelliServer is configured for use with PostgreSQL.

Create a virtual environment (specify the path if the default interpreter is python3):
```
$ cd [IntelliServer/]
$ virtualenv [-p path/to/python2.7] venv  
```

To activate the virtual environment:

    windows:
```
$ venv\Scripts\activate   
```

    Posix:
```
$ source venv/bin/activate   
```

To deactivate the virtual environment:
```
$ deactivate   
```

Install python dependencies using requirements.txt:
    make sure the virtual environment is activated
    ```
    $ venv/bin/pip install -r requirements.txt  
    ```


## Usage
  To run IntelliServer from your localhost on port 5000:
    make sure the virtual environment is activated 
    navigate to your IntelliServer/ folder  
    ```
    $ python runserver.py  
    ```

## Coding Conventions
    Follow PEP8    
    Use four spaces for python

## Problems
* entity/meal_plans POST route allows users to generate multiple meals for a single day. (e.g. two breakfasts for the same date.) Only one breakfast will be displayed in the android application.
