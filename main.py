import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mysql.connector
from sklearn.cluster import DBSCAN
from matplotlib import cm

import config

def normalisation_axis(df):
    # Normalisation axis 'buildid'
    # (что бы вклад в расстояние по оси 'buildid' был соизмерим с вкладом 'duration'
    duration_min = df["duration"].min()
    duration_max = df["duration"].max()

    buildid_min = df["buildid"].min()
    buildid_max = df["buildid"].max()

    coef = (duration_min + duration_max) / (buildid_min + buildid_max)

    data = df[["buildid", "duration"]]
    data["buildid"] *= coef
    return data, coef

def outlier_detector(df):
    outlier_detection = DBSCAN(
        eps=0.3,
        metric="euclidean",
        min_samples=10,
        n_jobs=-1)
    clusters = outlier_detection.fit_predict(df)
    return clusters


# test_number = int(input("Enter number of test: "))
test_number = 4

db = mysql.connector.connect(
    host=config.host,
    user=config.user,
    password=config.password,
    database=config.database
)


cur = db.cursor()

cur.execute("SELECT * FROM testresults WHERE testid=" + str(test_number) + " ORDER BY create_time;")

# Put it all to a data frame
sql_data = pd.DataFrame(cur.fetchall())
sql_data.columns = cur.column_names

# Close the session
db.close()


data, coef = normalisation_axis(sql_data)
clusters = outlier_detector(data)


data_without_outlier = data.drop(data.index[[i for i, e in enumerate(clusters) if e == -1]])
clusters_without_outlier = [value for value in clusters if value != -1]


fig, (ax1, ax2) = plt.subplots(2, 1)
ax1.set_title("Исходное множество")
cmap = cm.get_cmap('Accent')
sql_data.plot.scatter(
  x = "buildid",
  y = "duration",
  c = clusters,
  cmap = cmap,
  colorbar = False,
  ax= ax1)

ax2.set_title("Множество без выбросов")
cmap = cm.get_cmap('Accent')
data_without_outlier.plot.scatter(
  x = "buildid",
  y = "duration",
  c = clusters_without_outlier,
  cmap = cmap,
  colorbar = False,
  ax= ax2)
fig.tight_layout()
plt.show()


if(test_number == 4):
    data_without_outlier  = data_without_outlier[(data_without_outlier.duration != 4.) & (data_without_outlier.duration != 6.)]


    clusters_2_iter = DBSCAN(
      eps = 0.1,
      metric="euclidean",
      min_samples = 10,
      n_jobs = -1).fit_predict(data_without_outlier[["duration"]])

    cmap = cm.get_cmap('Accent')
    data_without_outlier.plot.scatter(
      x = "buildid",
      y = "duration",
      c = clusters_2_iter,
      cmap = cmap,
      colorbar = False
    )
    plt.show()

# print(list(clusters_2_iter))



