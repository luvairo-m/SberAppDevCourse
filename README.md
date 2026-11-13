# SberAppDevCourse

Репозиторий для решения задач по курсу СБЕРА "Разработка приложений" (направление магистратуры - "Прикладной анализ данных")

## Пара 9. API автомастерской

API помогает сотрудникам автомастерской вести заказ-наряды и отслеживать ход ремонта.

## Как делали

1. В [`api.yaml`](api.yaml) описаны пять операций OpenAPI 3.0.3. Для списка задан фильтр по статусу, для отдельного заказ-наряда используется ID.
2. В `components` вынесены DTO запросов, ответов и ошибок. Сервер назначает ID при создании, а роль сотрудника определяется по токену и не попадает в DTO заказ-наряда.
3. Спецификация проверена OpenAPI Generator CLI 7.26.0. Тем же инструментом сгенерирован каркас Python Flask в [`service/`](service/).

   ```sh
   openapi-generator-cli validate -i api.yaml
   openapi-generator-cli generate -i api.yaml -g python-flask -o service --additional-properties useConnexion3=true --global-property apiTests=false
   ```

   CLI можно установить командой `python -m pip install openapi-generator-cli==7.26.0`. Для генератора нужен Java 11 или новее.

4. В сгенерированные контроллеры добавлены операции над заказ-нарядами и проверка демо-токенов. `.openapi-generator-ignore` сохраняет эти контроллеры при повторной генерации в `service/`. Данные хранятся в памяти процесса и сбрасываются при перезапуске.

## Запуск и проверка

Из корня репозитория, в окружении Python 3.12:

```sh
cd service
python -m pip install -r requirements.txt
python -m openapi_server
```

Интерфейс Swagger UI доступен на [localhost:8080/ui/](http://localhost:8080/ui/). В Swagger UI нажмите **Authorize**. В Postman выберите **Import**, загрузите `api.yaml` и создайте коллекцию из OpenAPI. В разделе **Authorization** коллекции выберите **Bearer Token**. Для записи используйте `demo-editor`, для чтения достаточно `demo-reader`.

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

Подставьте `id` из ответа в `GET`, `PUT` и `DELETE`. Запрос без токена вернёт `401`, попытка записи с `demo-reader` вернёт `403`, а чтение удалённого заказ-наряда вернёт `404`.
