import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mysql.connector
from matplotlib import cm

import config

def outlier_filter(df, gr):
    """Удаление точек помеченных """
    gr = np.array(gr)
    df_wo = df.drop(df.index[[i for i, e in enumerate(gr) if e == -1]])
    gr_wo = np.delete(gr, np.where(gr == -1))
    df_wo = df_wo.reset_index(drop=True)
    return df_wo, gr_wo.tolist()


def plot_clastered_data(df, gr):
    """Построить график, в котором точки различных групп имеют различный цвет"""
    cmap = cm.get_cmap('Accent')
    df.plot.scatter(
        x="buildid",
        y="duration",
        c=gr,
        cmap=cmap,
        colorbar=False
    )
    plt.show()




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

def create_result_table(db):
    """Создание результирующей таблицы в базе данных переданной в соединении"""
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

def creating_groups(df, limit):
    """Создание групп точек"""
    groups = []  # номера групп
    groups.append(1)  # первая точка принадлежит первой группе

    # формирование групп
    for current_index in range(1, len(df)):
        mean_group = pd.Series(df.loc[
                               groups.index(groups[current_index - 1]):len(groups) - 1 - groups[::-1].index(
                                   groups[current_index - 1]), "normed_duration"]).mean()
        if (abs(df["normed_duration"].iloc[current_index] - mean_group) < limit / 100):
            groups.append(groups[current_index - 1])
        else:
            groups.append(groups[current_index - 1] + 1)
    return groups

def deleting_outliers_in_groups(df, gr):
    """Удаление выбросов внутри групп по правилу трех сигм"""
    groups_without_outliers_in_groups = []
    # поиск выбросов внутри групп
    for index in range(len(gr)):
        mean_group = pd.Series(df.loc[gr.index(gr[index]):len(gr) - 1 - gr[::-1].index(gr[index]),"normed_duration"]).mean()
        var_group = pd.Series(df.loc[gr.index(gr[index]):len(gr) - 1 - gr[::-1].index(gr[index]),"normed_duration"]).var()
        sigma = var_group ** (1 / 2)

        if (abs(df["normed_duration"].iloc[index] - mean_group) > 3 * sigma):
            groups_without_outliers_in_groups.append(-1)
        else:
            groups_without_outliers_in_groups.append(gr[index])
    return groups_without_outliers_in_groups

def find(df, gr, limit):
    """Поиск точек существенного измения"""
    buildid_points = []
    duration_persents = []
    prev_index = 0
    for index in range(1, len(gr)):
        if (gr[index] != gr[index - 1]):
            mean_group_prev = pd.Series(df.loc[gr.index(gr[index - 1]):len(gr) - 1 - gr[::-1].index(gr[index - 1]),"normed_duration"]).mean()
            mean_group_current = pd.Series(df.loc[gr.index(gr[index]):len(gr) - 1 - gr[::-1].index(gr[index]),"normed_duration"]).mean()

            if (abs(mean_group_current - mean_group_prev) * 100 > limit):
                duration_persents.append(abs(mean_group_current - mean_group_prev) * 100)
                buildid_points.append(df["buildid"].iloc[index])



    return buildid_points, duration_persents

def main():
    connection = mysql.connector.connect(
        host=config.host,
        user=config.user,
        password=config.password,
        database=config.database
    )
    # create_result_table(connection)
    cursor = connection.cursor()



    for test_id in range(1, 5):

        cursor.execute("SELECT buildid, duration FROM testresults WHERE testid=" + str(test_id) +" ORDER BY create_time;")
        data = pd.DataFrame(cursor.fetchall())
        data.columns = cursor.column_names


        normed_data = data.copy(deep=True)
        normed_duration = pd.Series(normed_data["duration"] / normed_data["duration"].max())
        normed_data["normed_duration"] =normed_duration


        limitSlowdownOrSpeedup = 20  # чувствительность в процентах

        # формирование групп
        groups = creating_groups(normed_data, limitSlowdownOrSpeedup)
        plot_clastered_data(normed_data, groups)


        # удаление выбросов(группы в которых меньше 10 элементов помечаем -1)
        support = 10  # минимальное количество точек в групп, что бы не являться выбросом
        for value in set(groups):
            if(groups.count(value) < support):
                groups = [x if x != value else -1 for x in groups]

        normed_data_without_outliers, groups_without_outliers = outlier_filter(normed_data, groups)

        # поиск выбросов внутри групп
        groups_without_outliers_in_groups = deleting_outliers_in_groups(normed_data_without_outliers, groups_without_outliers)
        finaly_normed_data, finaly_groups = outlier_filter(normed_data_without_outliers, groups_without_outliers_in_groups)
        # print(finaly_groups)
        buildid_points ,duration_persents = find(finaly_normed_data, finaly_groups, limitSlowdownOrSpeedup)
        print(buildid_points)
        print(duration_persents)
        plt.vlines(buildid_points, 0, data["duration"].max(), color="r", linewidth=1, linestyle="--")
        plt.plot(data["buildid"], data["duration"])
        plt.show()

    connection.close()

    # while (count < len(buildid_points)):
    #     cur.execute("INSERT INTO points(testid, buildid, slowdownOrSpeedup) VALUES({t_id},{b_id},{value});".format(
    #         t_id=test_number, b_id=buildid_points[count], value=duration_persents[count]))
    #     count += 1
    # db.commit()

main()




