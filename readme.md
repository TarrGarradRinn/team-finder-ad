# TeamFinder (Вариант 3)

## 1. Виртуальное окружение

Перед началом работы необходимо создать и активировать виртуальное окружение Python.

1. **Создайте виртуальное окружение (в папке проекта):**
```bash
   python3 -m venv venv
```

2. **Активируйте окружение:**

    - **Windows (PowerShell):**
```bash
      venv\Scripts\Activate.ps1
```
    - **Windows (cmd):**
```bash
      venv\Scripts\activate
```
    - **Linux/Mac:**
```bash
      source venv/bin/activate
```

3. **Установите зависимости из `requirements.txt`:**
```bash
   pip install -r requirements.txt
```

## 2. Создание `.env`

В репозитории есть пример `.env_example`, который нужно скопировать и заполнить:

```bash
cp .env_example .env
```

После этого откройте `.env` и укажите свои значения. Для запуска проекта установите `TASK_VERSION=3`.

| Переменная            | Назначение                                                                                                                                                 |
|-----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **DJANGO_SECRET_KEY** | Секретный ключ Django, используемый для подписи cookie и токенов. Можно сгенерировать при помощи `get_random_secret_key` из `django.core.management.utils` |
| **DJANGO_DEBUG**      | Режим отладки. Установите `True` во время разработки.                                                                                                      |
| **POSTGRES_DB**       | Имя базы данных PostgreSQL, которую будет использовать Django.                                                                                             |
| **POSTGRES_USER**     | Имя пользователя PostgreSQL.                                                                                                                               |
| **POSTGRES_PASSWORD** | Пароль пользователя PostgreSQL.                                                                                                                            |
| **POSTGRES_HOST**     | Адрес сервера БД. В случае локальной разработки localhost.                                                                                                 |
| **POSTGRES_PORT**     | Порт подключения к БД (по умолчанию `5432`).                                                                                                               |
| **TASK_VERSION**      | Укажите `3`.                                                                                                                                               |

---

## 3. Запуск PostgreSQL

```bash
docker compose up -d
```

Чтобы остановить:

```bash
docker compose down
```

Если возникает ошибка "permission denied while trying to connect to the Docker daemon socket", то может потребоваться добавить `sudo` перед командой.

После этого база данных будет доступна по адресу `localhost:5432`.

> Если на компьютере уже развёрнут сервер БД на порте 5432, целесообразнее будет изменить порт на нестандартный.
> Нестандартный порт нужно будет поставить слева в паре портов в docker-compose (`"5433":"5432"`) и в .env.

## 4. Миграции

```bash
python manage.py migrate
```

## 5. Запуск Django

```bash
python manage.py runserver
```

Проект доступен по адресу [http://localhost:8000](http://localhost:8000).