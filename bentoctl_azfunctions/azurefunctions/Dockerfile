# To enable ssh & remote debugging on app service change the base image to the one below
# FROM mcr.microsoft.com/azure-functions/python:3.0-python3.8-appservice
FROM mcr.microsoft.com/azure-functions/python:3.0-python3.8

ENV AzureWebJobsScriptRoot=/home/site/wwwroot 
ENV AzureFunctionsJobHost__Logging__Console__IsEnabled=true
# https://github.com/MicrosoftDocs/azure-docs/issues/26761
ARG BENTO_PATH=/home/site/wwwroot
ENV BENTO_PATH=$BENTO_PATH
WORKDIR $BENTO_PATH

# install bentoml
RUN python -m pip install bentoml=={bentoml_version} --pre


# copy over env directory
COPY ./env ./env
RUN chmod +x ./env/docker/init.sh
RUN ./env/docker/init.sh ensure_python
RUN ./env/docker/init.sh restore_conda_env
RUN ./env/docker/init.sh install_pip_packages
RUN ./env/docker/init.sh install_wheels
RUN ./env/docker/init.sh user_setup_script

# copy over all remaining bento files
COPY . ./
