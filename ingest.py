import requests

dataset = 'wikisent2.txt'

with open(dataset,'r') as f:
    data = f.read().split('\n')


# Essa requisição busca evitar que o Elasticsearch reclame de low disk watermark ( quando o espaço máximo permitido em disco foi excedido )
requests.put("http://localhost:9200/_cluster/settings",
    data='{ "transient" : { "cluster.routing.allocation.disk.threshold_enabled" : false } }',
    headers={"Content-Type": "application/json"},
    cookies={},
)


# Iremos enviar o dataset para o Elasticsearch em pacotes de 80MB, com espaço de 0 segundos entre as requisições. 

SIZE = 8e+7
LATENCY = 0

# Os dois parâmetros acima devem ser editados caso não se atinja uma taxa de aproveitamento satisfatório.  
# Para a nossa finalidade, não é necessário ingerir 100% do dataset.

dump = ''
latency = 0
for idx,doc in enumerate(data):
    meta = { "index" : { "_index": "wiki", "_type": "snippet", "_id": idx }}
    entry = { "text": doc }
    dump += json.dumps(meta) + '\n' + json.dumps(entry) + '\n'
    if sys.getsizeof(dump) > 8e+7:
        response = requests.post("http://localhost:9200/_bulk",
                      data=dump,
                      headers={
                          "Content-Type": "application/json"
                      },
                      cookies={},
                     )
        del(dump)
        dump = ''
        sleep(latency)


# Agora iremos medir a taxa de aproveitamento como um fator entre 0 e 1.

lines = len(data)

response = requests.get("http://localhost:9200/wiki/_count",
                      headers={
                          "Content-Type": "application/json"
                      },
                     )

count = response.json()["count"]

status = count / lines

print(status)