import os

from .azurefunctions import (
    generate_azure_function_deployable,
    generate_resource_names,
    get_docker_login_info,
)
from .utils import (
    get_metadata,
    run_shell_command,
    build_docker_image,
    push_docker_image_to_repository,
    set_cors_settings,
    console,
)


def deploy(bento_path, deployment_name, deployment_spec):
    bento_metadata = get_metadata(bento_path)
    bento_tag = bento_metadata['tag']

    deployable_path = os.path.join(
        os.path.curdir,
        f"{bento_tag.name}-{bento_tag.version}-azure-deployable",
    )
    generate_azure_function_deployable(bento_path, deployable_path, deployment_spec)
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
                deployment_spec["location"],
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
                "B1",
                "--min-instances",
                str(deployment_spec["min_instances"]),
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
                "Basic",
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
        f"{acr_name}.azurecr.io/{bento_tag.name}:{bento_tag.version}".lower()
    )

    with console.status("Pushing image"):
        build_docker_image(
            context_path=deployable_path,
            image_tag=docker_image_tag,
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
