# BentoML Azure Functions deployment tool


## Prerequisites

- An active AWS account configured on the machine with AWS CLI installed and configured
    - Install instruction: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html
    - Configure AWS account instruction: https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html
- Docker is installed and running on the machine.
    - Install instruction: https://docs.docker.com/install

- Install required python packages
    - `$ pip install -r requirements.txt`


## Deployment operations

### Create a deployment

Use command line
```bash
$ python deploy.py <Bento_bundle_path> <Deployment_name> <Config_JSON default is ec2_config.json>
```

Example:
```bash
$ MY_BUNDLE_PATH=${bentoml get IrisClassifier:latest --print-location -q)
$ python deploy.py $MY_BUNDLE_PATH my_first_deployment ec2_config.json
```

Use Python API
```python
from deploy import deploy_to_azure

deploy_to_azure(BENTO_BUNDLE_PATH, DEPLOYMENT_NAME, CONFIG_JSON)
```


#### Available configuration options for EC2 deployments

* `location`: Azure function location for deployment.
* `min_instances`: The number of workers for the app.
* `max_burst`: The maximum number of elastic workers for the app
* `premium_plan_sku`: The SKU of the app service plan. Allowed values: EP1, EP2, EP3. See the link for more info: https://docs.microsoft.com/en-us/azure/azure-functions/functions-premium-plan
* `function_auth_level`: The authentication level for the function. Allowed values: anonymous, function, admin. See link for more info: # https://docs.microsoft.com/en-us/java/api/com.microsoft.azure.functions.annotation.httptrigger.authlevel?view=azure-java-stable
* `acr_sku`: The SKU of the container registry.  Allowed values: Basic, Classic, Premium, Standard. Default is `Standard`


### Update a deployment

Use command line
```bash
$ python update.py <Bento_bundle_path> <Deployment_name> <Config_JSON>
```

Use Python API
```python
from update import update_azure
update_azure(BENTO_BUNDLE_PATH, DEPLOYMENT_NAME, CONFIG_JSON)
```

### Get deployment's status and information

Use command line
```bash
$ python describe.py <Deployment_name> <Config_JSON>
```


Use Python API
```python
from describe import describe_azure
describe_azure(DEPLOYMENT_NAME)
```

### Delete deployment

Use command line
```bash
$ python delete.py <Deployment_name> <Config_JSON>
```

Use Python API
```python
from  delete import delete_azure
delete_azure(DEPLOYMENT_NAME)
```
