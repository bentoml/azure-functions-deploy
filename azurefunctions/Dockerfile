FROM mcr.microsoft.com/azure-functions/python:4-python3.8

ENV AzureWebJobsScriptRoot=/home/site/wwwroot \
    AzureFunctionsJobHost__Logging__Console__IsEnabled=true

# Instal Azure Functions with BentoML 0.13.2 LTS
RUN pip install azure-functions install bentoml==0.13.2 typing_extensions

# https://github.com/MicrosoftDocs/azure-docs/issues/26761
# Copying BentoService to Azure function specific directory
COPY . /home/site/wwwroot

# Install pip dependencies
RUN if [ -f /home/site/wwwroot/bentoml-init.sh ]; then /bin/bash -c /home/site/wwwroot/bentoml-init.sh; fi