import json
import requests

group_name = 'PY-148'
url = 'https://cataas.com/cat'
params = {}

text_for_image = input('Введите текст для картинки:')
print(f'введенный текст:{text_for_image}')
yd_token = input('Введите токен с Полигона Яндекс.Диска:')
print(f'введенный токен:{yd_token}')

headers = {
    "User-Agent": "Mozilla/5.0"
}

try:
    #  timeout, чтобы код не вис
    print("Связываюсь с сервером...")
    response = requests.get(f'https://cataas.com/cat/says/{text_for_image}',
                            timeout=(5, 30))

    # Проверяем, что сервер вообще ответил успешно
    response.raise_for_status()

    file_size = len(response.content)
    print(f'Картинка получена! Размер: {file_size} байт')

except requests.exceptions.ConnectTimeout:
    print("Ошибка: Сервер слишком долго не отвечает (Timeout).")
    exit()
except requests.exceptions.ConnectionError:
    print("Ошибка: Не удалось подключиться к серверу. Проверьте его доступность")
    exit()
except Exception as e:
    print(f"Произошла другая ошибка: {e}")
    exit()
# response = requests.get(f'{url}{text_for_image}')

json_report = [
    {
        "file_name": f'{text_for_image}.jpg',
        "size": file_size
    }
]

with open(f'{text_for_image}.json', 'w', encoding='utf-8') as f:
    json.dump(json_report, f, ensure_ascii=False, indent=4)

headers = {'Authorization': f'OAuth {yd_token}'}
base_yd_url = 'https://cloud-api.yandex.net/v1/disk'
requests.put(f'{base_yd_url}/resources?path={group_name}', headers=headers)

target_path = f"{group_name}/{text_for_image}.jpg"
upload_url_get = f'{base_yd_url}/resources/upload?path={target_path}&overwrite=true'
res = requests.get(upload_url_get, headers=headers)

if res.status_code == 200:
    upload_url = res.json().get('href')

    # В. Загружаем файл на Яндекс.Диск по полученной ссылке
    print("Загружаем саму картинку на Яндекс.Диск...")
    put_response = requests.put(upload_url, data=response.content)

    if put_response.status_code in (200, 201, 202):
        print("🎉 Файл успешно загружен на Яндекс.Диск!Запишем и JSON!")
        # запишем и json
        json_path = f"{group_name}/{text_for_image}.json"

        res_json = requests.get(f'{base_yd_url}/resources/upload',
                                headers=headers,
                                params={'path': json_path, 'overwrite': 'true'})

        res_json.raise_for_status()
        json_upload_url = res_json.json()['href']

        with open(f'{text_for_image}.json', 'rb') as f:
            put_json = requests.put(json_upload_url, data=f)

        if put_json.status_code in (200, 201, 202):
            print("JSON файл успешно загружен на Яндекс.Диск")
        else:
            print("Ошибка загрузки JSON:", put_json.status_code)


    else:
        print(f"Ошибка при отправке файла: {put_response.status_code}")
else:
    print(f"Не удалось получить ссылку для загрузки: {res.status_code}")
    print(res.json().get('message'))
