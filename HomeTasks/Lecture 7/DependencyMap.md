# Карта зависимостей StPlatform и PetClinic

## StPlatform: сдача домашней работы

Исследован репозиторий [UnMatty/StPlatform](https://gitverse.ru/UnMatty/StPlatform) на commit [`7bd1066`](https://gitverse.ru/UnMatty/StPlatform/commit/7bd10669913fbef8f8c6e7331c25420489edd8ba).

### Слои

- Контроллеры веб-страниц: `ActivateController`, `AssignmentPageController`, `AttachmentController`, `CabinetController`, `ConsentPageController`, `LoginController`, `PasswordResetController`, `TeacherAssignmentController`, `TeacherImportController`, `TeacherStudentController`.
- REST-контроллеры: `ApiAuthController`, `ApiAssignmentController`, `ApiSubmissionController`.
- Сервисы: `ActivationService`, `AssignmentService`, `ConsentService`, `PasswordResetService`, `PlatformUserDetailsService`, `StudentRemovalService`, `SubmissionService`, `UserService`.
- Репозитории Spring Data JPA: `AssignmentRepository`, `ConsentRecordRepository`, `SubmissionAttachmentRepository`, `SubmissionRepository`, `UserRepository`.
- Модель: `Assignment`, `ConsentRecord`, `Submission`, `SubmissionAttachment`, `User` и связанные enum-классы.
- Инфраструктурные компоненты: `AttachmentStorage` хранит файлы на диске, `InviteMailer` и `PasswordResetMailer` отправляют письма, `LinkValidator` проверяет ссылки.

`CommonPageModel`, `WebExceptionHandler` и `ApiExceptionHandler` относятся к обвязке слоя представления: добавляют общие данные страницы и преобразуют исключения в HTTP-ответы.

### Цепочка вызовов

Для успешной сдачи через веб-форму цепочка начинается с `POST /assignments/{id}/submit`:

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

Если студент прикрепил файл, после сохранения `Submission` выполняется дополнительная ветка:

```text
SubmissionService.java.submit
  → AttachmentStorage.java.store
    → Files.copy
  → SubmissionAttachmentRepository.java.save
```

После успешного выполнения контроллер возвращает redirect на `/assignments/{id}`. REST-вариант входит через `ApiSubmissionController.java.submit`, но затем вызывает тот же `SubmissionService.java.submit`.

### Направление зависимостей и граница

Основные стрелки идут вниз: контроллер → сервис → репозиторий или инфраструктура. Но граница не совсем чистая: `SubmissionService.submit` принимает `MultipartFile`, поэтому сервисный слой зависит от типа из Spring Web; кроме того, сервис обращается к `AssignmentRepository` напрямую, минуя `AssignmentService`.

Я бы провёл границу между HTTP и сценарием сдачи: контроллер преобразовывал бы форму в обычную команду и нейтральное описание файла, а сервис работал бы с ними через интерфейс хранилища, не зная о `MultipartFile`.

**Зачем нужна граница:** чтобы бизнес-правила сдачи не приходилось менять при замене HTTP-интерфейса или способа хранения файлов.

## PetClinic: добавление визита

Трассировку выполнил агент `/root/petclinic_trace`, модель `gpt-6.1-sol`.

Исследован официальный репозиторий [spring-projects/spring-petclinic](https://github.com/spring-projects/spring-petclinic), ветка `main`, commit [`500158f`](https://github.com/spring-projects/spring-petclinic/tree/500158f732419217507c7656904b8e6aa1bcc0d6).

### Слои

- Представление и HTTP: [`VisitController`](https://github.com/spring-projects/spring-petclinic/blob/500158f732419217507c7656904b8e6aa1bcc0d6/src/main/java/org/springframework/samples/petclinic/owner/VisitController.java), HTML-форма `createOrUpdateVisitForm.html`, после перенаправления — `OwnerController`.
- Доменная модель: `Owner`, `Pet`, `Visit`.
- Доступ к данным: `OwnerRepository`, наследующий `JpaRepository<Owner, Integer>`.
- Инфраструктура: Spring Data JPA, Hibernate и база данных.

Отдельного сервисного слоя в этом сценарии нет: `VisitController` обращается к `OwnerRepository` напрямую.

### Цепочка вызовов

Перед GET и POST Spring MVC вызывает метод с `@ModelAttribute`:

```text
VisitController.java.loadPetWithVisit
  → OwnerRepository.java.findById
  → Owner.java.getPet
  → Visit.java.Visit
  → Pet.java.addVisit
    → Pet.java.getVisits
    → Collection.add
```

При открытии формы продолжение выглядит так:

```text
VisitController.java.loadPetWithVisit
  → VisitController.java.initNewVisitForm
  → templates/pets/createOrUpdateVisitForm.html
```

При отправке заполненной формы:

```text
VisitController.java.loadPetWithVisit
  → Spring MVC: связывание полей формы и @Valid
  → VisitController.java.processNewVisitForm
    → Owner.java.addVisit
      → Owner.java.getPet
      → Pet.java.addVisit
        → Pet.java.getVisits
        → Collection.add
    → OwnerRepository.java.save
      → Spring Data JPA / Hibernate
      → SQL / база данных
```

Визит записывается каскадно при сохранении графа `Owner → Pet → Visit`, потому что у связей задан `CascadeType.ALL`. `Pet.addVisit` сам к базе не обращается.

### Направление зависимостей и граница

Не все стрелки обозначают переход на слой ниже: `Owner → Pet` — вызов внутри доменной модели, а результаты методов возвращаются вверх по стеку. При этом обратной зависимости доменных классов от контроллера нет. Главная архитектурная особенность — контроллер пропускает сервисный слой и обращается сразу к репозиторию.

Я бы добавил `VisitBookingService.bookVisit(ownerId, petId, date, description)`, который внутри одной транзакции загружал бы владельца, проверял правила, добавлял визит и сохранял результат. Контроллеру остались бы HTTP, поля формы и отображение ошибок; правило допустимой даты находилось бы в сценарии, а не только в контроллере.

**Зачем нужна граница:** граница отделяет правила записи на визит от HTTP и деталей хранения.
