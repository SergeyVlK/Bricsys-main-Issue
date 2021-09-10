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

![image test 1 20](/pictures/test1_limit_20.png) 

Plot in `test2`, limitSlowdownOrSpeedup = 30:

![image test 2 30](/pictures/test2_limit_30.png) 

In database, results are displayed in this form:

```mysql
mysql> SELECT * FROM points ORDER BY testid, buildid;
+---------+--------+-------------------+
| buildid | testid | slowdownOrSpeedup |
+---------+--------+-------------------+
|   78818 |      1 |             31.16 |
|   83044 |      1 |             28.46 |
|   78818 |      2 |             70.41 |
|   60286 |      4 |             27.58 |
+---------+--------+-------------------+
4 rows in set (0.09 sec)
```

## Additional information:

MySQL Server is running in a debian virtual machine on my laptop.
main.py connects to a rented VPS with a white ip. The server is running
OpenVPN server. Requests for a non-standard port are forwarded to the 
OpenVPN client running on debian.