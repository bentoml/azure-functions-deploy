import argparse

from utils import run_shell_command
from azurefunctions import generate_resource_names
from rich.pretty import pprint


def describe(deployment_name, azure_config=None):
    (resource_group_name, _, _, function_name, _) = generate_resource_names(
        deployment_name
    )
    show_function_result, _ = run_shell_command(
        [
            "az",
            "functionapp",
            "show",
            "--name",
            function_name,
            "--resource-group",
            resource_group_name,
        ]
    )
    keys = [
        "name",
        "defaultHostName",
        "id",
        "kind",
        "lastModifiedTimeUtc",
        "location",
        "repositorySiteName",
        "reserved",
        "resourceGroup",
        "state",
        "type",
        "usageState",
    ]
    info_json = {k: v for k, v in show_function_result.items() if k in keys}
    return info_json


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="describe",
        description="Describe the Azure Function deployment you made.",
        epilog="Check out https://github.com/bentoml/azure-functions-deploy/"
        "blob/main/README.md to know more",
    )
    parser.add_argument("deployment_name", help="Name of the App to be deleted")

    args = parser.parse_args()
    info_json = describe(args.deployment_name)
    pprint(info_json)
