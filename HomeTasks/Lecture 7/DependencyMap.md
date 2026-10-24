# Карта зависимостей StPlatform и PetClinic

## StPlatform — сценарий «сдать домашку»

Для разбора я взял репозиторий [UnMatty/StPlatform](https://gitverse.ru/UnMatty/StPlatform), commit [`7bd1066`](https://gitverse.ru/UnMatty/StPlatform/commit/7bd10669913fbef8f8c6e7331c25420489edd8ba).

### Какие слои я нашёл

В проекте нет отдельных папок с названиями `controller`, `service` и `repository`, но классы этих слоёв есть и отмечены аннотациями Spring.

**Контроллеры веб-страниц:**

- `AssignmentPageController` — страница задания, сдача и проверка работы;
- `CabinetController` — кабинет студента или преподавателя;
- `AttachmentController` — скачивание приложенного файла;
- `ActivateController`, `LoginController`, `PasswordResetController` — вход, активация и восстановление пароля;
- `TeacherAssignmentController`, `TeacherImportController`, `TeacherStudentController` — действия преподавателя;
- `ConsentPageController` — страницы согласий.

**REST-контроллеры:** `ApiAuthController`, `ApiAssignmentController`, `ApiSubmissionController`.

**Сервисы:** `ActivationService`, `AssignmentService`, `ConsentService`, `PasswordResetService`, `PlatformUserDetailsService`, `StudentRemovalService`, `SubmissionService`, `UserService`.

**Репозитории:** `AssignmentRepository`, `ConsentRecordRepository`, `SubmissionAttachmentRepository`, `SubmissionRepository`, `UserRepository`. Все они наследуются от `JpaRepository`, поэтому реализацию базовых методов вроде `findById` и `save` создаёт Spring Data JPA.

**Модель:** основные сущности — `Assignment`, `ConsentRecord`, `Submission`, `SubmissionAttachment`, `User`.

Ещё есть инфраструктурные компоненты: `AttachmentStorage` записывает файлы на диск, `InviteMailer` и `PasswordResetMailer` отправляют письма, а `LinkValidator` проверяет ссылки на GitVerse и GitHub.

### Как проходит сдача домашней работы

Я рассматривал успешную отправку веб-формы `POST /assignments/{id}/submit`. Главная цепочка выглядит так:

```text
AssignmentPageController.java.submitWork
  → UserService.java.byId
    → UserService.java.findById
      → UserRepository.java.findById
  → AssignmentPageController.java.splitLinks
  → SubmissionService.java.submit
    → AssignmentRepository.java.findById
    → SubmissionService.java.ensureNotAlreadySent
      → SubmissionRepository.java.findFirstByStudentIdAndAssignmentIdOrderByCreatedAtDesc
    → SubmissionService.java.normalizedLinks
    → SubmissionService.java.normalizedComment
    → LinkValidator.java.isValid
    → SubmissionRepository.java.save
```

Сначала `AssignmentPageController.submitWork` получает из Spring Security id вошедшего пользователя. Через `UserService` и `UserRepository` загружается сущность `User`. После этого контроллер делит многострочное поле со ссылками на список и вызывает `SubmissionService.submit`.

Внутри `SubmissionService.submit` последовательно проверяется:

1. Пользователь действительно имеет роль `STUDENT`.
2. Задание существует и опубликовано.
3. Предыдущая работа не находится в статусе `UNCHECKED` или `ACCEPTED`. Повторно отправить работу можно после `NEEDS_REWORK`.
4. Дедлайн не прошёл. Для доработки после `NEEDS_REWORK` сделано исключение.
5. Заполнено хотя бы одно поле: ссылка, комментарий или файл.
6. Каждая ссылка использует `https` и ведёт на разрешённый GitVerse или GitHub.
7. Не превышены ограничения на количество и длину ссылок и комментария.

Только после этих проверок создаётся `Submission`, а `SubmissionRepository.save` сохраняет его в базе. Если прикреплён файл, появляется ещё одна ветка:

```text
SubmissionService.java.submit
  → AttachmentStorage.java.store
    → Files.createDirectories
    → Files.copy
  → SubmissionAttachmentRepository.java.save
```

То есть содержимое файла лежит на диске под случайным UUID-именем, а в базе хранится сущность `SubmissionAttachment` с метаданными и ссылкой на сдачу. После успешного сохранения контроллер кладёт сообщение «Работа принята на проверку» во flash-атрибут и делает redirect обратно на `/assignments/{id}`.

У REST API начало немного другое:

```text
ApiSubmissionController.java.submit
  → UserService.java.byId
  → SubmissionService.java.submit
  → те же проверки и SubmissionRepository.java.save
```

Получается, что веб-страница и REST API используют одну бизнес-логику, а не дублируют правила сдачи.

### Все ли стрелки идут вниз

Основная цепочка действительно идёт вниз: **контроллер → сервис → репозиторий или файловое хранилище**. Обратно сущности и репозитории контроллеры не вызывают, поэтому явной циклической зависимости в этом сценарии я не увидел.

Но граница между web-слоем и сервисом немного размыта. Метод `SubmissionService.submit` принимает `MultipartFile`, а это тип из Spring Web. Получается, что сервис знает, каким способом файл пришёл из HTTP-запроса. Ещё `SubmissionService` обращается прямо к `AssignmentRepository`, хотя в проекте существует `AssignmentService`. Это не стрелка вверх, но один слой сервиса в этом месте обходит другой сервис и сам работает с чужим репозиторием.

Я бы сделал отдельную команду, например `SubmitWorkCommand`, с id задания, списком ссылок, комментарием и нейтральным описанием файла. Контроллер преобразовывал бы `MultipartFile` в эту команду, а `SubmissionService` работал бы через интерфейс файлового хранилища и не зависел от Spring Web.

**Зачем нужна граница:** чтобы правила сдачи можно было использовать из веб-формы, REST API или другого интерфейса без изменений в сервисе.

## PetClinic — сценарий «добавить визит»

Эту часть выполнял агент `/root/petclinic_trace` на модели `gpt-6.1-sol`.

Агент исследовал официальный репозиторий [spring-projects/spring-petclinic](https://github.com/spring-projects/spring-petclinic), ветку `main`, commit [`500158f`](https://github.com/spring-projects/spring-petclinic/tree/500158f732419217507c7656904b8e6aa1bcc0d6).

### Какие слои нашёл агент

- Представление и HTTP: `VisitController` и шаблон `templates/pets/createOrUpdateVisitForm.html`.
- Доменная модель: `Owner`, `Pet`, `Visit`.
- Доступ к данным: `OwnerRepository`, который наследуется от `JpaRepository<Owner, Integer>`.
- Инфраструктура: Spring Data JPA, Hibernate и база данных.

Отдельного сервиса для добавления визита в этой цепочке нет. `VisitController` получает `OwnerRepository` через конструктор и обращается к нему напрямую.

### Как проходит добавление визита

У `VisitController` есть метод `loadPetWithVisit` с аннотацией `@ModelAttribute`. Spring MVC вызывает его до обработчика GET и до обработчика POST. Поэтому сначала выполняется подготовка модели:

```text
VisitController.java.loadPetWithVisit
  → OwnerRepository.java.findById
  → Owner.java.getPet
  → Visit.java.Visit
  → Pet.java.addVisit
    → Pet.java.getVisits
    → Collection.add
```

На этом этапе контроллер загружает владельца по `ownerId`, находит его питомца по `petId`, создаёт пустой `Visit` и заранее добавляет его в коллекцию визитов питомца.

При открытии формы дальнейшая цепочка короткая:

```text
VisitController.java.loadPetWithVisit
  → VisitController.java.initNewVisitForm
  → templates/pets/createOrUpdateVisitForm.html
```

При отправке формы Spring заполняет созданный объект `Visit` значениями пользователя и запускает Bean Validation. После этого выполняется основная цепочка:

```text
VisitController.java.loadPetWithVisit
  → Spring MVC: заполнение полей формы и @Valid
  → VisitController.java.processNewVisitForm
    → Owner.java.addVisit
      → Owner.java.getPet
      → Pet.java.addVisit
        → Pet.java.getVisits
        → Collection.add
    → OwnerRepository.java.save
      → Spring Data JPA
      → Hibernate
      → SQL
      → база данных
```

`processNewVisitForm` дополнительно проверяет дату визита: она должна быть в будущем. Если дата неверная или Bean Validation нашёл ошибку, контроллер снова показывает форму и до `save` не доходит.

При успехе сохраняется не сам `Visit`, а весь объект `Owner`. Внутри него находится `Pet`, а внутри питомца — коллекция визитов. Для связей `Owner → Pet` и `Pet → Visit` указан `CascadeType.ALL`, поэтому Hibernate сохраняет новый визит каскадно. Сам метод `Pet.addVisit` запросов к базе не делает.

Вызов `Pet.addVisit` встречается дважды: первый раз в `loadPetWithVisit`, второй — внутри `Owner.addVisit` после отправки формы. Коллекция визитов имеет тип `Set`, и в неё повторно добавляется тот же экземпляр `Visit`, поэтому второй одинаковый элемент не появляется.

После сохранения контроллер перенаправляет пользователя на `/owners/{ownerId}`, где уже показывается страница владельца с добавленным визитом.

### Все ли стрелки идут вниз

Не все стрелки в цепочке означают переход между слоями. Например, `Owner.addVisit → Pet.addVisit` — это вызов внутри одного доменного слоя. Возвраты результатов идут обратно вверх по стеку, но это не обратные зависимости между классами. Доменные классы `Owner`, `Pet` и `Visit` ничего не знают о `VisitController`.

Главная особенность этой схемы в том, что контроллер перескакивает через сервисный слой: **`VisitController → OwnerRepository`**. Для маленького учебного приложения это работает, но правило о допустимой дате визита остаётся прямо в HTTP-контроллере. Если появится REST API или другой способ добавить визит, это правило придётся повторить.

Я бы добавил сервис с методом вроде `VisitBookingService.bookVisit(ownerId, petId, date, description)`. Внутри одной транзакции он загружал бы владельца, находил питомца, проверял дату, добавлял визит и сохранял результат. Контроллеру остались бы только получение полей формы, вызов сервиса и показ ошибок.

Также я бы не добавлял пустой `Visit` в коллекцию питомца на этапе подготовки формы. Для формы можно использовать отдельный объект ввода, а настоящий визит создавать только после успешной проверки данных.

**Зачем нужна граница:** чтобы правила добавления визита не зависели от HTTP-контроллера и одинаково работали при любом способе вызова.
