# SmartFlow
Are you spending a lot of time writing boilerplate code to start with a project in your organization?

Or going through large readmes or guides just for setting up a codebase?

Introducing ***SmartFlow*** - **a full fledged CLI solution!**

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
You need to have a team mate access the company's database, and write some boilerplate code before starting off a new project.

And he/she has to again and again write the boilerplate commands and make files/folders just to have access to the default features. For every new project.

Isn't it repetitive?

Here comes the `flow-create` command that automates this job for you!

Build a template once, and anyone can clone it along with the feature to dynamically change the name and version, in the file names and its content too!
<br><br>

### How to use it?
1. First, you will have to be authenticated to access the Github API. 
   
2. Name and template github link are required.
   
3. You can specify if there are variables to be substitued by the flag `-s` or `--substitute`
   
4. Default variables for:
   - project-name: `__project_name__`
- 
   - project-version: `__project_version__`
  
1. All the files would be stored in a new folder of the project name specified.

You can checkout a sample template [here](https://github.com/vrag99/sampleProjectTemplate).
<br><br><br>

## `flow-setup`
```
$ flow-setup
```
> No arguments required

### What does it do?

Let's say - a new person joins your organization and needs the code base to be set up.  
It requires quite some time to get them into the workflow.

Plus, if you want to contribute to an ongoing project, you've to set it up which is a hassle in itself.

Here comes the `flow-setup` command that automatically sets up the project for you!

It's a full-fledged readme parser that can set up the project following the instructions from the corresponding readme file.

But there are specific standards for the readme to be obeyed.
<br><br>

### Rules for `README.md`
2 sections are mandatory in the markdown file: **Requirements** and **Setup**  

#### 'Requirements' Section
- All the requirements, say node version, python version etc. will be given here along with relevant code blocks and links.
  
- User will have choice to execute the code blocks and open any links present.
  
- There will be a prompt for confirmation before proceeding to the setup section.

#### 'Setup' Section
- It will have 3 subsections - one each for Windows, Linux and MacOS.
- The parser will detect the current device's OS and move to the corresponding section.
- **The content under each section must strictly be in list form.**

  - *Ordered List* - Represents steps to be followed sequentially. The code blocks will be executed and links opened in the order given.
  - *Unordered List* - Represents choices. You'll be given choices to choose from and the selected code will be executed and links opened.

- There's support for nested list (upto one layer only) :)

Here's a sample [readme](./sampleReadme.md) for parsing.
