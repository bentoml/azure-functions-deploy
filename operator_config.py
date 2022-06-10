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
    "premium_plan_sku": {
        "type": "string",
        "default": "P1v2",
        "required": True,
        "help_message": "The SKU of the app service plan. Allowed values: P1v2, P2v2, P3v2",
        "allowed": ["P1v2", "P2v2", "P3v2"],
    },
}

OPERATOR_NAME = "azure-functions"

OPERATOR_MODULE = "bentoctl_azfunctions"

OPERATOR_DEFAULT_TEMPLATE = "terraform"
