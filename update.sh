rm -r dist/ build/ *.egg-info/
python setup.py bdist_wheel
python setup.py sdist
python3 -m twine upload dist/*  --username yuejiaxiang --password 1qazxsw2\'pypi
pip install aitool --upgrade
rm -r dist/ build/ *.egg-info/
