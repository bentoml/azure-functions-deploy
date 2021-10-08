import os
import argparse

from bentoml.saved_bundle import load_bento_service_metadata
from bentoml.configuration import LAST_PYPI_RELEASE_VERSION

from azurefunctions import (
    generate_azure_function_deployable,
    generate_resource_names,
    get_docker_login_info,
)
from utils import (
    get_configuration_value,
    run_shell_command,
    build_docker_image,
    push_docker_image_to_repository,
    set_cors_settings,
    console,
)


def deploy(bento_bundle_path, deployment_name, config_json):
    bento_metadata = load_bento_service_metadata(bento_bundle_path)

    azure_config = get_configuration_value(config_json)
    deployable_path = os.path.join(
        os.path.curdir,
        f"{bento_metadata.name}-{bento_metadata.version}-azure-deployable",
    )
    generate_azure_function_deployable(bento_bundle_path, deployable_path, azure_config)
    (
        resource_group_name,
        storage_account_name,
        function_plan_name,
        function_name,
        acr_name,
    ) = generate_resource_names(deployment_name)
    console.print("Created Azure function deployable")

    with console.status("Creating resources in Azure"):
        run_shell_command(
            [
                "az",
                "group",
                "create",
                "--name",
                resource_group_name,
                "--location",
                azure_config["location"],
            ]
        )
        console.print(f"Created Azure resource group [b]{resource_group_name}[/b]")

        run_shell_command(
            [
                "az",
                "storage",
                "account",
                "create",
                "--name",
                storage_account_name,
                "--resource-group",
                resource_group_name,
            ]
        )
        console.print(f"Created Azure storage account [b]{storage_account_name}[/b]")

        run_shell_command(
            [
                "az",
                "functionapp",
                "plan",
                "create",
                "--name",
                function_plan_name,
                "--resource-group",
                resource_group_name,
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
        console.print(f"Created Azure function plan [b]{function_plan_name}[/b]")

        run_shell_command(
            [
                "az",
                "acr",
                "create",
                "--name",
                acr_name,
                "--sku",
                azure_config["acr_sku"],
                "--resource-group",
                resource_group_name,
            ]
        )

        # build and push docker
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
        console.print(f"Created Azure ACR [b]{acr_name}[/b]")

    docker_image_tag = (
        f"{acr_name}.azurecr.io/{bento_metadata.name}:{bento_metadata.version}".lower()
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
            resource_group_name, acr_name
        )
        run_shell_command(
            [
                "az",
                "functionapp",
                "create",
                "--name",
                function_name,
                "--storage-account",
                storage_account_name,
                "--resource-group",
                resource_group_name,
                "--plan",
                function_plan_name,
                "--functions-version",
                "3",
                "--deployment-container-image-name",
                docker_image_tag,
                "--docker-registry-server-user",
                docker_username,
                "--docker-registry-server-password",
                docker_password,
            ]
        )
    console.print(f"Deployed in Azure function [b]{function_name}[/b]")
    set_cors_settings(function_name, resource_group_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="deploy",
        description="Deploy the bentoml bundle on Azure Functions",
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
    deploy(args.bento_bundle_path, args.deployment_name, args.config_json)
    console.print("[bold green]Deployment complete![/]")
