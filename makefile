install:
	python -m venv env
	. env/bin/activate && pip install -r requirements.txt

server:
	. env/bin/activate && python dashboard.py

clean:
	rm -rf env/