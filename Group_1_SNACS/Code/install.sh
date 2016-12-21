echo "Creates a python virtual environment to setup all data"
echo "Only python 3.5.2 on Windows 10 64-bit has been tested"
echo "It will likely work with Python 3.4+ on a 64-bit Windows machine"
echo "It will need changes to work in a Linux environment"

if [ ! -d py ]; then
	python -m venv py
fi

py/Scripts/python -m pip install --upgrade pip
py/Scripts/pip install praw==3.5.0
py/Scripts/pip install pytz
py/Scripts/pip install whls/python_igraph-0.7.1.post6-cp35-none-win_amd64.whl
py/Scripts/pip install plotly
py/Scripts/pip install networkx
py/Scripts/pip install matplotlib


