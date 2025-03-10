# 🚀 Soda Web Application

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-2.3-green)
![Docker](https://img.shields.io/badge/Docker-24.0-blueviolet)
![Soda Core](https://img.shields.io/badge/Soda_Core-3.0-orange)

Soda Web Application — это веб-приложение, разработанное для упрощения работы с инструментом **Soda Core**, который используется для проверки качества данных. Приложение предоставляет удобный интерфейс для создания и выполнения тестов качества данных, а также для управления конфигурациями подключения к источникам данных.

---

## 🌟 Основные функции

- **🔐 Авторизация пользователей**: Регистрация и вход в систему.
- **⚙️ Управление конфигурациями**: Создание и валидация конфигурационных файлов для подключения к источникам данных.
- **🧪 Создание и выполнение тестов**: Ввод и выполнение тестов качества данных с отображением результатов.
- **🗂️ Управление файлами**: Удаление конфигурационных и тестовых файлов.

---

## 🛠️ Технологии

- **Python 3.11**: Основной язык программирования.
- **Flask**: Веб-фреймворк для создания приложения.
- **SQLAlchemy**: ORM для работы с базой данных.
- **Soda Core**: Инструмент для проверки качества данных.
- **Docker**: Контейнеризация приложения для удобства развертывания.

---

## 🚀 Установка и запуск

### 📋 Требования

- Docker

### 📥 Инструкции по установке

```cmd
   docker pull myalkool/soda_web
   docker run -d -p 5000:5000 myalkool/soda_web
   ```
   Перейдите по адресу http://localhost:5000.
   
## 🧪 Пример тестовых полей:

## config
```
  data_source my_postgres:
  type: postgres
  connection:
    host: host.docker.internal
    port: 5432
    username: postgres
    password: pass
    database: db
```
## test
```
  checks for book_collection:
  - row_count < 0
  - invalid_count(id) = 0
  - custom_sql:
      name: "avg_published_year"
      query: |
        SELECT avg(published_year) AS avg_published_year
        FROM book_collection
      fail: when avg_published_year < 1000
      warn: when avg_published_year < 2000
```

