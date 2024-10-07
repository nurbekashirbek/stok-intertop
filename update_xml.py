import pandas as pd
from lxml import etree
import os

def find_file_with_word(word, extension):
    """Находит первый файл в текущем каталоге, содержащий указанное слово и имеющий указанное расширение (без учета регистра)."""
    for file in os.listdir('.'):
        if word in file and file.lower().endswith(extension.lower()):
            return file
    return None

def update_xml(stock_file, price_file, xml_file):
    # Загрузка данных из файлов
    try:
        stock_data = pd.read_excel(stock_file)
        price_data = pd.read_excel(price_file)
    except Exception as e:
        print(f"Ошибка при загрузке Excel файлов: {e}")
        return

    # Проверка, что нужные колонки существуют
    if 'EAN/UPC' not in stock_data.columns or 'Stock' not in stock_data.columns:
        print("Файл с запасами не содержит нужных колонок.")
        return
    
    print("Названия колонок в файле цен:", price_data.columns)

    if 'Generik' not in price_data.columns or 'Price' not in price_data.columns or 'Discount Price' not in price_data.columns:
        print("Файл с ценами не содержит нужных колонок.")
        return

    # Парсинг XML файла
    try:
        tree = etree.parse(xml_file)
        root = tree.getroot()
    except Exception as e:
        print(f"Ошибка при парсинге XML файла: {e}")
        return

    # Счетчики для обновлений
    updated_price_count = 0

    # Обновление данных в XML
    for offer in root.findall('.//offer'):
        barcode = str(offer.find('barcode').text).strip()
        stock_info = stock_data[stock_data['EAN/UPC'].astype(str).str.strip() == barcode]
        
        if not stock_info.empty:
            quantity = int(stock_info['Stock'].values[0])
            offer.find('quantity').text = str(quantity)
        else:
            offer.find('quantity').text = '0' 

        # Обновление цены
        article = offer.find('article').text
        price_info = price_data[price_data['Generik'] == article]
        if not price_info.empty:
            base_price = int(price_info['Price'].values[0])
            discount_price = int(price_info['Discount Price'].values[0])
            offer.find('base_price').text = str(base_price)
            offer.find('discount_price').text = str(discount_price)
            updated_price_count += 1
            print(f"Цены обновлены для артикула {article}: базовая цена = {base_price}, акционная цена = {discount_price}")

    # Сохранение обновленного XML файла
    try:
        tree.write(xml_file, encoding="UTF-8", xml_declaration=True)
        print("Файл XML успешно обновлен.")
        print(f"Обновлено цен для {updated_price_count} товаров.")
    except Exception as e:
        print(f"Ошибка при сохранении XML файла: {e}")

# Отладка для отображения всех файлов
print("Доступные файлы:", os.listdir('.'))

# Определение нужных файлов
stock_file = find_file_with_word('2024', '.xlsx')
price_file = 'цены.xlsm'
xml_file = 'intertop.xml'

# Отладочные сообщения для проверки
print(f"Файл запасов: {stock_file}")
print(f"Файл цен: {price_file}")
print(f"XML файл: {xml_file}")

# Запуск обновления XML, если все файлы найдены
if stock_file and os.path.exists(price_file) and os.path.exists(xml_file):
    update_xml(stock_file, price_file, xml_file)
else:
    print("Не все необходимые файлы найдены.")
