import sys
import os
import argparse
from rich.pretty import pprint

from utils import run_shell_command

from azurefunctions import generate_resource_names



def delete(deployment_name):
    print(f"Deleting {deployment_name}"
    resource_group_name, _, _, _, _ = generate_resource_names(deployment_name)
    run_shell_command(["az", "group", "delete", "-y", "--name", resource_group_name])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='delete',
        description="Delete the bentoml bundle on Azure Functions",
        epilog="Check out https://github.com/bentoml/azure-functions-deploy/blob/main/README.md to know more",
    )


    parser.add_argument(
        "deployment_name", help="Name of the App to be deleted"
    )

    args = parser.parse_args()

    delete(args.deployment_name)

    pprint(f"Deleted {args.deployment_name}!")
