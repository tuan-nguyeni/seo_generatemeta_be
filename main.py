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
        response = requests.get(url)
    except requests.exceptions.TooManyRedirects:
        return jsonify({'title': 'error: Too many redirects. Please check the URL and try again. Error code: 400', 'description': ''})
    soup = BeautifulSoup(response.text, 'html.parser')
    content = " ".join([p.text for p in soup.find_all('p')])

    print("url is " + url)
    print("keyword is " + keyword)
    print("content is " + content)

    # Here you can implement logic to generate the title and meta based on the keyword and content.

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

    return jsonify({'title': title, 'description': meta_description})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", DEFAULT_PORT))
    app.run(host='0.0.0.0', port=port)

