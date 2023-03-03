import os
from src.authenticate import authenticate_user
import json
from github import Github
import requests
import sys
import re

def SubstituteNameAndVersion(string, bin=False):
    '''
    Substitutes the project name and project's version
    in the string given.
    ------
    Parameters:
    1. string: The content where the variables need to be substituted.
    2. bin: If the provided data is in bytes. It's False by default.
    '''
    if bin:
        string = string.replace(b"__project_name__", bytes(project_name, encoding='utf-8'))
        string = string.replace(b"__project_version__", bytes(version, encoding='utf-8'))
    else:
        string = re.sub(r'__project_name__', project_name, string)
        string = re.sub(r'__project_version__', version, string)
    return string

# Getting the access token
if 'access_token.json' not in os.listdir("./src"):
    authenticate_user()

with open(os.path.normpath('./src/access_token.json'), 'r') as file:
    access_token = json.load(file)['access_token']

if len(sys.argv) != 4:
    usage = '''
    Usage : python3 main.py <project_name> <project_version> <template_link>
    '''
    print(usage)
    
else: 
    g = Github(access_token)
    project_name, version, template_link = sys.argv[1:]
    template = re.findall(r"https://github\.com/(.*)", template_link)[0]
    
    repo = g.get_repo(template)
    contents = repo.get_contents("")
          
    while contents:
        
        # Listing out all the structure of the template.
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        
        else:
            path = os.path.join(project_name, file_content.path)
            path = SubstituteNameAndVersion(path) # Substituting name and version in file names.

            # Making required folders
            if not os.path.exists(os.path.dirname(path)): 
                os.makedirs(os.path.dirname(path))
            
            res = requests.get(file_content.download_url)
            with open(path, 'wb+') as f:
                # Writing the substituted content onto the file
                f.write(SubstituteNameAndVersion(res.content, bin=True)) 
                
            print(f"\u2705 {path}")
            
    print("\nGood to Go!\n")
            