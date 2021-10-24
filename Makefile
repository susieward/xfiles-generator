
start:
	gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker


run:
	uvicorn app.main:app --reload
