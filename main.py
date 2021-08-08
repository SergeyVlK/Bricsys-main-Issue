import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mysql.connector
from sklearn.cluster import DBSCAN

import config

db = mysql.connector.connect(
    host=config.host,
    user=config.user,
    password=config.password,
    database=config.database
)


cur = db.cursor()

cur.execute("SELECT * FROM testresults WHERE testid=3  ORDER BY create_time;")

# Put it all to a data frame
sql_data = pd.DataFrame(cur.fetchall())
sql_data.columns = cur.column_names
# print(sql_data[["target", "name", "testnode"]])

# Close the session
db.close()

# plt.plot(sql_data["buildid"], sql_data["duration"], label='Original')
#
#
# plt.legend(loc=0)
# plt.grid(True)
# plt.show()
duration_min =  sql_data["duration"].min()
duration_max =  sql_data["duration"].max()

buildid_min =  sql_data["buildid"].min()
buildid_max =  sql_data["buildid"].max()

coef = (duration_min + duration_max) / (buildid_min + buildid_max)



data= sql_data[["buildid", "duration"]]
data["buildid"] *= coef
print(data.head())
outlier_detection = DBSCAN(
  eps = 0.3,
  # metric="euclidean",
  metric="l1",
  min_samples = 3,
  n_jobs = -1)
clusters = outlier_detection.fit_predict(data)


print(len(set(clusters)))
print(set(clusters))


from matplotlib import cm
cmap = cm.get_cmap('Accent')
sql_data.plot.scatter(
  x = "buildid",
  y = "duration",
  c = clusters,
  cmap = cmap,
  colorbar = False
)
plt.show()
