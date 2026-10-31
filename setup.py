from setuptools import setup, find_packages

setup(
    name="trustmesh",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    entry_points={
        "console_scripts": [
            "trustmesh = trustmesh.cli:main",
        ],
    },
)
