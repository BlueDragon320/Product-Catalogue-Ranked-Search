import os
from app import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'development')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() in ('true', '1', 'yes')
    app.run(host=host, port=port, debug=debug)
