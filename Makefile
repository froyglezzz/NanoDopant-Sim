.PHONY: install test run-demo clean

install:
	pip install -r requirements.txt

test:
	python -m pytest tests/ -v --tb=short --cov=physics_engine --cov-report=term-missing

run-demo:
	python -m cli.main --dopant B --temp 1000 --time 3600 --profile erfc --output all

clean:
	python -c "import shutil, pathlib; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').glob('output_*')]; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]; shutil.rmtree('.pytest_cache', ignore_errors=True)"
