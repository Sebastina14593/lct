AUTH = os.getenv('AUTH')

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

prompt = ChatPromptTemplate.from_template('''Ответь на вопрос пользователя. Используй при этом только информацию из контекста. Если в контексте нет информации для ответа, сообщи об этом пользователю. Контекст: {context} Вопрос: {input} Ответ:''')

document_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
retrieval_chain = create_retrieval_chain(embedding_retriever, document_chain)