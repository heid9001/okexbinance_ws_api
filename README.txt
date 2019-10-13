Стэк: rabbitmq, aiohttp, docker

Установка и запуск

докер
docker-compose build --no-cache
docker-compose up -d --force-recreate
docker-compose logs sub

без докера
# нужно установить rabbitmq локально https://www.vultr.com/docs/how-to-install-rabbitmq-on-ubuntu-16-04-47
source env.sh

# websocket клиенты
python -m rialtows.bootstrap binance &
python -m rialtows.bootstrap okex &

# rabbitmq подписчик
python -m rialtows.bootstrap sub

