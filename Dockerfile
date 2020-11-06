FROM continuumio/miniconda3
ENV DEBIAN_FRONTEND noninteractive
# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./
RUN conda create --name niche python=3.8
SHELL ["conda", "run", "-n", "niche", "/bin/bash", "-c"]
# Activate the environment, and make sure it's activated:
RUN pip install -r requirements.txt
RUN conda install -c conda-forge xesmf -y
RUN conda list
# Make sure the env is activated:
RUN echo "Make sure flask is installed:"
RUN python -c "import flask"
# The code to run when container is started:
# Change server timezone
RUN cp /usr/share/zoneinfo/America/Los_Angeles /etc/localtime
# Install curl for downloading scriptsudo apt-get install libeccodes0
RUN apt-get update && apt-get -y install curl
# Install eccodes for xarray library
RUN apt-get update && apt-get -y install libeccodes0
# ENTRYPOINT ["conda", "run", "-n", "niche", "gunicorn", "-c", "./gunicorn.config.py","--timeout","60", "run:app"]
CMD exec conda run -n niche gunicorn --bind :$PORT -c ./gunicorn.config.py   --timeout 0 main:app
