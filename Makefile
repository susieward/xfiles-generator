
start:
	gunicorn --workers 1 --worker-class gthread --threads 2 main:app


run:
	uvicorn app.main:app --reload
