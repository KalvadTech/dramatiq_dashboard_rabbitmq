port ?= 8080

install:
	python -m venv env
	. env/bin/activate && pip install -r requirements.txt
	npm install

server:
	. env/bin/activate && python dashboard.py

prod:
	gunicorn -w 4 -b :$(port) 'dashboard:app'

clean:
	rm -rf env/