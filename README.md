## Cel projektu
Symulacja działania aukcji w grze MMO. Prezentacja problemów współbieżności (Race Conditions)
w systemach rozproszonych oraz metod ich rozwiązywania przy użyciu blokady w bazie danych
i kolejek wiadomości. Wiele procesów próbuje jednocześnie zmodyfikować ten sam zasób,
w ramach czego projekt prezentuje:
- **Asynchroniczność**: Rozdzielanie przyjmowania żądań (API) od ich przetwarzania (Worker)
za pomocą RabbitMQ
- **Race Condition**: Symulacja sytuacji, w której wielu użytkowników kupuje ten sam unikalny
przedmiot w tej samej milisekundzie
- **Pessimistic Locking**: Zastosowanie blokady `SELECT ... FOR UPDATE` w PostgreSQL,
aby zagwarantować spójność danych
- **Dead Letter Queue**: Obsługa błędnych wiadomości lub wstrzykiwań

## Wykorzystane narzędzia
- **Język**: _Python 3.13_
- **API Framework**: _FastAPI_
- **Baza Danych**: _PostgreSQL_ (_SQLAlchemy ORM_)
- **Message Broker**: _RabbitMQ_
- **Klient Kolejki**: _Pika_
- **Konteneryzacja**: _Docker/Docker Compose_
- **Testy**: Skrypt oparty o _asyncio_ i _httpx_

## Architektura
[Client] -> [REST API] -> [RabbitMQ] -> [Worker 1] -> [PostgreSQL]  
------------------------------------------------- -> [Worker 2] -> [PostgreSQL]  
------------------------------------------------- -> ...

## Uruchomienie
`docker-compose up --build` (skalowanie workerów w `docker-compose.yml`)  

**Scenariusz testowy**:
`docker-compose run --rm scenario`  
Skrypt wykona dwa scenariusze:
1. n użytkowników próbuje kupić ten sam unikalny przedmiot w tej samej chwili.
2. Wstrzyknięcie błędnych dadnych (zły JSON, ujemne ID....) bezpośrednio do kolejki.

**Przydatne endpointy**:  
- `http://localhost:8000/docs` - Swagger UI
- `http://localhost:15672` - RabbitMQ

**Własna konfiguracja**:  
Ilość instancji workerów (`replicas`):  
**`/docker-compose.yml`**
```
  worker:
    build: ./worker
    deploy:
      mode: replicated
      replicas: 5
```

Ilość userów w scenariuszu (`n_requests`):  
**`/scenario.py`**
```python
async def main():
    await attack_concurrency(n_requests = 10)
    attack_poison()
```

Błędne wiadomości w JSON (`poison_pills`):  
**`/scenario.py`**  
```python
poison_pills = [
    "not JSON",
    json.dumps({"item_id": "tekst", "user_id": 1}),
    json.dumps({"item_id": 999999999999999, "user_id": 1}),
    json.dumps({"item_id": -1, "user_id": 66}),
    json.dumps({"user_id": 5})
]
```