# DevOps Brycsys test task

## Description:

Application finds points where test duration(execution time)
changes and uploads results to database

## Requirements:

- Instaled Python3
- Internet connection

## Installation:

Clone this project from GitHub.

```
git clone https://github.com/SergeyVlK/Bricsys-main-Issue.git
```

## Using:

### Prepearing files:

The source files with the data of the test
results are located in the directory `origin_files/`.

Execute script **prepearing files.py** to prepare files.

After executing the script, the `modified_files/` directory appears.
The prepared files are located in this directory.

### Run:

This block specifies the parameters for connecting to database.<br/>
Parameters are described in file **config.py**

```python
connection = mysql.connector.connect(
    host=config.host,
    user=config.user,
    password=config.password,
    database=config.database,
    port=config.port
)
```

Specify sensitivity value in parameter `limitSlowdownOrSpeedup`.

```python
limitSlowdownOrSpeedup = 20
```

Start **main.py** for execution.

### Results:

As a result of execution, the `points` table appears in database.<br/>
The cell of database contains information about the test number,
the build version, and the percentage of change.

Application **main.py** plots the source points and vertical lines
in the zone of the execution time change.

Plot in `test1`, limitSlowdownOrSpeedup = 20:

![image_test1_20](/pictures/test1_limit_20.png)   


