build:
	rm -rf dist build *.egg-info
	python -m build
	python -m twine check dist/*

publish: build
	twine upload dist/*
