# Запуск

1. В корневой директории проекта создать виртуальное окружение

- Linux

```sh
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ python -m pip install -r requirements.txt  
```

- Windows

```sh
$ py -3.10 -m venv venv
$ ./venv/Scripts/activate
(venv) $ python -m pip install -r requirements.txt  
```

2. Создать базу данных

- Linux

```sh
$ sudo -u postgres psql
postgres=# CREATE DATABASE tradeupdb;
postgres=# CREATE USER tradebot WITH PASSWORD 'psql'; 
postgres=# ALTER ROLE tradebot SET client_encoding TO 'utf8';
postgres=# ALTER ROLE tradebot SET default_transaction_isolation TO 'read committed';
postgres=# ALTER ROLE tradebot SET timezone TO 'Europe/Moscow';
postgres=# GRANT ALL PRIVILEGES ON DATABASE tradeupdb TO tradebot;
postgres=# \q
```

- Windows

* В пуске находим и открываем SQL Shell
* Server [localhost]: Enter
* Database [postgres]: Enter
* Port [5432]: Enter
* Username [postgres]: Enter
* Пароль пользователя postgres: Введите пароль от postgres
```sh
postgres=# CREATE DATABASE название_базы_данных;
postgres=# CREATE USER имя_пользователя WITH PASSWORD 'пароль'; 
postgres=# ALTER ROLE имя_пользователя SET client_encoding TO 'utf8';
postgres=# ALTER ROLE имя_пользователя SET default_transaction_isolation TO 'read committed';
postgres=# ALTER ROLE имя_пользователя SET timezone TO 'Europe/Moscow';
postgres=# GRANT ALL PRIVILEGES ON DATABASE название_базы_данных TO имя_пользователя;
postgres=# \q
```

Добавить данные в файл `backend/.env`

```sh
DATABASE_NAME="название_базы_данных"
DATABASE_USER="имя_пользователя"
DATABASE_PASSWORD="пароль"
DATABASE_HOST="localhost"
DATABASE_PORT=""
```

3. Сгенерировать в python пароль для django

```py
>> > from django.core.management.utils import get_random_secret_key
>> > get_random_secret_key()
'entwadfv&i6o'
```

Добавить данные в файл `backend/.env`

```sh
BACKEND_SECRET_KEY="entwadfv&i6o"
BACKEND_HOST="127.0.0.1"
BACKEND_PORT="8000"
```

4. Создать телеграм бота у bot father и получить api token

Добавить данные в файл `backend/.env`

```sh
BOT_USERNAME="blablabot"
TELEGRAM_API_TOKEN="564jkA"
```

5. Зарегистрироваться и получить токен на https://chart-img.com/account/api

Добавить данные в файл `backend/.env`

```sh
CHARTIMG_API_TOKEN="Cfasf4uk"
```

6. Сгенерировать ключ шифрования в python

```py
>> > from cryptography.fernet import Fernet
>> > Fernet.generate_key()
b'JkT1lE9VtAbPasdflsdf9OD0='
```

Добавить данные в файл `backend/.env`

```sh
ENCRYPTION_KEY="asfXcx2c9OD0="
```

7. Добавить адрес хостинга для webapp. Обязательна поддержка https протокола, иначе webapp не откроется в телеграм
   проложении.

Для тестирования можно использовать ngrok.io, который бесплатно открывает туннель для доступа к localhost с поддержкой
https.

```
$ ngrok http 8000
```

Для прода необходимо ввести адрес реального хостинга.

```sh
WEBAPP_HOST="32asdfsf9.eu.ngrok.io"
WEBAPP_PORT=""
```

8. Зарегистрироваться и получить токен на https://www.coinglass.com/ru/FundingRate

Добавить данные в файл `backend/.env`

```sh
COINGLASS_API_KEY=" "
```

9. Зарегистрироваться и получить токены на https://cryptocloud.plus/

Добавить данные в файл `backend/.env`

```sh
PAY_API_KEY=" "
PAY_SHOP_ID=" "
```

10. Добавить прокси только sock 5 !

Добавить данные в файл `backend/.env`

```sh
TELETHONE_PROXY="111.2:383838:29282:29292:3993"
```

11. Зарегистрироваться и получить токены на https://my.telegram.org/auth

Добавить данные в файл `backend/.env`

```sh
TELETHONE_API_ID=" "
TELETHONE_API_HASH=" "
```

12. Получить токены из куки хранилища (панель разработчика) сайта https://www.tradingview.com/

Добавить данные в файл `backend/.env`

```sh
TRADING_VIEW_API_SESSIONID=" "
TRADING_VIEW_API_SESSIONIDSIGN=" "
```

13. Получть токен с https://coinmarketcap.com/api/

Добавить данные в файл `backend/.env`

```sh
COINMARKETCUP_API=" "
```

14. Перейти в директорию `backend`

```sh
$ cd backend
```

15. Запустить django

```sh
(venv) [backend] $ python manage.py makemigrations
(venv) [backend] $ python manage.py migrate
(venv) [backend] $ python manage.py createsuperuser
(venv) [backend] $ python manage.py runserver
```

16. Запустить бота

```sh
(venv) [backend] $ python runbot.py
```

---

17. запуск сокета для получения индикаторов с trading view

```sh
(venv) [backend] $ python runwss.py
```

---

18. запуск парсера телеграмм каналов

```sh
(venv) [backend] $ python runparser.py
```

---

[Readme телеграм бота](/backend/telegram_bot/README.md)

[Readme вебсокет сервера](/backend/websocket/README.md)

