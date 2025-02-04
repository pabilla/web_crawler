from elasticsearch import Elasticsearch

es = Elasticsearch(['http://localhost:9200'])

mapping = {
    "mappings": {
        "properties": {
            "title": {
                "type": "text",
                "analyzer": "standard"
            },
            "url": {
                "type": "keyword"
            },
            "keywords": {
                "type": "keyword"
            },
            "content": {
                "type": "text",
                "analyzer": "standard"
            }
        }
    }
}

index_name = 'crawler_index'
if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name, body=mapping)
    print(f"Index '{index_name}' created with defined mapping")
else:
    print(f"Index '{index_name}' already exists.")
