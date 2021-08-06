rm -r dist/ build/ *.egg-info/
python setup.py bdist_wheel
python setup.py sdist
python3 -m twine upload dist/*
sleep 2
pip uninstall aitool
pip install aitool --upgrade
rm -r dist/ build/ *.egg-info/
