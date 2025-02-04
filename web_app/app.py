from flask import Flask, request, jsonify, render_template, send_from_directory
from elasticsearch import Elasticsearch
import re

app = Flask(__name__, static_folder='static', template_folder='templates')

es = Elasticsearch(['http://localhost:9200'])
index_name = 'crawler_index'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get('query', '').strip()
    page = data.get('page', 1)
    size = data.get('size', 10)

    if not query:
        return jsonify({"error": "No terms entered."}), 400

    from_ = (page - 1) * size

    es_query = {
        "from": from_,
        "size": size,
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["title", "keywords", "content"]
            }
        }
    }

    try:
        response = es.search(index=index_name, body=es_query)

        hits = response.get('hits', {}).get('hits', [])
        total = response.get('hits', {}).get('total', {}).get('value', 0)

        seen_titles = set()
        results = []
        for hit in hits:
            source = hit.get('_source', {})
            title = source.get('title', 'No Title')

            normalized_title = re.sub(r'\s*-\s*Page\s*\d+', '', title, flags=re.IGNORECASE)

            if normalized_title in seen_titles:
                continue

            seen_titles.add(normalized_title)
            results.append({
                'title': title,
                'url': source.get('url', '#'),
                'keywords': source.get('keywords', []),
                'content': source.get('content', 'No Content')
            })

        total_pages = (total + size - 1) // size
        total_pages = min(total_pages, 27)

        return jsonify({
            "results": results,
            "total": total,
            "page": page,
            "size": size,
            "total_pages": total_pages
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


if __name__ == '__main__':
    app.run(debug=True)
