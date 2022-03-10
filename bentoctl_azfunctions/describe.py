from .utils import run_shell_command
from .azurefunctions import generate_resource_names


def describe(deployment_name, deployment_spec=None):
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
