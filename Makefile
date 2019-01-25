build: clean
	python setup.py sdist
	twine upload dist/*

clean:
	rm -rf dist
	rm -rf *.egg-info
