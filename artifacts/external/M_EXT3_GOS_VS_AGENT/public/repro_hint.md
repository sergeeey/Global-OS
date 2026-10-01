# Allowed repro hint (from issue body)

```python
import httpx

client = httpx.Client(base_url="https://httpbingo.org/get?data=1")
print(client.base_url.query)

response = client.get("")
print(response.json()["args"])
```

Expected: `b'data=1'` and `{'data': ['1']}` (or empty query if base query dropped).
Actual (bug): `b'data=1/'` and `{'data': ['1/']}`.
