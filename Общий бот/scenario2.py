def scenario2_measure(df):
    
    question_new = ''
    answer_options = []
    diction = {
        'start':0, # если 1, то Задали вопрос про МСП
        'second':0, # если 1, то получили ответ про МСП и задали вопрос про ОКВЭД
        'third':0, # если 1, то получили и отфильтровали БД по ОКВЭДу, и задали вопрос про виды поддержки
        'fourth':0, # если 1, то получил ответ по виду поддержки, и задал вопрос про подвид поддержки
        'fifth':0, # если 1, то получил ответ про подвид поддержки, и выдал пользователю перечень мер поддержек
        'final':0 # если 1, то выдал пользователю перечень мер поддержек'
    }
    
    def zapusk_poddershki(request_user, df2, flag_start, flag_second, flag_third, flag_fourth, flag_fifth, flag_final, ishodniy_df):
      if request_user == 'Старт' or request_user == 'старт' or request_user == 'Вернуться в начало':
        new_df = ishodniy_df
        if diction['start']==0:
          question_new = "Добрый день, меня зовут Фрося. Я умный помощник инвестиционного портала города Москвы. Что вас интересует?"
          answer_options = ['Подобрать меру поддержки для бизнеса', 'Подобрать инвестиционную площадку']
        else:
          question_new = "Какой вопрос вас интересует?"
          answer_options = ['Подобрать меру поддержки для бизнеса', 'Подобрать инвестиционную площадку']
        diction['start'] = 0; diction['second'] = 0; diction['third'] = 0; diction['fourth'] = 0; diction['fifth'] = 0; diction['final'] = 0
        return question_new, answer_options, new_df
    
      if flag_start==0 and request_user=='Подобрать меру поддержки для бизнеса':
        question_new = """Я могу подобрать для вашего бизнеса меру поддержки. Подскажите, подходит ли ваш бизнес под требования малого и среднего предпринимательства (МСП)? """
        answer_options = ["Да","Нет","Узнать подробнее о критериях"]
        diction['start'] = 1
        return question_new, answer_options, df2
      if flag_second==0 and flag_start==1 and request_user=='Да':
        question_new = """Укажите вид экономической деятельности вашего бизнеса, под который вы хотите подобрать меру поддержки?"""
        answer_options = []
        diction['second'] = 1
        return question_new, answer_options, df2
      if flag_second==0 and flag_start==1 and request_user=='Нет':
        question_new = """Укажите вид экономической деятельности вашего бизнеса, под который вы хотите подобрать меру поддержки?"""
        answer_options = []
        diction['second'] = 1
        new_df = df2[df2["Требуется вхождение в реестр МСП"]=="Нет"]
        return question_new, answer_options, new_df
      if flag_second==0 and flag_start==1 and request_user=='Узнать подробнее о критериях':
        question_new = """Законодательно установлено понятие малого и среднего предпринимательства, к которому в соответствии со статьей 4 Федерального закона от 24.07.2007 № 209-ФЗ «О развитии малого и среднего предпринимательства в Российской Федерации» относятся:
                    1) Зарегистрированные в установленном порядке граждане (в качестве индивидуальных предпринимателей (ИП) или в качестве глав крестьянских (фермерских) хозяйств (КФХ);
                    2) Зарегистрированные в установленном порядке потребительские кооперативы и коммерческие организации (кроме государственных и муниципальных унитарных предприятий).
                    Более подробную информацию о критериях вы можете получить по ссылке: https://investmoscow.ru/business/sme-support
                    Подскажите, подходит ли ваш бизнес под требования малого и среднего предпринимательства (МСП)?"""
        answer_options = ["Да", "Нет", "Узнать подробнее о критериях"]
        return question_new, answer_options, df2
      if flag_second==1 and flag_start ==1 and flag_third == 0 and request_user.isdigit(): # заход в оквэд
        new_df = df2[df2['ОКВЭД'].apply(lambda x: any(code.strip().startswith(request_user + ' -') for code in x.split(';')))]
        if len(new_df)==0:
          question_new = "По вашему ОКВЭД-у не найдено ни одной подходящей меры поддержки"
          answer_options = ["Вернуться в начало"]
          return question_new, answer_options, new_df
        elif len(new_df)<=5:
          question_new = f"""Вам было представлено {len(new_df)} мер(ы) поддержки.
          Вы можете перейти на конкретную и ознакомиться с ней"""
          answer_options = new_df['Наименование меры поддержки'].unique().tolist()
          diction['final'] = 1
          return question_new, answer_options, new_df
        else:
          question_new = "Какой вид поддержки вас интересует?"
          answer_options = new_df['Вид поддержки'].unique().tolist()
          diction['third'] = 1
          return question_new, answer_options, new_df
    
      if flag_start == 1 and flag_second == 1 and flag_third ==1 and flag_fourth ==0 and request_user == 'прочие нефинансовые меры поддержки':
        new_df = df2[df2['Вид поддержки']=='прочие нефинансовые меры поддержки']
        if len(new_df)<=5:
          question_new = f"""Вам было представлено {len(new_df)} мер(ы) поддержки.
          Вы можете перейти на конкретную и ознакомиться с ней"""
          answer_options = new_df['Наименование меры поддержки'].unique().tolist()
          diction['final'] = 1
          return question_new, answer_options, new_df
        else:
          question_new = "Выберите подвид нефинансовой поддержки, которая вас интересует:"
          answer_options = df2[df2['Вид поддержки']=='прочие нефинансовые меры поддержки']['Подвид поддержки'].unique().tolist()
          diction['fourth'] = 1
          return question_new, answer_options, new_df
    
      if flag_start == 1 and flag_second == 1 and flag_third ==1 and flag_fourth ==0 and request_user in df2['Вид поддержки'].unique().tolist() and request_user != 'прочие нефинансовые меры поддержки':
        new_df = df2[df2["Вид поддержки"]==request_user]
        question_new = f"""Вам было представлено {len(new_df)} мер(ы) поддержки.
        Вы можете перейти на конкретную и ознакомиться с ней"""
        answer_options = new_df['Наименование меры поддержки'].unique().tolist()
        diction['fourth'] = 1
        diction['final'] = 1
        return question_new, answer_options, new_df
    
      if flag_start == 1 and flag_second == 1 and flag_third ==1 and flag_fourth ==1 and request_user in df2['Подвид поддержки'].unique().tolist():
        new_df = df2[df2['Подвид поддержки']==request_user]
        question_new = f"""Вы выбрали подвид {request_user}
                  Вам было представлено {len(new_df)} мер(ы) поддержки.
                  Вы можете перейти на конкретную и ознакомиться с ней.
          """
        answer_options = new_df['Наименование меры поддержки'].unique().tolist()
        diction['final'] = 1
        return question_new, answer_options, new_df
    
      if flag_final == 1 and request_user in df2['Наименование меры поддержки'].tolist():
        new_df = df2[df2['Наименование меры поддержки']==request_user]
        name_podderzh = request_user
        mechanism = new_df['Суть механизма'].tolist()[0]
        question_new = f"""Сейчас я вам расскажу подробнее о поддержке '{request_user}'
                {mechanism}.
                Возможно вы хотите узнать что-то подробнее?"""
        answer_options = ['Ограничения по видам деятельности', 'Требования к заявителю', 'Необходимые документы', 'Подать заявку на рассмотрение', 'Процедура подачи заявки','Вернуться в начало']
        return question_new, answer_options, new_df
    
      if flag_final == 1 and request_user == 'Ограничения по видам деятельности':
        new_df = df2
        info_po_ogranicheniyam = df2['Ограничения по видам деятельности'].tolist()[0]
        question_new =  f"""{info_po_ogranicheniyam}
                    Интересует ли вас другая информация по данной мере поддержки?"""
        answer_options = ['Требования к заявителю', 'Необходимые документы', 'Подать заявку на рассмотрение', 'Процедура подачи заявки','Вернуться в начало']
        return question_new, answer_options, new_df
    
      if flag_final == 1 and request_user == 'Требования к заявителю':
        new_df = df2
        info_treb_zayav = df2['Требования к заявителю'].tolist()[0]
        question_new = f"""{info_treb_zayav}
                    Интересует ли вас другая информация по данной мере поддержки?"""
        answer_options = ['Ограничения по видам деятельности', 'Необходимые документы', 'Подать заявку на рассмотрение', 'Процедура подачи заявки','Вернуться в начало']
        return question_new, answer_options, new_df
    
      if flag_final == 1 and request_user == 'Необходимые документы':
        new_df = df2
        info_neobh_docs = df2['Необходимые документы'].tolist()[0]
        question_new = f"""{info_neobh_docs}
                    Интересует ли вас другая информация по данной мере поддержки?"""
        answer_options = ['Ограничения по видам деятельности', 'Требования к заявителю', 'Подать заявку на рассмотрение', 'Процедура подачи заявки', 'Вернуться в начало']
        return question_new, answer_options, new_df
    
      if flag_final == 1 and request_user == 'Подать заявку на рассмотрение':
        new_df = df2
        info_link = df2['Подать заявку на рассмотрение'].tolist()[0]
        question_new = f"""{info_link}
                    Интересует ли вас другая информация по данной мере поддержки?"""
        answer_options = ['Ограничения по видам деятельности', 'Требования к заявителю', 'Необходимые документы', 'Процедура подачи заявки','Вернуться в начало']
        return question_new, answer_options, new_df
    
      if flag_final == 1 and request_user == 'Процедура подачи заявки':
        new_df = df2
        info_procedure_zayav = df2['Процедура подачи заявки'].tolist()[0]
        question_new = f"""{info_procedure_zayav}
                    Интересует ли вас другая информация по данной мере поддержки?"""
        answer_options =  ['Ограничения по видам деятельности', 'Требования к заявителю', 'Необходимые документы', 'Подать заявку на рассмотрение','Вернуться в начало']
        return question_new, answer_options, new_df
    
      if request_user == 'выйти' or request_user == 'Выйти':
        new_df = df2
        question_new = 'Хорошего дня. Ждем вас снова!'
        answer_options = []
        return question_new, answer_options, new_df

    df2 = df.copy()
    df3 = df2.copy()
    df4 = df2.copy()
    diction = {
        'start':0, # если 1, то Задали вопрос про МСП
        'second':0, # если 1, то получили ответ про МСП и задали вопрос про ОКВЭД
        'third':0, # если 1, то получили и отфильтровали БД по ОКВЭДу, и задали вопрос про виды поддержки
        'fourth':0, # если 1, то получил ответ по виду поддержки, и задал вопрос про подвид поддержки
        'fifth':0, # если 1, то получил ответ про подвид поддержки, и выдал пользователю перечень мер поддержек
        'final':0 # если 1, то выдал пользователю перечень мер поддержек'
    }
    # Подобрать меру поддержки для бизнеса
    i=0
    for i in range(20):
        request_user = input("Ваш запрос в бот: ")
        question, ans, df3 = zapusk_poddershki(request_user, df3, diction['start'], diction['second'], diction['third'], diction['fourth'], diction['fifth'], diction['final'], df4)
        print(question)
        print("Варианты ответов:")
        print(ans)
        i = i + 1