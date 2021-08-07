import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mysql.connector

import config

db = mysql.connector.connect(
    host=config.host,
    user=config.user,
    password=config.password,
    database=config.database
)


cur = db.cursor()

cur.execute("SELECT * FROM testresults WHERE testid=2 ORDER BY create_time;")

# Put it all to a data frame
sql_data = pd.DataFrame(cur.fetchall())
sql_data.columns = cur.column_names

# Close the session
db.close()

plt.plot(sql_data["buildid"], sql_data["duration"], label='Original')

spectr_sin = np.fft.rfft(sql_data["duration"])

# print(spectr_sin)
spectr_sin[:200] = 0
spectr_sin[260:] = 0
Y = np.fft.irfft(spectr_sin)
# # print("len(x) = " + str(len(sql_data)))
# # print("len(Y) = " + str(len(Y)))
if(len(Y) != len(sql_data)):
    plt.plot(sql_data["buildid"][:-1], Y, label='Transformed')
else:
    plt.plot(sql_data["buildid"], Y, label='Transformed')
plt.legend(loc=0)
plt.grid(True)
plt.show()