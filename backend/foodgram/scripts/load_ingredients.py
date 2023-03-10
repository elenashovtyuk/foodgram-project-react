
# импортируем модуль csv - модуль Python для чтения и записи файлов
import csv


# этот файл-скрипт должен реализовывать функцию run
# это то, что запускается при запуске скрипта
def run():
    # открываем наш файл со списком ингредиентов как file.
    # Для этого передаем переменную file в csv.reader
    # метод reader модуля csv используется для извлечения данных
    # в объект reader
    with open('recipes/ingredients.csv') as file:
        reader = csv.reader(file)
        # next(reader)  # Advance past the header

        # затем перебираем объект reader и извлекаем каждую строку наших данных
        for row in reader:
            print(row)
