# app.py
import os

import openai
import tiktoken
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS
from constants import API_KEY_NAME, MODEL_NAME, DEFAULT_PORT, PROMPT_FORMAT_TITLE, SYSTEM_MESSAGE, \
    PROMPT_FORMAT_METADESCRIPTION
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)
openai.api_key = os.getenv(API_KEY_NAME)
MAX_TOKENS = 16000
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def ensure_valid_url(url):
    if len(url) == 0:
        return url
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
    encoding = tiktoken.encoding_for_model(MODEL_NAME)

    keyword = request.json['keyword']
    url = ensure_valid_url(request.json['url'])
    language = request.json['language']
    excluded_words = request.json['excluded_words']
    content = ""

    # Only fetch URL content if it's not empty
    if url:
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            content = " ".join([p.text for p in soup.find_all('p')])
        except requests.exceptions.Timeout:
            return jsonify({'error': 'Timeout error'}), 408
        except requests.exceptions.TooManyRedirects:
            return jsonify({'error': 'Too many redirects. Please check the URL.'}), 400
        except requests.exceptions.RequestException as e:
            return jsonify({'error': 'URL fetching error. Your URL might be wrong.', 'message': str(e)}), 400

    # Checking tokens and possibly breaking the content
    full_prompt = PROMPT_FORMAT_TITLE.format(keyword=keyword, content=content, language=language, excluded_words=excluded_words)
    token_count = len(encoding.encode(full_prompt))
    print(f"The text contains {token_count} tokens.")

    messages = [{"role": "system", "content": SYSTEM_MESSAGE}]

    if token_count > MAX_TOKENS:
        # Breaking the content and sending in batches.
        split_content = [full_prompt[i:i + MAX_TOKENS] for i in range(0, len(full_prompt), MAX_TOKENS)]
        for partial_prompt in split_content:
            messages.append({"role": "user", "content": partial_prompt})
    else:
        messages.append({"role": "user", "content": full_prompt})

    try:
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=messages
        )
        title = response.choices[0].message.content

        prompt = PROMPT_FORMAT_METADESCRIPTION.format(language=language,excluded_words=excluded_words)
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
    if os.getenv("FLASK_ENV") == "development":
        app.run(debug=True, port=DEFAULT_PORT)
    else:
        port = int(os.environ.get("PORT", DEFAULT_PORT))
        app.run(host='0.0.0.0', port=port)

