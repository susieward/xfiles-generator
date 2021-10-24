
start:
	gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker


run:
	uvicorn app.main:app --workers 1 --limit-max-requests 5
