#!/usr/bin/env bash
sudo rm -rf dist
sudo python setup.py sdist
twine upload dist/*