FROM jupyter/minimal-notebook

RUN mkdir app database framework resources
COPY app ./app
COPY framework ./framework
COPY resources ./resources

COPY requirements.txt ./
COPY Notebook.ipynb ./

# Necessary when creating the image on Windows to fix file permissions
USER root
RUN chown -R jovyan .
USER jovyan

RUN pip install -r requirements.txt
