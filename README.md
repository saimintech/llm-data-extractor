bash setup.sh /var/www/html

pm2 start venv/bin/python --name my_flask_app -- app.py
