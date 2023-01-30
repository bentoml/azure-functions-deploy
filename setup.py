from setuptools import setup

setup(
    name='bento_azure_function',
    version="0.3",

    author='michal.wojdylak',
    author_email='michal.wojdylak@wundermanthompson.com',

    install_requires=[
        "bentoml==0.13.2",
        "azure-functions",
        "flask",
        "docker",
        "pandas",
        "rich",
        "numpy",
        "pillow",
    ],
    include_package_data=True,
    data_files=[('azurefunctions', [
        'azurefunctions/host.json',
        'azurefunctions/local.settings.json',
        'azurefunctions/Dokcerfile'
    ])],
    entry_points={
        'console_scripts': [
            'deploy_function=azurefunctions.deploy:main',
            'describe_function=azurefunctions.describe:main',
            'update_function=azurefunctions.update:main',
        ]
    }
)
