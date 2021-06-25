import json
import sys

from utils import run_shell_command
from azure import generate_resource_names


def describe_azure(deployment_name):
    (resource_group_name, _, _, _, function_name,) = generate_resource_names(
        deployment_name
    )
    show_function_result = run_shell_command(
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
        "defaultHostName",
        "enabledHostNames",
        "hostNames",
        "id",
        "kind",
        "lastModifiedTimeUtc",
        "location",
        "name",
        "repositorySiteName",
        "reserved",
        "resourceGroup",
        "state",
        "type",
        "usageState",
    ]
    info_json = {k: v for k, v in show_function_result.items() if k in keys}
    print(json.dumps(info_json, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise Exception("Please provide deployment_name")
    deployment_name = sys.argv[1]

    describe_azure(deployment_name)
