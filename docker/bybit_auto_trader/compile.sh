docker image rm bybit_auto_trader
docker build --no-cache -t bybit_auto_trader ./docker/bybit_auto_trader/

# docker run -v ./:/bybit_bot/ bybit_auto_trader