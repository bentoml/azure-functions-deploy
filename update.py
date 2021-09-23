import os
import sys
import argparse
from rich.pretty import pprint

from bentoml.saved_bundle import load_bento_service_metadata
from bentoml.configuration import LAST_PYPI_RELEASE_VERSION

from utils import (
    get_configuration_value,
    run_shell_command,
    build_docker_image,
    push_docker_image_to_repository,
)

from azure import generate_azure_function_deployable, generate_resource_names


def update(bento_bundle_path, deployment_name, config_json):
    bento_metadata = load_bento_service_metadata(bento_bundle_path)

    azure_config = get_configuration_value(config_json)
    deployable_path = os.path.join(
        os.path.curdir,
        f"{bento_metadata.name}-{bento_metadata.version}-azure-deployable",
    )
    print("Creating Azure function deployable")
    generate_azure_function_deployable(bento_bundle_path, deployable_path, azure_config)
    (
        resource_group_name,
        storage_account_name,
        function_plan_name,
        function_name,
        acr_name,
    ) = generate_resource_names(deployment_name)

    run_shell_command(
        [
            "az",
            "acr",
            "login",
            "--name",
            acr_name,
            "--resource-group",
            resource_group_name,
        ]
    )
    docker_image_tag = (
        f"{acr_name}.azurecr.io/{bento_metadata.name}:{bento_metadata.version}".lower()
    )
    print(f"Build and push image {docker_image_tag}")
    major, minor, _ = bento_metadata.env.python_version.split(".")
    build_docker_image(
        context_path=deployable_path,
        image_tag=docker_image_tag,
        dockerfile="Dockerfile-azure",
        additional_build_args={
            "BENTOML_VERSION": LAST_PYPI_RELEASE_VERSION,
            "PYTHON_VERSION": major + minor,
        },
    )
    push_docker_image_to_repository(docker_image_tag)
    print(f"Updating Azure function {function_name}")
    run_shell_command(
        [
            "az",
            "functionapp",
            "config",
            "container",
            "set",
            "--name",
            function_name,
            "--resource-group",
            resource_group_name,
            "--docker-custom-image-name",
            docker_image_tag,
        ]
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='deploy',
        description="Update bentoml bundle on Azure Functions",
        epilog="Check out https://github.com/bentoml/azure-functions-deploy/blob/main/README.md to know more",
    )
    parser.add_argument("bento_bundle_path", help="Path to bentoml bundle")
    parser.add_argument(
        "deployment_name", help="The name you want to use for your deployment"
    )
    parser.add_argument(
        "config_json",
        help="(optional) The config file for your deployment",
        default=os.path.join(os.getcwd(), "azure_config.json"),
        nargs="?",
    )
    args = parser.parse_args()

    update(args.bento_bundle_path, args.deployment_name, args.config_json)

    pprint(f"{args.deployment_name} update complete!")
