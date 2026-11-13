# SberAppDevCourse

Репозиторий для решения задач по курсу СБЕРА "Разработка приложений" (направление магистратуры - "Прикладной анализ данных")

## Пара 9. API автомастерской

API помогает сотрудникам автомастерской вести заказ-наряды и отслеживать ход ремонта.

## Как делали

Сначала в [`api.yaml`](api.yaml) описаны список заказ-нарядов и операции с одним заказом. Список можно отфильтровать по статусу. Поля запроса и ответа вынесены в DTO в разделе `components`. Сервер сам выдаёт ID и возвращает адрес заказа в поле `href`.

Затем `api.yaml` проверен через OpenAPI Generator CLI 7.26.0. Из него сгенерирован Flask-сервис в папке [`service/`](service/).

```sh
openapi-generator-cli validate -i api.yaml
openapi-generator-cli generate -i api.yaml -g python-flask -o service --additional-properties useConnexion3=true --global-property apiTests=false
```

Для генерации нужны Java 11 или новее и CLI (`python -m pip install openapi-generator-cli==7.26.0`).

В каркасе дописаны обработчики и проверка демо-токенов. Заказы лежат в памяти и пропадают при перезапуске. Файл `.openapi-generator-ignore` сохраняет дописанный код при повторной генерации.

## Запуск и проверка

Для запуска на Python 3.12 выполните из корня репозитория следующие команды.

```sh
cd service
python -m pip install -r requirements.txt
python -m openapi_server
```

В Swagger UI нажмите **Authorize** и введите `demo-editor` для чтения и записи или `demo-reader` для чтения. [Открыть Swagger UI](http://localhost:8080/ui/).

В Postman нажмите **Import** и выберите `api.yaml`, чтобы создать коллекцию. В настройках авторизации коллекции выберите **Bearer Token** и введите один из демо-токенов.

| Метод и путь | Что делает |
| --- | --- |
| `GET /work-orders?status=scheduled` | Показывает запланированные работы. Без `status` возвращает весь список. |
| `GET /work-orders/{order_id}` | Показывает заказ-наряд по ID. |
| `POST /work-orders` | Создаёт заказ-наряд и возвращает его с ID. |
| `PUT /work-orders/{order_id}` | Заменяет госномер, описание работ и статус. |
| `DELETE /work-orders/{order_id}` | Удаляет заказ-наряд и возвращает подтверждение. |

Отправьте `POST /work-orders` с токеном `demo-editor` и телом `application/json`.

```json
{
  "vehiclePlate": "А123ВС196",
  "workDescription": "Замена масла и фильтра",
  "status": "scheduled"
}
```

Возьмите адрес из `href` и попробуйте прочитать, заменить и удалить заказ. Запрос без токена вернёт `401`, запись с `demo-reader` вернёт `403`, а чтение удалённого заказа вернёт `404`.
