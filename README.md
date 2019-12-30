Telegram бот для учёта личных расходов и ведения бюджета.

В переменных окружения надо проставить API токен бота, а также адрес proxy и логин-пароль к ней.

`TELEGRAM_API_TOKEN` — API токен бота

`TELEGRAM_PROXY_URL` — URL прокси сервера

`TELEGRAM_PROXY_LOGIN` — логин прокси сервера

`TELEGRAM_PROXY_PASSWORD` — пароль прокси сервера

Использование с Docker (предварительно заполните ENV переменные, указанные выше, в Dockerfile):

```
docker build -t tgfinance ./
docker run -ti --name tg tgfinance
```

