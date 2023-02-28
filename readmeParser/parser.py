import markdown
from bs4 import BeautifulSoup
import questionary
import sys
import re
import os
import webbrowser
from time import sleep

##### Utilities ######
def GetSection(heading, listForm=False):
    '''
    Gets the content in between of 2 consecutives h2 tags.
    ---
    Parameters:
    1. heading: Heading of the section containing the required content.
    2. listForm: If the elements are required in a list form.
    '''
    section_elements, section_html = [], ""
    for elements in heading.next_siblings:
        if elements.name == 'h2':
            break
        else:
            if listForm:
                if elements!='\n':
                    section_elements.append(elements)
            else:
                section_html += re.sub("\n *","\n",str(elements))
    
    if listForm: return section_elements
    else:
        section_html = BeautifulSoup(section_html, 'html.parser')
        return section_html
                
def ParseCommands(codeHtml) -> list:
    '''
    Parses the commands in a code block into a list.
    '''
    command_list = re.sub('(\n *)|(&& *)', '\n', codeHtml.text).split("\n")
    command_list = [command for command in command_list if command != '']
    return command_list

def ParseLinks(html) -> list:
    '''
    Parses all the links in the html into a list of tuples 
    each having a reference and its corresponding link.
    '''
    return [(link.text, link.get('href')) for link in html.find_all('a')]

def ExecuteCommands(commandList: list):
    '''
    Executes all the commands in commandList.
    '''
    [os.system(command) for command in commandList]

def OpenLinks(parsedlinkList: list):
    '''
    Opens links in a new tab from the parsedlinkList.
    '''
    [webbrowser.open_new_tab(link) for reference, link in parsedlinkList]


##### Main functions ####
def EnsureRequirements(requirementHtml) -> bool:
    '''
    Ensures the requirements are met before moving onto setup.
    '''
    print("\033[1mRequirements include:\033[0m")
    print(requirementHtml.text)
    
    if requirementHtml.find('a'):
        
        links = ParseLinks(requirementHtml)
        
        chosen_links = questionary.checkbox(
            message="A few links found. Which one(s) do you want to open?",
            choices=list([f"{ref} : {link}" for ref, link in links])
        ).ask()
        if chosen_links: #If user has selected atleast 1 choice.
            chosen_links = [string.split(" : ") for string in chosen_links]
            print("Opening links...")
            OpenLinks(chosen_links)
        
    if requirementHtml.find('code'):
        
        command_list = []
        for code_tag in requirementHtml.find_all('code'):
            command_list.extend(ParseCommands(code_tag))
        
        chosen_commands = questionary.checkbox(
            message="A few command blocks found. Which one(s) do you want to execute?",
            choices=command_list
        ).ask()
        if chosen_commands: 
            print("Executing....")
            ExecuteCommands(chosen_commands)

    sleep(1)
    print("\nMake sure the requirements are satisfied :)\n")
    sleep(1)
    return questionary.confirm("Continue with the setup?").ask()
    

def ParseInstructions(htmlList):
    '''
    Segregates the list item code into:
    1. prompt - The instruction.
    2. commands - The snippets to be executed.
    3. links - any files aur docs linked.
    ---
    Parameters:
    htmlList : An ordered or unordered html list, parsed with BeautifulSoup
    '''
    instructions = htmlList.find_all("li")
    parsed_instructions = {}
    for i in range(len(instructions)):
        commands_list = []
        for code_tag in instructions[i].find_all('code'):
            commands_list.extend(ParseCommands(code_tag))
            code_tag.decompose()

        # links = [(link.text, link.get('href')) for link in instructions[i].find_all('a')]
        links = ParseLinks(instructions[i])
        prompt = instructions[i].text.strip()
        
        parsed_instructions[i] = {
            "prompt" : prompt,
            "commands" : commands_list,
            "links" : links
        }
        
    return parsed_instructions


def SetupViaChoices(parsed_choices: dict):
    '''
    Setup described by unordered list indicates choices.
    This takes the parsed instructions and sets up via choices.
    '''
    prompts = [parsed_choices[i]['prompt'] for i in parsed_choices.keys()]
    choice = questionary.select("How do you want to set up?", choices=prompts).ask()
    choice_index = prompts.index(choice)
    commands = parsed_choices[choice_index]['commands']
    links = parsed_choices[choice_index]['links']
    
    if links:
        print(f"The following links will be opened:")
        [print(f"{reference} : {link}") for (reference,link) in links]
        if questionary.confirm("Want to open the links?").ask():
            OpenLinks(links)
            print("\nGood to Go!\n")
            
    if commands:
        print(f"The following commands will be executed:")
        [print(i) for i in commands]
        if questionary.confirm("Want to proceed?").ask():
            ExecuteCommands(commands)
            print("\nGood to Go!\n")
        

def SetupViaSteps(parsed_steps: dict):
    '''
    Setup described by ordered list indicates choices.
    This takes the parsed instructions and sets up via steps.
    '''
    print("The following steps will be followed -->\n")
    for i in parsed_steps.keys():
        prompt, commands, links = parsed_steps[i].values()
        print(f"{i+1}. {prompt}")
        if commands: 
            print(f"Commands to be executed -->")
            [print("  "+i) for i in commands]
        if links: 
            print(f"Links to be opened -->")
            [print(f"  '{reference}' : {link}") for reference, link in links]
        print()
    
    if questionary.confirm('Want to continue?').ask():
        for i in parsed_steps.keys():
            prompt, commands, links = parsed_steps[i].values()
            if commands: ExecuteCommands(commands)
            if links: OpenLinks(links)
    
        print("\nGood to Go! \n")


if __name__ == '__main__':
    
    path_to_readme = questionary.path("Where is the README for setup?").ask()
    
    with open(path_to_readme, 'r') as file:
        string = file.read()
        html = markdown.markdown(string)

    soup = BeautifulSoup(html, 'html.parser')
    h2 = soup.find_all('h2')

    # Finding the index of "Requirements" &" "Setup" in the file
    setup_heading_index = req_heading_index = None
    for heading in h2:
        if "requirements" in heading.text.lower() : 
            req_heading_index = h2.index(heading)
        if "setup" in heading.text.lower():
            setup_heading_index = h2.index(heading)
        if setup_heading_index!=None and req_heading_index!=None: 
            break
    else:
        print("This readme does not fall under the template standards specified, and cannot be parsed.")
        sys.exit()
    
    req_html_elements = GetSection(h2[req_heading_index])
    
    # If requirements satisfied, move onto setup
    if EnsureRequirements(req_html_elements):
        
        setup_html_elements = GetSection(
            heading  = h2[setup_heading_index], 
            listForm = True
        )
        
        # identifying the device's OS
        keys_for_platform = {
            "linux" : "linux",
            "win32" : "windows",
            "darwin": "macos",
        }
        platform = keys_for_platform[sys.platform]
        
        sleep(1)
        print(f"Operating System: \033[1m{platform}\033[0m")
        sleep(1)
        print("\033[1mGetting steps for setup...\033[0m")
        sleep(1)
        
        # Finding the setup instructions for the current platform.
        for i in range(len(setup_html_elements)):
            if setup_html_elements[i].name=="h3" and setup_html_elements[i].text.lower()==platform:
                setup_html = setup_html_elements[i+1]
                break
        else:
            print("The current platform isn't supported yet.")
            exit()

        # Calling the equired functions as per the list type 
        print(setup_html)
        parsed_instructions = ParseInstructions(setup_html)
        
        if setup_html.name == 'ul': SetupViaChoices(parsed_instructions)
        elif setup_html.name == 'ol': SetupViaSteps(parsed_instructions)