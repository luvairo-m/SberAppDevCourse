# SberAppDevCourse

Задания по курсу Сбера «Разработка приложений» для магистратуры «Прикладной анализ данных».

## Пара 9. API автомастерской

API помогает сотрудникам автомастерской вести заказ-наряды и отслеживать ход ремонта. Например, можно записать машину на замену масла, отметить, что работа началась, а потом найти заказ среди завершённых.

### Что лежит в репозитории

- [`api.yaml`](api.yaml) — спецификация OpenAPI 3.0.3 с маршрутами, DTO и ответами на ошибки.
- [`service/`](service/) — сгенерированный каркас Flask и дописанные обработчики.
- [`postman_collection.json`](postman_collection.json) — коллекция из пяти запросов, экспортированная из Postman после импорта `api.yaml`.

### Как делал

Сначала описал маршруты `/work-orders` для списка и создания заказов и `/work-orders/{order_id}` для работы с конкретным заказом. Форматы запросов и ответов вынес в `components`. При создании достаточно передать госномер, описание работ и статус. ID назначает сервер, а в `href` возвращается адрес заказа.

Затем проверил спецификацию и сгенерировал Flask-каркас. Для этих команд нужны Java 11 или новее и OpenAPI Generator CLI 7.26.0. Выполняйте их из корня репозитория.

```powershell
python -m pip install openapi-generator-cli==7.26.0
openapi-generator-cli validate -i api.yaml
openapi-generator-cli generate -i api.yaml -g python-flask -o service --additional-properties useConnexion3=true --global-property apiTests=false
```

В каркасе дописал обработчики и проверку демо-токенов. Заказы храню в памяти, поэтому при перезапуске список очищается. При повторной генерации дописанные файлы сохраняются благодаря [`service/.openapi-generator-ignore`](service/.openapi-generator-ignore).

### Как запустить

Из корня репозитория выполните команды в PowerShell. Сервис проверен на Python 3.12.

```powershell
cd service
python -m pip install -r requirements.txt
python -m openapi_server
```

Сервис запустится на `http://localhost:8080`. В Swagger UI нажмите **Authorize** и введите `demo-editor` для чтения и записи или `demo-reader` для чтения. [Открыть Swagger UI](http://localhost:8080/ui/)

### Какие запросы есть

| Метод и путь | Что делает |
| --- | --- |
| `GET /work-orders` | Возвращает список. Параметр `status` позволяет отфильтровать заказы. |
| `GET /work-orders/{order_id}` | Показывает заказ-наряд по ID. |
| `POST /work-orders` | Создаёт заказ-наряд и возвращает его с ID. |
| `PUT /work-orders/{order_id}` | Заменяет госномер, описание работ и статус. |
| `DELETE /work-orders/{order_id}` | Удаляет заказ-наряд и возвращает подтверждение. |

Все пять операций возвращают `200 OK` при успехе, как указано в задании. Статус `scheduled` означает, что работа запланирована, `in_progress` — что она началась, `completed` — что она завершена.

### Как проверить в Postman

1. Нажмите **Import** и выберите [`postman_collection.json`](postman_collection.json). Чтобы получить коллекцию из спецификации, импортируйте [`api.yaml`](api.yaml) и выберите **Postman Collection**. Для импорта запускать сервис не нужно.
2. Запустите сервис. В коллекции проверьте, что `baseUrl` равен `http://localhost:8080`. В разделе **Authorization → Bearer Token** укажите `demo-editor`.
3. Откройте `POST /work-orders`. В **Body → raw → JSON** вставьте пример и нажмите **Send**.

   ```json
   {
     "vehiclePlate": "А123ВС196",
     "workDescription": "Замена масла и фильтра",
     "status": "scheduled"
   }
   ```

4. Возьмите `id` из ответа. Для `GET`, `PUT` и `DELETE` одного заказа укажите этот ID в **Params → Path Variables → order_id**. Прочитайте заказ через `GET`, затем отправьте `PUT` с теми же полями и статусом `completed`. В запросе списка установите `status=completed` и убедитесь, что заказ появился в выдаче.
5. Удалите заказ через `DELETE` и снова запросите его по ID. Теперь сервер вернёт `404 Not Found`.

Для проверки доступа отправьте `GET /work-orders` без токена и получите `401 Unauthorized`. Затем попробуйте отправить корректный `POST` с токеном `demo-reader`. Сервер распознает сотрудника и вернёт `403 Forbidden`, потому что этому сотруднику доступно только чтение.
