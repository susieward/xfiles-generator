
start:
	gunicorn --workers 1 --worker-class uvicorn.workers.UvicornWorker --threads 2 app.main:app


run:
	uvicorn app.main:app --reload
