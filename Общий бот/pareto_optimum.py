import pandas as pd
from geopy.distance import geodesic # для расчета расстояния между точками
import numpy as np # для работы с np.nan

# Алгоритм поиска парето-оптимальных строк
def is_dominated(row, other_row):
    """Проверка, доминирует ли строка other_row над строкой row."""
    return all(other_row <= row) and any(other_row < row)


def find_pareto_optimal(df):
    pareto_optimal = []
    for i, row in df.iterrows():
        dominated = False
        for j, other_row in df.iterrows():
            if i != j and is_dominated(row, other_row):
                dominated = True
                break
        if not dominated:
            pareto_optimal.append(row)
    return pd.DataFrame(pareto_optimal)


def df_pareto_optimum(df_result, df_source, questions_answers_list, goal_coords):
    '''
    Описание: Здесь происходит поиск парето-оптимальных решений
    для датафреймов размерностью больше 5.

    Входные параметры:

    df_result - датафрйем после фильтров
    df_source - исходный датафрейм со всеми атрибутами (по нему будет в дальнейш формироваться pdf-файл)
    questions_answers_list - список словарей вопросов-ответов пользователя
    goal_coords - координаты идеального помещения

    Выходные данные:
    df_source_ - скорректированный исходный датафрейм df_source
    с найденными парето-оптимальными решениями

    '''

    # отбираем только те количественные поля, которые были упомянуты в диалоге
    number_columns = [list(x.keys())[0] for x in questions_answers_list if list(x.keys())[0] in ["Площадь", "Район",
                                                                                                 "Стоимость объекта, руб. (покупки или месячной аренды)"]]

    df_result["Район"] = df_result["Координаты (точка)"]

    # Определяем ранги числовых полей
    df_corrected = pd.DataFrame()
    if 'Район' in number_columns:
        df_corrected['dist'] = df_result.apply(lambda x: geodesic(goal_coords,
                                                                  x["Район"].split(",")[::-1]).kilometers, axis=1)
        df_corrected["dist_rank"] = df_corrected["dist"].rank(method="dense")
        df_corrected.drop("dist", axis=1, inplace=True)

    if "Стоимость объекта, руб. (покупки или месячной аренды)" in number_columns:
        df_corrected["cost"] = df_result["Стоимость объекта, руб. (покупки или месячной аренды)"].str.replace(",",
                                                                                                              ".").astype(
            float)
        df_corrected["cost_rank"] = df_corrected["cost"].rank(method="dense")
        df_corrected.drop("cost", axis=1, inplace=True)

    if "Площадь" in number_columns:
        df_corrected["area"] = df_result["Площадь"].str.replace(",", ".").astype(float)
        df_corrected["area_rank"] = df_corrected["area"].rank(method="dense")
        df_corrected.drop("area", axis=1, inplace=True)

    df_pareto_optimal = find_pareto_optimal(df_corrected)
    df_pareto_optimal["is_pareto_optimum"] = 1

    if df_pareto_optimal.shape[0] < 5:
        df_pareto_optimal_ = find_pareto_optimal(df_corrected.drop(index=df_pareto_optimal.index))
        df_pareto_optimal_ = df_pareto_optimal_.sample(5 - df_pareto_optimal.shape[0])
        df_pareto_optimal = pd.concat([df_pareto_optimal, df_pareto_optimal_]).replace(np.nan, 0)

    elif df_pareto_optimal.shape[0] > 5:
        df_pareto_optimal = df_pareto_optimal.sample(5)
    else:
        pass

    df_source_0 = df_source.loc[df_pareto_optimal.query("is_pareto_optimum == 0").index][:]
    df_source_0["is_pareto_optimum"] = 0

    df_source_1 = df_source.loc[df_pareto_optimal.query("is_pareto_optimum == 1").index][:]
    df_source_1["is_pareto_optimum"] = 1

    df_source_ = pd.concat([df_source_0, df_source_1])

    return df_source_