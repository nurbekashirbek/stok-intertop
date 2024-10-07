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
    # Загрузка данных из файла запасов
    try:
        stock_data = pd.read_excel(stock_file)
    except Exception as e:
        print(f"Ошибка при загрузке файла запасов: {e}")
        return

    # Проверка структуры файла запасов
    if 'EAN/UPC' not in stock_data.columns or 'Stock' not in stock_data.columns:
        print("Файл с запасами не содержит нужных колонок.")
        return
    
    # Загрузка данных из файла цен, если он существует
    price_data = None
    if price_file and os.path.exists(price_file):
        try:
            price_data = pd.read_excel(price_file)
            # Проверка структуры файла цен
            if 'Generik' not in price_data.columns or 'Price' not in price_data.columns or 'Discount Price' not in price_data.columns:
                print("Ошибка: Файл с ценами не содержит нужных колонок.")
                return
        except Exception as e:
            print(f"Ошибка при загрузке файла цен: {e}")
    else:
        print("Файл с ценами не найден. Обновление цен пропущено.")

    # Парсинг XML файла
    try:
        tree = etree.parse(xml_file)
        root = tree.getroot()
    except Exception as e:
        print(f"Ошибка при парсинге XML файла: {e}")
        return

    # Множество для уникальных артикулов
    updated_articles = set()

    # Обновление данных в XML
    for offer in root.findall('.//offer'):
        # Обновление количества
        barcode = str(offer.find('barcode').text).strip()
        stock_info = stock_data[stock_data['EAN/UPC'].astype(str).str.strip() == barcode]
        
        if not stock_info.empty:
            quantity = int(stock_info['Stock'].values[0])
            offer.find('quantity').text = str(quantity)
        else:
            offer.find('quantity').text = '0' 

        # Обновление цен, если файл цен существует и имеет правильную структуру
        if price_data is not None:
            article = str(offer.find('article').text).strip()
            price_info = price_data[price_data['Generik'].astype(str).str.strip() == article]
            
            if not price_info.empty:
                base_price = int(price_info['Price'].values[0])
                discount_price = int(price_info['Discount Price'].values[0])
                offer.find
