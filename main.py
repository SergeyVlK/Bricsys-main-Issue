import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mysql.connector

import config

db = mysql.connector.connect(
    host=config.host,              # your host, usually localhost
    user=config.user,            # your username
    password=config.password,        # your password
    database=config.database     # name of the data base
)


cur = db.cursor()

cur.execute("SELECT * FROM testresults WHERE testid=2 ORDER BY create_time;")

# Put it all to a data frame
sql_data = pd.DataFrame(cur.fetchall())
sql_data.columns = cur.column_names

# Close the session
db.close()