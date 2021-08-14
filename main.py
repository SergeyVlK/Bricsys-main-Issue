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
    # data['buildid'] = data['buildid'].apply(lambda x: x * coef)
    # data.loc[:, 'buildid'] *= coef
    return data, coef

def outlier_detector(df):
    outlier_detection = DBSCAN(
        eps=0.3,
        metric="euclidean",
        min_samples=10,
        n_jobs=-1)
    clusters = outlier_detection.fit_predict(df)
    return clusters

def outlier_filter(df, clusters_ar):
    df_wo = df.drop(df.index[[i for i, e in enumerate(clusters_ar) if e == -1]])
    cl_wo = np.delete(clusters_ar, np.where(clusters_ar == -1))
    df_wo = df_wo.reset_index(drop=True)
    return df_wo, cl_wo

def plot_source_data(df_source, cl_source, df_wo, cl_wo):
    fig, (ax1, ax2) = plt.subplots(2, 1)
    ax1.set_title("Исходное множество")
    cmap = cm.get_cmap('Accent')
    df_source.plot.scatter(
        x="buildid",
        y="duration",
        c=cl_source,
        cmap=cmap,
        colorbar=False,
        ax=ax1)

    ax2.set_title("Множество без выбросов")
    cmap = cm.get_cmap('Accent')
    df_wo.plot.scatter(
        x="buildid",
        y="duration",
        c=cl_wo,
        cmap=cmap,
        colorbar=False,
        ax=ax2)
    fig.tight_layout()
    plt.show()

def plot_clastered_data(df, cl):
    cmap = cm.get_cmap('Accent')
    df.plot.scatter(
        x="buildid",
        y="duration",
        c=cl,
        cmap=cmap,
        colorbar=False
    )
    plt.show()


def search_points(df, cl, coef):
    buildid_points = []
    duration_persents = []
    prev_index = 0
    for index in range(1, len(cl)):
        if (cl[index] != cl[prev_index]):
            buildid_points.append(int(df.at[index, "buildid"] / coef))
            duration_persents.append(
                (df.at[index, "duration"] - df.at[prev_index, "duration"]) /
                (df.at[prev_index, "duration"]) * 100)
        prev_index = index
    return buildid_points, duration_persents

def main():
    db = mysql.connector.connect(
        host=config.host,
        user=config.user,
        password=config.password,
        database=config.database
    )
    cur = db.cursor()
    cur.execute("DROP TABLE IF EXISTS points;")
    cur.execute("CREATE TABLE IF NOT EXISTS points("
                "buildid INT NOT NULL, "
                "testid INT NOT NULL, "
                "slowdownOrSpeedup FLOAT(5,2) NOT NULL,"
                " PRIMARY KEY (buildid, testid),"
                "CONSTRAINT fk_points_testresults "
                "FOREIGN KEY (testid,buildid) REFERENCES testresults(testid,buildid) "
                "ON UPDATE CASCADE "
                "ON DELETE CASCADE, "
                "CONSTRAINT fk_points_testnames FOREIGN KEY (testid) REFERENCES testnames(id) "
                "ON UPDATE CASCADE "
                "ON DELETE CASCADE);")
    db.commit()
    for test_number in range(1, 5):

        cur.execute("SELECT * FROM testresults WHERE testid=" + str(test_number) + " ORDER BY create_time;")

        sql_data = pd.DataFrame(cur.fetchall())
        sql_data.columns = cur.column_names

        data, coef = normalisation_axis(sql_data)
        clusters = outlier_detector(data)

        data_without_outlier, clusters_without_outlier = outlier_filter(data, clusters)
        # plot_source_data(data, clusters, data_without_outlier, clusters_without_outlier)

        if (test_number == 4):
            data_without_outlier = data_without_outlier[
                (data_without_outlier.duration != 4.) & (data_without_outlier.duration != 6.)]
            data_without_outlier = data_without_outlier.reset_index(drop=True)

            clusters_2_iter = DBSCAN(
                eps=0.1,
                metric="euclidean",
                min_samples=10,
                n_jobs=-1).fit_predict(data_without_outlier[["duration"]])

            # plot_clastered_data(data_without_outlier, clusters_2_iter)
            data_without_outlier, clusters_without_outlier = outlier_filter(data_without_outlier, clusters_2_iter)

        if (test_number == 3):
            data_without_outlier = data_without_outlier[data_without_outlier.duration != 1.]
            data_without_outlier = data_without_outlier.reset_index(drop=True)

            clusters_2_iter = DBSCAN(
                eps=0.3,
                metric="euclidean",
                min_samples=10,
                n_jobs=-1).fit_predict(data_without_outlier[["duration"]])

            # plot_clastered_data(data_without_outlier, clusters_2_iter)
            clusters_without_outlier = clusters_2_iter

        buildid_points, duration_persents = search_points(data_without_outlier, clusters_without_outlier, coef)

        count = 0
        while (count < len(buildid_points)):
            cur.execute("INSERT INTO points(testid, buildid, slowdownOrSpeedup) VALUES({t_id},{b_id},{value});".format(
                t_id=test_number, b_id=buildid_points[count], value=duration_persents[count]))
            count += 1
        db.commit()

    db.close()

def visualization(testid):
    db = mysql.connector.connect(
        host=config.host,
        user=config.user,
        password=config.password,
        database=config.database
    )
    cur = db.cursor()
    cur.execute("SELECT buildid, duration FROM testresults WHERE testid=" + str(testid) + " ORDER BY create_time;")
    data = pd.DataFrame(cur.fetchall())
    data.columns = cur.column_names

    cur.execute("SELECT * FROM points WHERE testid=" + str(testid) + " ORDER BY testid, buildid;")
    rows = cur.fetchall()
    if(len(rows)>0):
        points = pd.DataFrame(rows)
        points.columns = cur.column_names
        plt.vlines(points[["buildid"]], 0, data[["duration"]].max(), color="r", linewidth=5, linestyle="--")

    db.close()

    plt.plot(data[["buildid"]],data[["duration"]])
    plt.show()


# main()
# visualization(4)

def main2():
    db = mysql.connector.connect(
        host=config.host,
        user=config.user,
        password=config.password,
        database=config.database
    )
    cur = db.cursor()

    cur.execute("SELECT buildid, duration FROM testresults WHERE testid=1 ORDER BY create_time;")
    data = pd.DataFrame(cur.fetchall())
    data.columns = cur.column_names
    db.close()

    normed_data = data.copy(deep=True)
    normed_duration = pd.Series(normed_data["duration"] / normed_data["duration"].max())
    normed_data["normed_duration"] =normed_duration

    groups = [] # номера групп
    groups.append(1) # первая точка принадлежит первой группе

    limitSlowdownOrSpeedup = 5  # чувствительность в процентах
    support = 10 # минимальное количество точек в групп, что бы не являться выбросом

    # формирование групп
    for current_index in range(1, len(normed_data)):
        mean_group = pd.Series(normed_data.loc[groups.index(groups[current_index - 1]):len(groups) - 1 - groups[::-1].index(groups[current_index - 1]), "normed_duration"]).mean()
        if (abs(normed_data["normed_duration"].iloc[current_index] - mean_group) < limitSlowdownOrSpeedup / 100):
            groups.append(groups[current_index - 1])
        else:
            print("Среднее группы " + str(groups[current_index -1]) + " = " + str(mean_group))
            groups.append(groups[current_index - 1] + 1)
    print(groups)
    plot_clastered_data(normed_data, groups)


    # удаление выбросов(группы в которых меньше 10 элементов помечаем -1)
    for value in set(groups):
        if(groups.count(value) < support):
            groups = [x if x != value else -1 for x in groups]

    normed_data_without_outliers, groups_without_outliers = outlier_filter(normed_data, np.array(groups))
    plot_clastered_data(normed_data_without_outliers, groups_without_outliers)

    groups_without_outliers_in_groups =[]
    # поиск выбросов внутри групп
    for index in range(len(groups_without_outliers)):
        mean_group = pd.Series(normed_data_without_outliers.loc[groups.index(groups[index]):len(groups) - 1 - groups[::-1].index(groups[index]), "normed_duration"]).mean()
        var_group = pd.Series(normed_data_without_outliers.loc[groups.index(groups[index]):len(groups) - 1 - groups[::-1].index(groups[index]), "normed_duration"]).var()
        sigma = var_group**(1/2)

        if(abs(normed_data_without_outliers["normed_duration"].iloc[index] - mean_group) > 3*sigma):
            groups_without_outliers_in_groups.append(-1)
        else:
            groups_without_outliers_in_groups.append(groups_without_outliers[index])

    normed_data_without_outliers, groups_without_outliers = outlier_filter(normed_data_without_outliers, np.array(groups_without_outliers_in_groups))
    plot_clastered_data(normed_data_without_outliers, groups_without_outliers)







main2()




