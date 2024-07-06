FROM python:3.9.7-slim-buster

ENV FLYWHEEL="/flywheel/v0"
WORKDIR ${FLYWHEEL}

RUN apt-get update \
&& apt-get install gcc -y \
&& apt-get clean

# install main dependenices
RUN pip install flywheel_gear_toolkit
RUN pip install fw_core_client
RUN pip install flywheel-sdk
RUN pip install Pillow==9.5.0
RUN pip install geojson==3.0.1

# copy main files into working directory
COPY run.py manifest.json $FLYWHEEL/
COPY fw_gear_geojson2image ${FLYWHEEL}/fw_gear_geojson2image 
COPY ./ $FLYWHEEL/

# start the pipeline
RUN chmod a+x $FLYWHEEL/run.py
RUN chmod -R 777 .
ENTRYPOINT ["python","/flywheel/v0/run.py"]
