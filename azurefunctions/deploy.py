import os
import argparse

from bentoml.saved_bundle import load_bento_service_metadata
from bentoml.configuration import LAST_PYPI_RELEASE_VERSION

from azurefunctions.azure_utils import (
    generate_azure_function_deployable,
    get_docker_login_info,
)
from azurefunctions.utils import (
    get_configuration_value,
    validate_name,
    run_shell_command,
    build_docker_image,
    push_docker_image_to_repository,
    set_cors_settings,
    console,
    get_bundle_path
)


def deploy(bento_service_name: str, new_function_name: str, config_json: str) -> None:
    bento_bundle_path = get_bundle_path(bento_service_name=bento_service_name)
    bento_metadata = load_bento_service_metadata(bento_bundle_path)

    azure_config = get_configuration_value(config_json)
    deployable_path = os.path.join(
        os.path.curdir,
        f".cache/{bento_metadata.name}-{bento_metadata.version}-azure-deployable",
    )
    generate_azure_function_deployable(bento_bundle_path, deployable_path, azure_config)
    console.print("Created Azure function deployable")

    with console.status("Creating resources in Azure"):
        if run_shell_command(
                [
                    "az",
                    "group",
                    "exists",
                    "--name",
                    azure_config["resource_group"],
                ]
        )[0]:
            console.print(f'Azure resource group [b]{azure_config["resource_group"]}[/b]')
        else:
            run_shell_command(
                [
                    "az",
                    "group",
                    "create",
                    "--name",
                    azure_config["resource_group"],
                    "--location",
                    azure_config["location"],
                ]
            )
            console.print(f'Created Azure resource group [b]{"resource_group"}[/b]')

        run_shell_command(
            [
                "az",
                "storage",
                "account",
                "create",
                "--name",
                azure_config["storage_account"],
                "--resource-group",
                azure_config["resource_group"],
            ]
        )
        console.print(f'Created Azure storage account [b]{azure_config["storage_account"]}[/b]')

        run_shell_command(
            [
                "az",
                "functionapp",
                "plan",
                "create",
                "--name",
                azure_config["app_service_plan"],
                "--resource-group",
                azure_config["resource_group"],
                "--is-linux",
                "--sku",
                azure_config["function_sku"],
                "--min-instances",
                str(azure_config["min_instances"]),
                # Only for EP plans
                # "--max-burst",
                # str(azure_config["max_burst"]),
            ]
        )
        console.print(f'Created Azure function plan [b]{azure_config["app_service_plan"]}[/b]')

        run_shell_command(
            [
                "az",
                "acr",
                "create",
                "--name",
                azure_config["container_registry"],
                "--sku",
                azure_config["acr_sku"],
                "--resource-group",
                azure_config["resource_group"],
            ]
        )
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
        console.print(f'Created Azure ACR [b]{azure_config["container_registry"]}[/b]')

    # build and push docker
    docker_image_tag = (
        f'{azure_config["container_registry"]}.azurecr.io/{bento_metadata.name}:{bento_metadata.version}'.lower()
    )

    major, minor, _ = bento_metadata.env.python_version.split(".")

    with console.status("Pushing image"):
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
    console.print(f"Pushed image {docker_image_tag}")

    with console.status("Deploying image in Azure functions"):
        docker_username, docker_password = get_docker_login_info(
            azure_config["resource_group"], azure_config["container_registry"]
        )
        new_function_name = validate_name(new_function_name)
        run_shell_command(
            [
                "az",
                "functionapp",
                "create",
                "--name",
                new_function_name,
                "--storage-account",
                azure_config["storage_account"],
                "--resource-group",
                azure_config["resource_group"],
                "--plan",
                azure_config["app_service_plan"],
                "--functions-version",
                str(azure_config["azure_functions_version"]),
                "--deployment-container-image-name",
                docker_image_tag,
                "--docker-registry-server-user",
                docker_username,
                "--docker-registry-server-password",
                docker_password,
            ]
        )
    console.print(f"Deployed in Azure function [b]{new_function_name}[/b]")
    set_cors_settings(new_function_name, azure_config["resource_group"])


def main():
    parser = argparse.ArgumentParser(
        prog="deploy",
        description="Deploy the bentoml bundle on Azure Functions",
        epilog="Check out https://github.com/bentoml/azure-functions-deploy/blob/main/README.md to know more",
    )
    parser.add_argument(
        "bento_service_name", help="The name of Bento service you want to deploy eq. [PytorchService:latest]"
    )
    parser.add_argument(
        "new_function_name", help="The name of new Azure function you want to deploy."
    )
    parser.add_argument(
        "config_json",
        help="(optional) The config file for your deployment. Default azure_config.json",
        default=os.path.join(os.getcwd(), "azure_config.json"),
        nargs="?",
    )
    args = parser.parse_args()

    deploy(bento_service_name=args.bento_service_name, new_function_name=args.new_function_name,
           config_json=args.config_json)
    console.print("[bold green]Deployment complete![/]")


if __name__ == "__main__":
    main()
