# SmartFlow
Are you spending a lot of time writing boilerplate code to start with a project in your organization?

Or going through large readmes or guides just for setting up a codebase?

Introducing ***SmartFlow*** - **a full fledged CLI solution!**
<!-- It's a full-fledged CLI tool, bundled with these features:
- ```flow-create``` Replicates the exact structure of the specified template repository, and can substitute the variables of project's name and version.
- ```flow-setup``` It's a readme parser and can setup in any readme obeying certain standards. -->

# Installation
1. Download the source zip file.
2. Install it via pip.
   ```
   pip install <name_of_zip_file>.zip
   ```
---
# Features
After installation, you will be able to run `flow-create` and `flow-setup` commands.
<br><br>

## `flow-create`
```
$ flow-create --help
usage: flow-create [-h] -n NAME -t TEMPLATE [-v VERSION] [--s] [-projnamevar PROJNAMEVAR] [-projversvar PROJVERSVAR]

options:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  name of the new project
  -t TEMPLATE, --template TEMPLATE
                        github link of the template for the project
  -v VERSION, --version VERSION
                        version of the project, default: None
  --s, --substitute     Specify if there are variables to be replaced
  -projnamevar PROJNAMEVAR
                        variable referring to the project's name to be changed dynamically in the files and folders, default: "__project_name__"
  -projversvar PROJVERSVAR
                        variable referring to the project's version to be changed dynamically in the files and folders, default: "__project_version__"
```
> **Name of the project and template github link are required arguments.**

### What does it do?
Let's take an example.

Suppose you are a part of an organization.  
You need to have a team mate already access the company's database, and some boilerplate code before starting off a new project.

And he/she has to again and again write the boilerplate commands and make files/folders just to have access to the default features. For every new project.

Isn't it repetitive?

Here comes the `flow-create` command that automates this job for you!

Build a template once, and anyone can clone it along with the feature to dynamically change the name and version, in the file names and its content too!
<br>

### How to use it?
1. First, you will have to be authenticated to access the Github API. 
2. Name and template github link are required.
3. You can specify if there are variables to be substitued by the flag `-s` or `--substitute`
4. Default variables for:
   - project-name: `__project_name__`
   - project-version: `__project_version__`
5. All the files would be stored in a new folder of the project name specified.

You can checkout a sample template [here](https://github.com/vrag99/sampleProjectTemplate).
<br>
<br>
## ```flow-setup```