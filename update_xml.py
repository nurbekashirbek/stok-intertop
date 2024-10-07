import pandas as pd
from lxml import etree
import os

def find_file_with_word(word, extension):
    """Находит первый файл в текущем каталоге, содержащий указанное слово и имеющий указанный расширение."""
    for file in os.listdir('.'):
        if word in file and file.endswith(extension):
            return file
    return None

def update_xml(stock_file, price_file, xml_file):
    stock_data = pd.read_excel(stock_file)
    price_data = pd.read_excel(price_file)

    tree = etree.parse(xml_file)
    root = tree.getroot()

    for offer in root.findall('.//offer'):
        barcode = offer.find('barcode').text
        stock_info = stock_data[stock_data['EAN/UPC'] == barcode]
        if not stock_info.empty:
            quantity = int(stock_info['Stock'].values[0])
            offer.find('quantity').text = str(quantity)
        else:
            offer.find('quantity').text = '0' 

        article = offer.find('article').text
        price_info = price_data[price_data['Generik'] == article]
        if not price_info.empty:
            base_price = int(price_info['Price'].values[0])
            discount_price = int(price_info['Discount Price'].values[0])
            offer.find('base_price').text = str(base_price)
            offer.find('discount_price').text = str(discount_price)

    tree.write(xml_file, encoding="UTF-8", xml_declaration=True)

stock_file = find_file_with_word('2024', '.xlsx')
price_file = 'цены.xlsm'
xml_file = 'intertop.xml'

if stock_file and os.path.exists(price_file) and os.path.exists(xml_file):
    update_xml(stock_file, price_file, xml_file)
else:
    print("Не все необходимые файлы найдены.")
