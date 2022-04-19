import sys
import requests

url = "http://static-maps.yandex.ru/1.x"
params = {
    "ll": '55.673317,37.463594',
    "spn": "0.003,0.003",
    "l": "map"
}
response = requests.get(url, params=params)

if not response:
    print("Ошибка выполнения запроса:")
    print("Http статус:", response.status_code, "(", response.reason, ")")
    sys.exit(1)

# Запишем полученное изображение в файл.
map_file = "map.png"
with open(map_file, "wb") as file:
    file.write(response.content)
print(map_file)
# Инициализируем pygame
