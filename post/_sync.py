import requests

tasks = ['http://www.baidu.com']*10

for url in tasks:
    requests.get(url)



