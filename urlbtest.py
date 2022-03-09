import orjson
import urllib3

encoded_data = orjson.dumps({"attribute": "value"})
http = urllib3.PoolManager()
resp = http.request(method="POST", url="http://httpbin.org/post", body=encoded_data)

print(orjson.loads(resp.data)["json"])
