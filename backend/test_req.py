import requests
res = requests.post("http://127.0.0.1:8000/api/backtest/run", json={"ticker": "RELIANCE.NS", "years": 5, "initial_capital": 100000.0})
print("STATUS:", res.status_code)
print("BODY:", res.text)
