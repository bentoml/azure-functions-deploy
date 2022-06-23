from __future__ import annotations

import os
import shutil
from pathlib import Path
from sys import version_info
from typing import Any

from attr import asdict

if version_info >= (3, 8):
    from shutil import copytree
else:
    from backports.shutil_copytree import copytree

from bentoml._internal.bento.bento import BentoInfo
from bentoml._internal.bento.build_config import DockerOptions
from bentoml._internal.bento.gen import generate_dockerfile

root_dir = Path(os.path.abspath(os.path.dirname(__file__)), "azurefunctions")

HOST_JSON_PATH = os.path.join(root_dir, "host.json")
LOCAL_SETTINGS_PATH = os.path.join(root_dir, "local.settings.json")
TEMPLATE_PATH = os.path.join(root_dir, "template.j2")
APP_INIT_PATH = os.path.join(root_dir, "app_init.py")
FUNCTION_JSON_PATH = os.path.join(root_dir, "function.json")


# NOTE: map to bentoml supported python version: 3.7 -> 3.10
AZURE_FUNCTIONS_DOCKER_PYTHON_VERSION_MAPPING = {
    "3.7": "mcr.microsoft.com/azure-functions/python:3.0-python3.7",
    "3.8": "mcr.microsoft.com/azure-functions/python:4-python3.8",
    "3.9": "mcr.microsoft.com/azure-functions/python:4-python3.9",
    "3.10": "mcr.microsoft.com/azure-functions/python:4-python3.10",
}

AZURE_ENV = {
    "AzureWebJobsScriptRoot": "/home/site/wwwroot",
    "AzureFunctionsJobHost__Logging__Console__IsEnabled": "true",
}


def create_deployable(
    bento_path: str,
    destination_dir: str,
    bento_metadata: dict[str, Any],
    overwrite_deployable: bool,
) -> str:
    """
    The deployable is the bento along with all the modifications (if any)
    requried to deploy to the cloud service.

    Parameters
    ----------
    bento_path: str
        Path to the bento from the bento store.
    destination_dir: str
        directory to create the deployable into.
    bento_metadata: dict
        metadata about the bento.

    Returns
    -------
    dockerfile_path : str
        path to the dockerfile.
    docker_context_path : str
        path to the docker context.
    additional_build_args : dict
        Any addition build arguments that need to be passed to the
        docker build command
    """
    deployable_path = Path(destination_dir)

    # copy over the bento bundle
    copytree(bento_path, deployable_path, dirs_exist_ok=True)
    # Dockerfile
    bento_metafile = Path(bento_path, "bento.yaml")
    with bento_metafile.open("r", encoding="utf-8") as metafile:
        info = BentoInfo.from_yaml_file(metafile)

    options = bentoml_cattr.unstructure(info.docker)
    options["dockerfile_template"] = TEMPLATE_PATH
    options["base_image"] = AZURE_FUNCTIONS_DOCKER_PYTHON_VERSION_MAPPING[
        options["python_version"]
    ]
    if "env" in options and options["env"] is not None:
        options["env"] = AZURE_ENV.update(options["env"])
    else:
        options["env"] = AZURE_ENV

    dockerfile_path = deployable_path.joinpath("env", "docker", "Dockerfile")
    with dockerfile_path.open("w", encoding="utf-8") as dockerfile:
        dockerfile.write(
            generate_dockerfile(
                DockerOptions(**options).with_defaults(),
                str(deployable_path),
                use_conda=any(
                    i is not None
                    for i in bentoml_cattr.unstructure(info.conda).values()
                ),
            )
        )

    # host.json file
    shutil.copy(HOST_JSON_PATH, deployable_path)
    # local.settings.json file
    shutil.copy(LOCAL_SETTINGS_PATH, deployable_path)

    app_module_path = deployable_path.joinpath("app")
    app_module_path.mkdir(exist_ok=True)
    shutil.copy(APP_INIT_PATH, os.path.join(app_module_path, "__init__.py"))
    shutil.copy(FUNCTION_JSON_PATH, app_module_path)

    return str(deployable_path)
