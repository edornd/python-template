import os
from datetime import datetime

import toml

DEFAULT_PY_VERSION = ">=3.10"
DEFAULT_DEPS_DEV = {
    "black": ">= 23.0.0, 24",
    "ruff": ">= 0.1.0, < 1",
    "isort": ">= 5.0.0, < 6",
}
DEFAULT_DEPS_DOC = {
    "mkdocs-material": ">= 9.2.0, < 10",
    "mdx-include": ">= 1.3.0, < 2",
}
DEFAULT_DEPS_TEST = {
    "pytest": ">= 7.4.0, < 8",
    "pytest-cov": ">= 4.1.0, < 5",
    "coverage": ">= 7.3.0, < 8",
}


def query_params(validate: bool = True):
    """
    Query the user for the project parameters.
    """
    while True:
        while not (name := input("What is your name? ")):
            print("Please enter your name, or press Ctrl+C to exit.")

        while not (email := input("What is your email address? ")):
            print("Please enter your email address, or press Ctrl+C to exit.")

        while not (project_name := input("What should we call your project? ")):
            print("Please enter a project name, or press Ctrl+C to exit.")

        while not (project_description := input("What is your project about? ")):
            print("Please enter a project description, or press Ctrl+C to exit.")

        py_version = (
            input(f"What version of Python do you want to use? (default: {DEFAULT_PY_VERSION}) ") or DEFAULT_PY_VERSION
        )

        if validate:
            print("So far, we have:")
            print(f" - Author: {name} <{email}>")
            print(f" - Project name: {project_name}")
            print(f" - Project description: {project_description}")
            print(f" - Python version: {py_version}")
            if input("Is this correct? (y/n) ").lower() != "y":
                print("Understood, let's try again.")
                continue
        return name, email, project_name, project_description, py_version


def query_dependencies(scope: str = "runtime"):
    """
    Query the user for the project dependencies.
    """
    deps = {}

    while True:
        if input(f"Add {scope} dependencies? (y/n) ").lower() != "y":
            break
        try:
            print("Please enter the dependencies you want to add.")
            print("Press Ctrl+C to leave empty and move on.")
            while not (dep := input("Add a dependency (e.g. requests): ")):
                print("Please enter a dependency, or press Ctrl+C to exit.")
            while not (version := input(f"Version of {dep} (default: empty): ") or ""):
                print("Please enter a version, or press Ctrl+C to exit.")
            print("Added!")
            if input("Add another dependency? (y/n) ").lower() != "y":
                break
            deps[dep] = version
        except KeyboardInterrupt:
            deps = {}
            break
    print("Understood, let's move on.")
    return deps


def rename_project(project_name: str):
    """
    Rename the project by recursively replacing the string "project_name" with the project name.
    """
    for path in os.listdir("."):
        if os.path.isdir(path):
            rename_project(path)
        elif os.path.isfile(path):
            with open(path) as f:
                data = f.read()
            with open(path, "w") as f:
                f.write(data.replace("project_name", project_name))


def update_license(name: str):
    """
    Replace the <year> and <name> placeholders in the LICENSE file with the actual values.
    At the moment the license is hardcoded to MIT.
    """
    with open("LICENSE") as f:
        data = f.read()
    data = data.replace("<year>", str(datetime.now().year))
    data = data.replace("<name>", name)
    with open("LICENSE", "w") as f:
        f.write(data)


def main():
    try:
        with open("pyproject.toml") as f:
            data = toml.load(f)
    except FileNotFoundError:
        print("No pyproject.toml found, exiting.")
        exit(1)

    try:
        print("Hi! Let's get started.")
        print("Please answer the following questions to help us get you set up.")
        name, email, project_name, project_description, py_version = query_params()
        data["project"]["authors"] = [{"name": name, "email": email}]
        data["project"]["name"] = project_name
        data["project"]["description"] = project_description
        data["project"]["python"] = py_version

        # runtime dependencies
        dependencies = query_dependencies(scope="runtime")
        data["project"]["dependencies"] = [f'"{dep} {version}"' for dep, version in dependencies.items()]
        # development dependencies
        dependencies = query_dependencies(scope="development")
        data["project"]["optional-dependencies"]["dev"] = [
            f'"{dep} {version}"' for dep, version in dependencies.items()
        ]
        # documentation dependencies
        dependencies = query_dependencies(scope="documentation")
        data["project"]["optional-dependencies"]["doc"] = [
            f'"{dep} {version}"' for dep, version in dependencies.items()
        ]
        # testing dependencies
        dependencies = query_dependencies(scope="testing")
        data["project"]["optional-dependencies"]["test"] = [
            f'"{dep} {version}"' for dep, version in dependencies.items()
        ]

        print("Updating license...")
        update_license(name)

        # storing the updated pyproject.toml
        print("Generating pyproject.toml...")
        with open("pyproject.toml", "w") as f:
            toml.dump(data, f)

        # update package name and dynamic versioning
        print("Renaming project...")
        rename_project(project_name)
        os.rename("src/project_name", f"src/{project_name}")
        data["tool"]["setuptools"]["dynamic"] = f"{project_name}.__version__"

        print("Your project is ready! Deleting myself from existence, farewell!")
        print(__file__)
        # os.remove(__file__)

    except KeyboardInterrupt:
        print("\nExiting.")
        exit(0)


if __name__ == "__main__":
    main()
