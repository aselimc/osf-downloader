build:
	rm -rf dist build *.egg-info
	python -m build
	python -m twine check dist/*

publish: build
	twine upload dist/*

clean:
	rm -rf dist build *.egg-info
	rm -rf __pycache__
	rm -rf .ruff_cache
	rm -rf .pytest_cache
