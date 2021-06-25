import os
import sys
from bentoml.saved_bundle import load_bento_service_metadata
from bentoml.yatai.deployment.azure_functions.operator import _set_cors_settings
from bentoml.configuration import LAST_PYPI_RELEASE_VERSION

from azure import (
    generate_azure_function_deployable,
    generate_resource_names,
    get_docker_login_info,
)
from utils import (
    get_configuration_value,
    run_shell_command,
    build_docker_image,
    push_docker_image_to_repository,
)


def deploy_to_azure(bento_bundle_path, deployment_name, config_json):
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
        acr_name,
        function_name,
    ) = generate_resource_names(deployment_name)

    print(f"Creating Azure resource group {resource_group_name}")
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
    print(f"Creating Azure storage account {storage_account_name}")
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
    print(f"Creating Azure function plan {function_plan_name}")
    run_shell_command(
        [
            "az",
            "functionapp",
            "plan",
            "create",
            "--name",
            function_plan_name,
            "--is-linux",
            "--sku",
            azure_config["premium_plan_sku"],
            "--min-instances",
            azure_config["min_instances"],
            "--max-burst",
        ]
    )
    print(f"Creating Azure ACR {acr_name}")
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

    print(f"Deploying Azure function {function_name}")
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
    _set_cors_settings(function_name, resource_group_name)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise Exception(
            "Please provide bento_bundle_path deployment_name and configuration json"
        )
    bento_bundle_path = sys.argv[1]
    deployment_name = sys.argv[2]
    config_json = sys.argv[3] if sys.argv[3] else "ec2_config.json"

    deploy_to_azure(bento_bundle_path, deployment_name, config_json)
