# Web Proxy with Frontend

## Backend (Flask)
To run the proxy server:

1. Install dependencies:
   ```
   pip install flask requests flask-cors
   ```

2. Start the server:
   ```
   python proxy_server.py
   ```

## Frontend
Open `proxy_frontend.html` in a browser. Ensure it’s served from the same domain as your backend or configure CORS.

## Deployment
You can deploy this using:
- Render.com (Free)
- Heroku
- VPS (with Docker or system Python)
