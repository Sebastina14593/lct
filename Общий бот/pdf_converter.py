from fpdf import FPDF # для формирования pdf-файла
import requests
from PIL import Image
from io import BytesIO
import os

# Функция для загрузки и сохранения изображения
def download_and_save_image(url, save_directory='.'):
    try:
        # Отправляем запрос на URL
        response = requests.get(url)
        response.raise_for_status()  # Проверяем, что запрос прошел успешно

        # Открываем изображение из полученных байтов
        image = Image.open(BytesIO(response.content))

        # Определяем имя файла
        filename = os.path.join(save_directory, f"{url.split('=')[-1]}.jpg")

        # Сохраняем изображение в формате JPG
        image = image.convert("RGB")  # Убедимся, что изображение в RGB формате
        image.save("images/" + filename, "JPEG")

        # print(f"Изображение сохранено: {filename}")
    except requests.RequestException as e:
        pass
        # print(f"Ошибка при загрузке изображения: {e}")
    except IOError as e:
        pass
        # print(f"Ошибка при сохранении изображения: {e}")

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", 'B', 10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf(df, name, logo_path):
    pdf = PDF()
    pdf.add_page()

    # Добавление шрифта DejaVuSansCondensed
    pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)

    # Логотип
    pdf.image(logo_path, 10, 8, 33)
    pdf.ln(10)

    # Заголовок
    pdf.set_font("DejaVu", '', 16)
    pdf.multi_cell(0, 10, f"Подбор инвестиционных площадок под ваш запрос, {name}", 0, 'C')
    pdf.ln(10)

    # Слог
    pdf.set_font("DejaVu", '', 10)
    pdf.multi_cell(0, 10, 'Выберите площадку вашей мечты! Предложения рекомендованные именно вам:', 0, 'C')

    # Разделительная черта
    pdf.set_line_width(0.5)
    pdf.line(10, 28, 200, 28)
    pdf.ln(10)

    # Список названий инвестиционных площадок
    pdf.set_font("DejaVu", '', 10)
    pdf.multi_cell(0, 10, 'Список инвестиционных площадок:', 0, 'L')

    for idx, row in df.iterrows():
        pdf.multi_cell(0, 10, f"{idx + 1}. {row['Название площадки']}", 0, 1)

     # Разделительная черта
    pdf.set_line_width(0.5)
    pdf.line(10, 28, 200, 28)
    pdf.ln(10)

    # Очищаем папку с изображениями
    if len(os.listdir("images")) > 0:
        images = os.listdir("images")
        for image in images:
            os.remove(f"images/{image}")

    # Подробная информация по каждой площадке
    for idx, row in df.iterrows():
        pdf.add_page()
        pdf.multi_cell(0, 10, f"{idx + 1}. {row['Название площадки']}")
        pdf.multi_cell(0, 10, f"Преференциальный режим: {row['Преференциальный режим']}")
        pdf.multi_cell(0, 10, f"Адрес объекта: {row['Адрес объекта']}")
        pdf.multi_cell(0, 10, f"Тип площадки: {row['Тип площадки']}")
        pdf.multi_cell(0, 10, f"Форма сделки: {row['Форма сделки']}")
        pdf.multi_cell(0, 10, f"Стоимость объекта, руб. (покупки или месячной аренды): {row['Стоимость объекта, руб. (покупки или месячной аренды)']}")
        pdf.multi_cell(0, 10, f"Характеристики расположенных объектов капитального строительства: {row['Характеристики расположенных объектов капитального строительства']}")
        pdf.multi_cell(0, 10, f"Площадь: {row['Площадь']}")
        pdf.ln(5)
        download_and_save_image(row['Фото'])

        try:
            pdf.ln(5)
            pdf.image("images/" + row['Название для фото'] + '.jpg', x=None, y=None, w=100)
            pdf.ln(10)
        except:
            pass
        # Разделительная черта между объектами
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)

    pdf.output("investment_sites.pdf")