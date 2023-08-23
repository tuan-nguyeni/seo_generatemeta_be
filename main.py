# app.py
import os

import openai
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS
from constants import API_KEY_NAME, MODEL_NAME, DEFAULT_PORT, PROMPT_FORMAT_TITLE, SYSTEM_MESSAGE, \
    PROMPT_FORMAT_METADESCRIPTION

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv(API_KEY_NAME)


def ensure_valid_url(url):
    # Ensure URL starts with http:// or https://
    if not url.startswith(('http://', 'https://')):
        if not url.startswith('www.'):
            url = 'www.' + url
        url = 'https://' + url

    # Ensure URL ends with a trailing slash
    if not url.endswith('/'):
        url += '/'

    return url


@app.route('/generate-meta', methods=['POST'])
def generate_meta():
    keyword = request.json['keyword']
    url = ensure_valid_url(request.json['url'])
    language = request.json['language']

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Timeout error'}), 408
    except requests.exceptions.TooManyRedirects:
        return jsonify({'error': 'Too many redirects. Please check the URL.'}), 400
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'URL fetching error. Your URL might be wrong or empty', 'message': str(e)}), 400

    soup = BeautifulSoup(response.text, 'html.parser')
    content = " ".join([p.text for p in soup.find_all('p')])

    try:
        prompt = PROMPT_FORMAT_TITLE.format(keyword=keyword, content=content, language=language)
        messages = [{"role": "system", "content": SYSTEM_MESSAGE}]
        messages.append({"role": "user", "content": prompt})

        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=messages
        )
        title = response.choices[0].message.content

        prompt = PROMPT_FORMAT_METADESCRIPTION.format(language=language)
        messages.append({"role": "user", "content": prompt})

        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=messages
        )
        meta_description = response.choices[0].message.content

    except openai.error.OpenAIError as e:
        return jsonify({'error': 'OpenAI service error', 'message': str(e)}), 500

    return jsonify({'title': title, 'description': meta_description})



if __name__ == '__main__':
    #for production:
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    app.run(host='0.0.0.0', port=port)
    #For localhost:
    #app.run(debug=True, port=DEFAULT_PORT)
