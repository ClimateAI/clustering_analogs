FROM continuumio/miniconda3
ADD env.yml /tmp/env.yml
RUN conda env create -f /tmp/env.yml
COPY . /
SHELL ["conda", "run", "-n", "apienv", "/bin/bash", "-c"]
# Make sure the env is activated:
RUN echo "Make sure flask is installed:"
RUN python -c "import flask"
# The code to run when container is started:
# Change server timezone
RUN cp /usr/share/zoneinfo/America/Los_Angeles /etc/localtime
# Create directories
RUN mkdir soilGrib
RUN mkdir temp
RUN mkdir data
# Install curl for downloading scriptsudo apt-get install libeccodes0
RUN apt-get update && apt-get -y install curl
# Install eccodes for xarray library
RUN apt-get update && apt-get -y install libeccodes0
# ENTRYPOINT ["conda", "run", "-n", "apienv", "gunicorn", "-c", "./gunicorn.config.py","--timeout","60", "run:app"]
CMD exec conda run -n apienv gunicorn --bind :$PORT -c ./gunicorn.config.py   --timeout 0 main:app
