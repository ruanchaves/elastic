# elastic
Trabalho para a disciplina de Sistemas Gerenciadores de Banco de Dados: demonstração do Elasticsearch.

As instruções para a execução da demonstração estão [no notebook Demonstração do Elasticsearch.ipynb](https://github.com/ruanchaves/elastic/blob/master/Demonstra%C3%A7%C3%A3o%20do%20Elasticsearch.ipynb).

# Descrição  

Nesta demonstração, baixamos um dataset de 1GB contendo as primeiras frases de todos os artigos da Wikipedia.  

Em seguida, inicializamos um servidor que nos permite construir grafos que mostram a correlação entre as entidades nomeadas extraidas do dataset.

Basta enviar uma requisição para `https://localhost:5000/1/Alan Turing` , e temos o resultado abaixo :

![](https://i.imgur.com/ROQB5h2.png)

![](https://i.imgur.com/TSjP1BM.png)

A grossura das arestas é proporcional à força da correlação entre as entidades nomeadas. 
