from flask import Flask, request, Response
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/go', methods=['GET', 'POST'])
def proxy():
    target_url = request.args.get('url')
    if not target_url:
        return 'Missing URL', 400

    try:
        headers = {
            'User-Agent': request.headers.get('User-Agent'),
            'Accept': request.headers.get('Accept'),
            'Accept-Language': request.headers.get('Accept-Language'),
        }

        if request.method == 'POST':
            resp = requests.post(
                target_url,
                data=request.form,
                headers=headers,
                cookies=request.cookies,
                timeout=10
            )
        else:
            resp = requests.get(
                target_url,
                headers=headers,
                cookies=request.cookies,
                timeout=10
            )

        content_type = resp.headers.get('Content-Type', '')

        if 'text/html' in content_type:
            soup = BeautifulSoup(resp.text, 'html.parser')
            base_url = target_url

            # Inject <base> to fix relative URLs
            if soup.head and not soup.head.find('base'):
                base_tag = soup.new_tag('base', href=base_url)
                soup.head.insert(0, base_tag)

            # Rewrite <a href>, <img src>, <script src>, <link href>
            for tag in soup.find_all(['a', 'img', 'script', 'link']):
                attr = 'href' if tag.name in ['a', 'link'] else 'src'
                if tag.has_attr(attr):
                    original = tag[attr]
                    if not original.startswith('data:'):  # skip base64
                        new_url = urljoin(base_url, original)
                        tag[attr] = '/go?url=' + new_url

            # Rewrite <form action>
            for form in soup.find_all('form'):
                action = form.get('action')
                if action:
                    new_action = urljoin(base_url, action)
                else:
                    new_action = base_url
                form['action'] = '/go?url=' + new_action

            # Remove Content Security Policy
            for meta in soup.find_all('meta', {'http-equiv': 'Content-Security-Policy'}):
                meta.decompose()

            return Response(str(soup), headers={
                'Content-Type': content_type,
                'X-Content-Type-Options': 'nosniff'
            })

        # Return other content types (e.g. images, CSS, JS) as-is
        return Response(resp.content, headers={
            'Content-Type': content_type,
            'X-Content-Type-Options': 'nosniff'
        })

    except Exception as e:
        return f'Error: {str(e)}', 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
