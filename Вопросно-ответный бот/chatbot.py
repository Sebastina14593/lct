auth = os.getenv('AUTH')

llm = GigaChat(credentials=AUTH, model='GigaChat', verify_ssl_certs=False, profanity_check=False)

loader = CSVLoader("ОЭЗ вопросы.csv", encoding='utf-8')
docs = loader.load()

model_name = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embedding = HuggingFaceEmbeddings(model_name=model_name,
model_kwargs=model_kwargs,
encode_kwargs=encode_kwargs)
vector_store = FAISS.from_documents(docs, embedding=embedding)

# Задаем параметры извлечения
embedding_retriever = vector_store.as_retriever(search_kwargs={"k": 5})

# Задаем сам гигачат
giga = GigaChat(credentials=auth,
                model='GigaChat:latest',
                verify_ssl_certs=False
                )

system_msg = '''Ты задаешь вопросы пользователя на основе данных, которые были загружены предварительно.'''
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