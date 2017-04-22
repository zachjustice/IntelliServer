## Installation
Install python 2.7
Install pip
Install virtualenv:
```
$ pip install virtualenv
```

## Setup
create virtual environment (specify path if default interpreter is python3):
```
$ cd [IntelliServer/]
$ virtualenv [-p path/to/python2.7] venv  
```

t0 activate virtual environment:

    windows:
```
$ venv\Scripts\activate   
```

    Posix:
```
$ source venv/bin/activate   
```

(to deactivate virtual environment):
```
$ deactivate   
```

install python dependencies using requirements.txt:
    make sure virtual environment is activated
    ```
    $ venv/bin/pip install -r requirements.txt  
    ```


## Usage
  To run IntelliServer on localhost from port 5000:
    make sure virtual environment is activated 
    navigate to django_site/ folder  
    ```
    $ python runserver.py  
    ```

## Coding Conventions
    Follow PEP8    
    Use four spaces for python

## Problems
