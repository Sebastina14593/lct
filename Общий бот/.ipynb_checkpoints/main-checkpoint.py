#Уберем предупреждения, чтобы они не загромождали вывод
import warnings
warnings.filterwarnings('ignore')

import pandas as pd # для считывания Excel-файла

from geopy.geocoders import Yandex # для вычисления координат

import os
from dotenv import load_dotenv
load_dotenv()
auth = os.getenv('AUTH')
api_key = os.getenv('API_KEY')

geolocator = Yandex(api_key=api_key)

from pareto_optimum import df_pareto_optimum
from pdf_converter import generate_pdf

# Для работы с LLM-моделью
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import GigaChat
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.schema import HumanMessage, SystemMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders.csv_loader import CSVLoader

# Далее идет работа гига-чата на основе полученных результатов от пользователя
model_name = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embedding = HuggingFaceEmbeddings(model_name=model_name,
                                  model_kwargs=model_kwargs,
                                  encode_kwargs=encode_kwargs)

# Загрузка данных из Excel
df_source = pd.read_excel("Помещения и сооружения.xlsx")
df = pd.read_csv("Помещения и сооружения.csv")

questions_answers_list = []

# По умолчанию задаем координаты центра Москвы
location_center = geolocator.geocode("Москва")
goal_coords = [location_center.latitude, location_center.longitude]

from scenario2 import scenario2_measure
# что вас интересует (мера поддержки/инвестциионная площадка)
first_step = input()

# если пользователя интересует инвестиционная площадка
if first_step == "инвестиционная площадка":
    
    while True:
        if len(questions_answers_list) == 0:
            question = 'Преференциальный режим: '
            answer = input(question)
            questions_answers_list.append({question[:-2]:answer})
            if answer.lower() == 'да':
                df_result = df[df["Преференциальный режим"] != 'Отсутствует']
                break
    
        else:
            # Отбираем предыдущие вопрос и ответ
            question_prev = list(questions_answers_list[-1].keys())[0]
            answer_prev = list(questions_answers_list[-1].values())[0]
    
            if 'преференц' in question_prev.lower():
                question = 'Формат площадки: '
                df_result = df[df["Преференциальный режим"] == 'Отсутствует']
    
            elif 'формат площадки' in question_prev.lower():
                question = 'Тип площадки: '
                if answer_prev.lower() == 'земельный участок':
                    df_result = df_result[df_result["Формат площадки"] == 'Земельный участок']
                else:
                    df_result = df_result[df_result["Формат площадки"] != 'Земельный участок']
    
            elif 'тип площадки' in question_prev.lower():
                if "грин" in answer_prev.lower():
                    df_result = df_result[df_result["Тип площадки"] == 'Гринфилд']
                else:
                    df_result = df_result[df_result["Тип площадки"] == 'Браунфилд']
    
                question = "Форма сделки: "
    
            elif question_prev == "Форма сделки":
                df_result = df_result[df_result["Форма сделки"].str.lower() == answer_prev.lower()]
                if df_result.shape[0] < 5:
                    break
                else:
                    question = "Район: "
    
            elif question_prev == "Район":
                if df_result.shape[0] == 43:
                    min_area = df_result["Площадь"].str.replace(",",".").astype(float).min()
                    max_area = df_result["Площадь"].str.replace(",",".").astype(float).max()
                    question = f"Площадь (мин = {min_area}, макс = {max_area}). Введите в формате мин/макс: "
    
                    answer = input(question)
                    min_area_user = float(answer.split("/")[0])
                    max_area_user = float(answer.split("/")[1])
    
                    while min_area_user < min_area or max_area_user > max_area:
                        answer = input(question)
                        min_area_user = float(answer.split("/")[0])
                        max_area_user = float(answer.split("/")[1])
    
                    df_result = df_result[df_result["Площадь"].str.replace(",", ".").astype(float) >= min_area_user]
                    df_result = df_result[df_result["Площадь"].str.replace(",", ".").astype(float) <= max_area_user]
    
                    questions_answers_list.append({question[:-2]:answer})
                    break
                else:
                    min_cost = df_result["Стоимость объекта, руб. (покупки или месячной аренды)"].str.replace(",",".").astype(float).min()
                    max_cost = df_result["Стоимость объекта, руб. (покупки или месячной аренды)"].str.replace(",",".").astype(float).max()
                    question = f"Стоимость (мин = {min_cost}, макс = {max_cost}). Введите в формате мин/макс: "
                    answer = input(question)
                    min_cost_user = float(answer.split("/")[0])
                    max_cost_user = float(answer.split("/")[1])
                    while min_cost_user < min_cost or max_cost_user > max_cost:
                        answer = input(question)
                        min_cost_user = float(answer.split("/")[0])
                        max_cost_user = float(answer.split("/")[1])
    
                    df_result_check = df_result[df_result["Стоимость объекта, руб. (покупки или месячной аренды)"].str.replace(",", ".").astype(float) >= min_cost_user]
                    df_result_check = df_result[df_result["Стоимость объекта, руб. (покупки или месячной аренды)"].str.replace(",", ".").astype(float) <= max_cost_user]
                    if df_result_check.shape[0] == 0:
                        df_result = df_result[df_result["Стоимость объекта, руб. (покупки или месячной аренды)"].str.replace(",", ".").astype(float) <= max_cost_user]
    
            elif "Стоимость" in question_prev:
    
                min_area = df_result["Площадь"].str.replace(",", ".").astype(float).min()
                max_area = df_result["Площадь"].str.replace(",", ".").astype(float).max()
                question = f"Площадь (мин = {min_area}, макс = {max_area}). Введите в формате мин/макс: "
    
                answer = input(question)
                min_area_user = float(answer.split("/")[0])
                max_area_user = float(answer.split("/")[1])
    
                while min_area_user < min_area or max_area_user > max_area:
                    answer = input(question)
                    min_area_user = float(answer.split("/")[0])
                    max_area_user = float(answer.split("/")[1])
    
                df_result_check = df_result[df_result["Площадь"].str.replace(",", ".").astype(float) >= min_area_user]
                df_result_check = df_result[df_result["Площадь"].str.replace(",", ".").astype(float) <= max_area_user]
                if df_result_check.shape[0] == 0:
                    df_result = df_result[df_result["Площадь"].str.replace(",", ".").astype(float) >= min_area_user]
    
                questions_answers_list.append({question[:-2]:answer})
                break
    
            if df_result.shape[0] <= 5:
                break
    
            if "Стоимость" not in question and "Площадь" not in question:
                answer = input(question)
    
            if "Район" in question:
                location = geolocator.geocode(answer)
                goal_coords = [location.latitude, location.longitude]
    
            questions_answers_list.append({question[:-2]:answer})
    
    # Найдем парето-оптимальные значения для датафреймов размером больше 1
    if df_result.shape[0] > 5:
        df_source_ = df_pareto_optimum(df_result, df_source, questions_answers_list, goal_coords)
    else:
        df_source_ = df_source.loc[df_result.index][:]
        df_source_["is_pareto_optimum"] = 1
    
    
    # Сконвертируеем полученные результаты в виде pdf-файла
    name = 'Беда Даниил Андреевич'
    logo_path = 'logo_investmoscow.png'
    generate_pdf(df_source_.sort_values("is_pareto_optimum", ascending=False)
                 , name
                 , logo_path)
    
    print("Я сгенерировал для Вас наиболее подходящие варианты в PDF-документе. Могу ли помочь Вам чем-нибудь еще?")
    
    # Сохраняем полученные результаты в формате CSV
    df_source_.to_csv("Итоговый датафрейм.csv", index = False)
    loader = CSVLoader("Итоговый датафрейм.csv", encoding="utf-8")
    docs = loader.load()
    
    vector_store = FAISS.from_documents(docs, embedding=embedding)
    
    # Задаем параметры извлечения
    embedding_retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    
    # Задаем сам гигачат
    giga = GigaChat(credentials=auth,
                    model='GigaChat:latest',
                    verify_ssl_certs=False
                    )
    
    system_msg = '''Ты задаешь вопросы пользователя на основе данных, которые были загружены предварительно.
                    В первом полученном сообщении от пользователя будет содержаться ответ на вопрос
                    "Могу ли помочь Вам чем-нибудь еще?".
                 '''
    # Здесь будет история переписки
    msgs = [
        SystemMessage(content=system_msg)
    ]
    
    user_input = input()
    while user_input != "СТОП": # задаем стоп-слово
        if len(msgs) > 1:
            user_input = input("Пользователь: ")
        msgs.append(HumanMessage(content=user_input))
        answer = giga(msgs)
        print("Фрося:", answer.content)

# если пользователя интересують меры поддержки
elif first_step == "мера поддержки":
    df = pd.read_excel("Региональные_меры_поддержки_Москва.xlsx")
    scenario2_measure(df)

# иначе включается GiGaChat
else:
    loader = CSVLoader("ОЭЗ вопросы.csv", encoding="utf-8")
    docs = loader.load()
    
    vector_store = FAISS.from_documents(docs, embedding=embedding)
    
    # Задаем параметры извлечения
    embedding_retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    
    # Задаем сам гигачат
    giga = GigaChat(credentials=auth,
                    model='GigaChat:latest',
                    verify_ssl_certs=False
                    )
    
    system_msg = '''Ты задаешь вопросы пользователя на основе данных, которые были загружены предварительно'''
    # Здесь будет история переписки
    msgs = [
        SystemMessage(content=system_msg)
    ]
    
    user_input = input("Пользователь: ")
    while user_input != "СТОП": # задаем стоп-слово
        if len(msgs) > 1:
            user_input = input("Пользователь: ")
        msgs.append(HumanMessage(content=user_input))
        answer = giga(msgs)
        print("Фрося:", answer.content)