import markdown
from bs4 import BeautifulSoup
import questionary
import sys
import re
import os
import webbrowser
from time import sleep

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
            commands = re.sub('(\n *)|(&& *)', '\n', code_tag.text).split("\n")
            commands_list.extend([command for command in commands if command != ''])
            code_tag.decompose()

        links = [(link.text, link.get('href')) for link in instructions[i].find_all('a')]
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
            [webbrowser.open_new_tab(link) for (reference, link) in links]
            print("\nGood to Go!\n")
            
    if commands:
        print(f"The following commands will be executed:")
        [print(i) for i in commands if i!='']
        if questionary.confirm("Want to proceed?").ask():
            [os.system(command) for command in commands]
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
            if commands: [os.system(command) for command in commands]
            if links: [webbrowser.open_new_tab(link) for reference, link in links]
    
        print("\nGood to Go! \n")


if __name__ == '__main__':
    
    path_to_readme = questionary.path("Where is the README for setup?").ask()
    
    with open(path_to_readme, 'r') as file:
        string = file.read()
        html = markdown.markdown(string)

    soup = BeautifulSoup(html, 'html.parser')
    h2 = soup.find_all('h2')

    # Finding the index of "Setup" in the file
    for heading in h2: 
        if "setup" in heading.text.lower():
            setup_heading_index = h2.index(heading)
            break
    else:
        print("This readme does not fall under the template standards specified, and cannot be parsed.")
        sys.exit()
        
    # Getting all the elements in the Setup section
    setup_html_elements = []
    for elements in h2[setup_heading_index].next_siblings:
        if elements.name == 'h2':
            break
        else:
            if elements!='\n':
                setup_html_elements.append(elements)

    # identifying the device's OS
    keys_for_platform = {
        "linux" : "linux",
        "win32" : "windows",
        "darwin": "macos",
    }
    platform = keys_for_platform[sys.platform]
    
    sleep(1)
    print(f"Operating System: \033[1m{platform}\033[1m")
    sleep(1)
    print("\033[1mGetting steps for setup...\033[1m")
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
    parsed_instructions = ParseInstructions(setup_html)
    if setup_html.name == 'ul': SetupViaChoices(parsed_instructions)
    elif setup_html.name == 'ol': SetupViaSteps(parsed_instructions)

