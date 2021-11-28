
start:
	gunicorn app.main:app --workers 1 --threads 4 --worker-class uvicorn.workers.UvicornWorker --max-requests 5


run:
	uvicorn app.main:app --reload --host 0.0.0.0


generate:
	python generate.py
