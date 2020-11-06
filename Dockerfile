FROM continuumio/miniconda3
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update -y && apt-get install dialog apt-utils -y
RUN conda create --name niche python=3.8
ADD environment.yml /tmp/environment.yml
SHELL ["conda", "run", "-n", "niche", "/bin/bash", "-c"]
RUN apt-get update && apt-get install dialog python3-dev -y
RUN conda env update --file /tmp/environment.yml
RUN pip install flask xarray numpy xesmf pandas intake-esm
RUN conda list
COPY . /
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
