import pandas as pd
import random

import uncurl

import json
import requests
import sys
from time import sleep

import itertools
import spacy

json_header = { "Content-Type": "application/json" }

def pretty(res):
    result = res.json()['hits']['hits']
    for item in result:
        item['text'] = item['_source']['text']
        del(item['_source'])
    return pd.DataFrame(result)
    
def build_array(array, field):
    output = []
    for item in array:
        output.append({
            "match" : {field: item}
        })
    return output

def search(plus, minus, limit=1000):
    minus = []
    query = {
        "query": {
            "bool": {
                "must": build_array(plus, "text"),
                "must_not": build_array(minus, "text")
                }
            }
    }
    pages = []
    for i in range(0,limit,10):
        url = "http://localhost:9200/wiki/_search?size=10&from={0}".format(i)
        res = requests.get(url,
        data=json.dumps(query),
        headers=json_header
        )
        pages.append(res)
    return pages 

def more_like_this(pages, chosen_index="wiki", fields=["text"], limit=1000):
    indexes = []
    for i in range(0,len(pages)):
        try:
            indexes.extend(pretty(pages[i])['_id'].tolist())
        except:
            break
    like_list = [ {
        "_index" : chosen_index,
        "_id" : item
        } for item in indexes]
    query = {
            "query": {
                "more_like_this" : {
                    "fields" : fields,
                    "like" : like_list,
                    "min_term_freq" : 1,
                    "max_query_terms" : 25
                }
            }
        }
    result = []
    for i in range(0,10,limit):
        res = requests.get("http://localhost:9200/_search?size=10&from={0}".format(i),
             data=json.dumps(query),
            headers=json_header)
        result.append(pretty(res))
    return result

def similar_entities(start_node=0, result=[]):
    scores = []
    matches = []
    for df in result:
        scores.extend(df['_score'].tolist())
        matches.extend(df['text'].tolist())
    sentences = ' '.join(matches)
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(sentences)
    data = []
    for ent in doc.ents:
        data.append({ "entity" : ent.text, "label" : ent.label_ })
    data = [x for x in data if x['label'] in ["PERSON", "PRODUCT", "ORG"] ]
    entities = [ x['entity'] for x in data ]
    entity_score = [0] * len(entities)
    for idx1,match in enumerate(matches):
        for idx2,entity in enumerate(entities):
            if entity in match:
                entity_score[idx2] += scores[idx1]
    scored_entities = sorted(list(zip(entities, entity_score)), key=(lambda x: x[1]), reverse=True)
    df = pd.DataFrame([ {'entity' : x[0], 'score': x[1]}  for x in scored_entities ])

    try:
        df['score']
    except:
        return {"nodes": [], "edges": []}

    Q1 = df['score'].quantile(0.25)
    Q3 = df['score'].quantile(0.75)
    IQR = Q3 - Q1
    df = df[ ( df.score > Q1 ) & ( df.score < Q3 + 1.5 * IQR ) ]
    nodes = df['entity'].tolist()
    normalized_score = [ ( ( x - Q1 ) / (Q3 + 1.5 * IQR - Q1) ) for x in df['score'].tolist() ]
    integer_score = [ int(x * 10 + 1) for x in normalized_score ]
    node_list = [start_node] + [item for idx, item in enumerate(nodes)]
    edge_list = [ [start_node, item] for idx, item in enumerate(nodes)]
    for idx, item in enumerate(edge_list):
        item.append(integer_score[idx])
        item.append(normalized_score[idx])
    return {"nodes" : node_list, "edges": edge_list }


class Graph(object):

    def __init__(self):
        self.nodes = []
        self.edges = []
        self.visited = []
        self.iterations = 2

    def build_graph(self, term, iterations):
        print(term)
        start = similar_entities(
            start_node = term,
            result = more_like_this(search([term], []))
        )
        self.nodes.extend(start['nodes'])
        self.edges.extend(start['edges'])
        self.iterations -= 1
        self.visited.append(term)
        if iterations:
            for item in start['nodes']:
                if item not in self.visited:
                    self.build_graph(item, iterations - 1)

def convert_graph(nodes, edges):
    nodes = list(set(nodes))
    edges = sorted(edges)
    edges = [edges[i] for i in range(len(edges)) if i == 0 or edges[i] != edges[i-1]]
    json_nodes = []
    json_edges = []
    for idx,item in enumerate(nodes):
        json_nodes.append({
            "id": idx,
            "label": item,
            "url" : "http://localhost:5000/1/{0}".format(item)
        })
    for idx,item in enumerate(edges):
        json_edges.append({
            "from": nodes.index(item[0]),
            "to": nodes.index(item[1]),
            "value": item[2],
            "title": str(item[3]),
        })
    return {
        "nodes" : json_nodes,
        "edges" : json_edges
    }


if __name__ == '__main__':
    G = Graph()
    G.build_graph('Hadoop', 1)
    print(convert_graph(G.nodes, G.edges))
