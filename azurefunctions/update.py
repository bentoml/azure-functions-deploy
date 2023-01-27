import os
import argparse

from bentoml.saved_bundle import load_bento_service_metadata
from bentoml.configuration import LAST_PYPI_RELEASE_VERSION

from azurefunctions.utils import (
    get_configuration_value,
    run_shell_command,
    build_docker_image,
    push_docker_image_to_repository,
    console, get_bundle_path,
)

from azurefunctions.azure_utils import generate_azure_function_deployable


def update(bento_service_name, function_name, config_json):
    bento_bundle_path = get_bundle_path(bento_service_name=bento_service_name)
    bento_metadata = load_bento_service_metadata(bento_bundle_path)

    azure_config = get_configuration_value(config_json)
    deployable_path = os.path.join(
        os.path.curdir,
        f"{bento_metadata.name}-{bento_metadata.version}-azure-deployable",
    )
    generate_azure_function_deployable(bento_bundle_path, deployable_path, azure_config)

    run_shell_command(
        [
            "az",
            "acr",
            "login",
            "--name",
            azure_config["container_registry"],
            "--resource-group",
            azure_config["resource_group"],
        ]
    )
    docker_image_tag = (
        f'{azure_config["container_registry"]}.azurecr.io/{bento_metadata.name}:{bento_metadata.version}'.lower()
    )
    with console.status("Building and Pushing image"):
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
    console.print(f"Built and pushed image {docker_image_tag}")

    with console.status("Updating Azure function"):
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
                azure_config["resource_group"],
                "--docker-custom-image-name",
                docker_image_tag,
            ]
        )
    console.print(f"Updated Azure function [b]{function_name}[/b]")


def main():
    parser = argparse.ArgumentParser(
        prog="update",
        description="Update bentoml bundle on Azure Functions",
        epilog="Check out https://github.com/bentoml/azure-functions-deploy/"
               "blob/main/README.md to know more",
    )
    parser.add_argument(
        "bento_service_name", help="The name of Bento service you want to deploy eq. [PytorchService:latest]"
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

    update(args.bento_service_name, args.function_name, args.config_json)

    console.print(f"[bold green]{args.function_name} update complete![/]")


if __name__ == "__main__":
    main()
