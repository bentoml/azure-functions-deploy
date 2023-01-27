import argparse
import os

from azurefunctions.utils import run_shell_command, get_configuration_value
from rich.pretty import pprint


def describe(function_name: str, config_json: str):
    azure_config = get_configuration_value(config_json)

    show_function_result, _ = run_shell_command(
        [
            "az",
            "functionapp",
            "show",
            "--name",
            function_name,
            "--resource-group",
            azure_config["resource_group"],
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


def main():
    parser = argparse.ArgumentParser(
        prog="describe",
        description="Describe the Azure Function deployment you made.",
        epilog="Check out https://github.com/bentoml/azure-functions-deploy/"
               "blob/main/README.md to know more",
    )
    parser.add_argument(
        "function_name", help="The name of new Azure function you want to deploy."
    )
    parser.add_argument(
        "config_json",
        help="(optional) The config file for your deployment. Default azure_config.json",
        default=os.path.join(os.getcwd(), "azure_config.json"),
        nargs="?",
    )

    args = parser.parse_args()
    info_json = describe(function_name=args.function_name, config_json=args.config_json)
    pprint(info_json)


if __name__ == "__main__":
    main()
