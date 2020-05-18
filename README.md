# museums-linear-regression
##### Correlating museums visits with population size

This simple python service can look up the most visited museums in the world and fill up a small sqlite database with information about those museums and the city they're located in. This data can then be queried and obtained in a CSV format for easy ingestion in something like a Pandas Dataframe.

The Notebook.ipynb Jupyter Notebook presents data analysis and a simple linear regression model to attempt to correlate City Population with Museum Visits. A pre-rendered Notebook.html is available as a read-only version of the analysis. 

A Docker image configuration is provided that will create an instance of the app and run Jupyter with all required dependencies, ready to be connected to. 

### To run the service and connect via Jupyter

Build the docker image:
    
    docker build -t museums-linear-regression .

Run it, exposing the internal 8888 port used by Jupyter to whatever host port you want

    docker run -p 8888:8888 museums-linear-regression

Connect using the Jupyter URL provided in the command prompt, replacing the internal 8888 port with whatever port you've exposed 

# Data sources

Cities population database provided by <https://simplemaps.com/data/world-cities>