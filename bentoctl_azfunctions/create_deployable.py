import os
import shutil

root_dir = os.path.join(os.path.dirname(__file__), "azurefunctions")
HOST_JSON_FILE = os.path.join(root_dir, "host.json")
LOCAL_SETTINGS_FILE = os.path.join(root_dir, "local.settings.json")
DOCKERFILE_TEMPLATE = os.path.join(root_dir, "Dockerfile")
APP_INIT_FILE = os.path.join(root_dir, "app_init.py")
FUNCTION_JSON_FILE = os.path.join(root_dir, "function.json")


def generate_dockerfile_in(deployable_path, bento_metadata):
    dockerfile_path = os.path.join(deployable_path, "Dockerfile")
    with open(DOCKERFILE_TEMPLATE, "r") as template_file, open(
        dockerfile_path, "w"
    ) as dockerfile:
        template = template_file.read()
        dockerfile.write(
            template.format(
                bentoml_version=bento_metadata["bentoml_version"],
                python_version=bento_metadata["python_version"],
            )
        )

    return dockerfile_path


def generate_function_app_module_in(deployable_path):
    """
    Make an app module that stores the azure function app which will
    load our service and when a request arrives, uses bentoml's ASGI Middleware
    to serve the response.
    """
    app_module_path = os.path.join(deployable_path, "app")
    os.mkdir(app_module_path)
    shutil.copy(APP_INIT_FILE, os.path.join(app_module_path, "__init__.py"))
    shutil.copy(FUNCTION_JSON_FILE, app_module_path)


def create_deployable(
    bento_path: str,
    destination_dir: str,
    bento_metadata: dict,
    overwrite_deployable=None,
):
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
    deployable_path = os.path.join(destination_dir, "bentoctl_deployable")
    docker_context_path = deployable_path

    # copy over the bento bundle
    shutil.copytree(bento_path, deployable_path)
    # Dockerfile
    dockerfile_path = generate_dockerfile_in(deployable_path, bento_metadata)
    # host.json file
    shutil.copy(HOST_JSON_FILE, deployable_path)
    # local.settings.json file
    shutil.copy(LOCAL_SETTINGS_FILE, deployable_path)
    generate_function_app_module_in(deployable_path)

    additional_build_args = None
    return dockerfile_path, docker_context_path, additional_build_args
