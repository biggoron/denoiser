import requests
import array

r = requests.get(
    'http://0.0.0.0:8080/',
    params={
        "flush": True,
        "uid": 1,
        "data": array.array('B', [0] * 8000),
        "start": 0,
        "end": 8000})
print(r.content)
