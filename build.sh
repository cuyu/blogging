sudo rm -rf dist
sudo python setup.py sdist
twine upload dist/*