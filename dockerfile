FROM jupyter/minimal-notebook
EXPOSE 3333:8888
COPY . ./
RUN pip install -r requirements.txt
