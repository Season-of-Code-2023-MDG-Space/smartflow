import os
from src.authenticate import authenticate_user
import json
from github import Github
import requests
import sys

# Getting the access token
if 'access_token.json' not in os.listdir("./src"):
    authenticate_user()

with open(os.path.normpath('./src/access_token.json'), 'r') as file:
    access_token = json.load(file)['access_token']

if len(sys.argv) != 3:
    usage = '''
    Usage : python3 main.py <project_name> <framework>
    Currently supported frameworks -->
    * React.js
    '''
    print(usage)
    
else: 
    g = Github(access_token)
    project_name, framework = sys.argv[1:]

    if framework.lower().startswith('react'):
        with open(os.path.normpath('./templateConfig.json'), 'r') as configFile:
            repo_link = json.load(configFile)['react']
    
        repo = g.get_repo(repo_link)
        contents = repo.get_contents("")

        while contents:
            
            # Listing out all the structure of the template.
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
                
            else:
                path = os.path.join(project_name, file_content.path)

                if not os.path.exists(os.path.dirname(path)): # Making the required folders
                    os.makedirs(os.path.dirname(path))
                    
                res = requests.get(file_content.download_url) # Saving the files
                with open(path, 'wb') as f:
                    f.write(res.content)
                
                print(f"\u2705 {path}")
                
        print("\nGood to Go!\n")
    else: 
        print("Support coming soon... \N{smiling face with halo}")
        

