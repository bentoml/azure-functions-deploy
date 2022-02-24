OPERATOR_NAME = "azure-functions"

OPERATOR_MODULE_DIR = "bentoctl_azfunctions"

# BentoML deployment tool use Cerberus to validate the input.
OPERATOR_SCHEMA = {
    "resource_group": {
        "type": "string",
        "required": True,
        "help_message": "Resource group into which the resources have to be created.",
    },
    "acr_name": {
        "type": "string",
        "required": True,
        "help_message": "The name of Azure Container Registry to use to store images.",
    },
    "location": {
        "type": "string",
        "required": True,
        "help_message": "Azure region or location that you want to deploy to. By default it will use the same one as your resource group",
    },
    "min_instances": {
        "type": "integer",
        "default": 1,
        "coerce": int,
        "help_message": "The number of workers for the app.",
    },
    "max_burst": {
        "type": "integer",
        "default": 2,
        "coerce": int,
        "help_message": "The maximum number of elastic workers for the app",
    },
    "premiume_plan_sku": {
        "type": "string",
        "default": "EP1",
        "help_message": "The SKU of the app service plan. Allowed values: EP1, EP2, EP3.",
        "allowed": ["EP1", "EP2", "EP3"],
    },
    "function_auth_level": {
        "type": "string",
        "default": "anonymous",
        "help_message": "The authentication level for the function. Allowed values: anonymous, function, admin.",
        "allowed": ["anonymous", "function", "admin"],
    },
}
