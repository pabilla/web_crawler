import json
import re
import langid
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

stopwords_en = set(stopwords.words('english'))
stopwords_fr = set(stopwords.words('french'))

def clean_text(text):
    text = text.lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-zàâçéèêëîïôûùüÿñæœ\s]', '', text)
    return text

def detect_language(text):
    lang, score = langid.classify(text)
    if lang.startswith('en'):
        return 'english'
    elif lang.startswith('fr'):
        return 'french'
    else:
        return 'unknown'

def preprocess_document(content):
    lang = detect_language(content)
    if lang == 'unknown':
        pass

    cleaned = clean_text(content)

    tokens = word_tokenize(cleaned, language='english')

    if lang == 'english':
        tokens = [t for t in tokens if t not in stopwords_en and len(t) > 1]
    elif lang == 'french':
        tokens = [t for t in tokens if t not in stopwords_fr and len(t) > 1]
    else:
        tokens = [t for t in tokens if len(t) > 1]

    return ' '.join(tokens), lang

def main():
    input_file = '../web_crawler/data.jsonl'
    output_file = '../../final_data/data_processed.jsonl'

    documents = []
    original_data = []

    with open(input_file, 'r', encoding='utf-8') as infile:
        for line_number, line in enumerate(infile, 1):
            try:
                data = json.loads(line)
                content = data.get('content', '')
                processed_text, lang = preprocess_document(content)

                documents.append(processed_text)
                original_data.append(data)

            except json.JSONDecodeError:
                print(f"[Line {line_number}] JSON decoding error.")
            except Exception as e:
                print(f"[Line {line_number}] An error has occurred : {e}")
                documents.append("")
                original_data.append({'title': '', 'url': '', 'content': '', 'keywords': []})

    vectorizer = TfidfVectorizer(
        max_df=0.9,
        min_df=5,
        ngram_range=(1, 1)
    )
    tfidf_matrix = vectorizer.fit_transform(documents)
    feature_names = vectorizer.get_feature_names_out()

    top_n = 10
    keywords_per_doc = []
    for doc_idx, row in enumerate(tfidf_matrix):
        row_array = row.toarray()[0]
        top_indices = row_array.argsort()[-top_n:][::-1]
        top_keywords = [feature_names[i] for i in top_indices if row_array[i] > 0]
        keywords_per_doc.append(top_keywords)

    output_data = []
    for data, keywords in zip(original_data, keywords_per_doc):
        data['keywords'] = keywords
        output_data.append({
            'title': data.get('title', ''),
            'url': data.get('url', ''),
            'keywords': data.get('keywords', []),
            'content': data.get('content', '')
        })

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for item in output_data:
            outfile.write(json.dumps(item, ensure_ascii=False) + '\n')

    print(f"Keyword extraction completed. Results in '{output_file}'.")


if __name__ == "__main__":
    main()
