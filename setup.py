from setuptools import setup

setup(
    name='ttttttttt',
    version="0.1",

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

    entry_points={
        'console_scripts': [
            'deploy_function=ttttttttt.deploy:main',
            'describe_function=ttttttttt.describe:main',
            'update_function=ttttttttt.update:main',
        ]
    }
)
