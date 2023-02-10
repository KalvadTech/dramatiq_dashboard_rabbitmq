port ?= 8080

install:
	python3.11 -m venv env
	. env/bin/activate && pip3.11 --version
	. env/bin/activate && python3.11  -m pip install --upgrade pip
	. env/bin/activate && pip3.11 --version
	. env/bin/activate && pip3.11 install -r requirements.txt --use-pep517
	npm install

greenkeeping:
	. env/bin/activate && pur -r requirements.txt

server:
	. env/bin/activate && python dashboard.py

prod:
	gunicorn -w 4 -b :$(port) 'dashboard:app'

clean:
	rm -rf env/