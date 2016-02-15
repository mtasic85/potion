# real  0m1.278s
# user  0m0.283s
# sys   0m0.020s

import requests

results = [
    requests.get('http://ipinfo.io/ip')
    for i in range(10)
]

print(results)
