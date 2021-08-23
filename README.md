# iot_aws_mqtt_checkers

Projekt został stworzony na potrzeby przemiotu **IOT**

Gra w warcaby korzystająca z wyświetlacza LED oraz joysticka płytki Sense Hat.

Komunikacja pomiędzy graczami zapewniona jest poprzez serwer REST API napisany z wykorzystaniem frameworka Fast API oraz kolejki komunikatów MQTT zapewnionej przez usługę AWS.

Dodatkowo istnieje możliwość wytrenowania prostego modelu Drzewa Decyzyjnego na podstawie wykonanych ruchów, aby przewidzieć kolejny ruch gracza.
