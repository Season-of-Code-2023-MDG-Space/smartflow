import os
from src.authenticate import authenticate_user
import json
from github import Github
import requests
import sys
import re
import argparse


def SubstituteNameAndVersion(string, bin=False):
    """
    Substitutes the project name and project's version
    in the string given.
    ------
    Parameters:
    1. string: The content where the variables need to be substituted.
    2. bin: If the provided data is in bytes. It's False by default.
    """
    global project_name, version, proj_name_var, proj_version_var
    if bin:
        string = string.replace(
            bytes(proj_name_var, encoding="utf-8"), bytes(project_name, encoding="utf-8")
        )
        if version:
            string = string.replace(
                bytes(proj_version_var, encoding="utf-8"), bytes(version, encoding="utf-8")
            )
    else:
        string = re.sub(proj_name_var, project_name, string)
        if version:
            string = re.sub(proj_version_var, version, string)
    return string


if __name__ == "__main__":
    # Initializing argument parser for commandline arguments
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-n", "--name", required=True, help="name of the new project")
    argParser.add_argument("-t", "--template", required=True, help="github link of the template for the project")
    argParser.add_argument("-v", "--version", help="version of the project", default=None)
    argParser.add_argument(
        "-projnamevar",
        help="variable referring to the project's name to be changed dynamically in the files and folders",
        default="__project_name__"
    )
    argParser.add_argument(
        "-projversvar",
        help="variable referring to the project's version to be changed dynamically in the files and folders",
        default="__project_version__"
    )
    args = vars(argParser.parse_args())

    # Getting the access token
    if "access_token.json" not in os.listdir("./src"):
        print("\033[1mGetting you access to GitHub API...\033[0m")
        authenticate_user()

    with open(os.path.normpath("./src/access_token.json"), "r") as file:
        access_token = json.load(file)["access_token"]

    g = Github(access_token)
    project_name, template_link, version, proj_name_var, proj_version_var = args.values()

    try:
        template = re.findall(r"https://github\.com/(.*)", template_link)[0]
    except IndexError:
        print("\033[1mPlease provide a valid GitHub repo url.\033[0m")

    repo = g.get_repo(template)
    contents = repo.get_contents("")

    while contents:
        # Listing out all the structure of the template.
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))

        else:
            path = os.path.join(project_name, file_content.path)
            # Substituting name and version in file names.
            path = SubstituteNameAndVersion(path)

            # Making required folders
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

            res = requests.get(file_content.download_url)
            with open(path, "wb+") as f:
                # Writing the substituted content onto the file
                f.write(SubstituteNameAndVersion(res.content, bin=True))

            print(f"\u2705 {path}")

    print("\nGood to Go!\n")
