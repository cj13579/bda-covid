# Bermuda COVID-19 Data

A scraper and simple web page for displaying better Bermuda COVID-19 statistics.

https://cj13579.github.io/bda-covid

## Development

This is a project written in Python and has one main file: `app.py`. 

To get started with the project after cloning the repository:

1. Create a venv: `python -m venv env`
2. Activate venv: `. env/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`

There is also a notebook for exploring the data a bit more. For now, it just recreates the charts that are plotted in the JS file.

To run a local version of the web page, change directories into the `docs` folder and run the following: `python -m http.server`. The address and port will be displayed on your command line. 

