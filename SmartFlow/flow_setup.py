import mistune
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

def DisplayLinks(links: list):
    '''
    Displays links of the form of (reference, link) in the links list.
    '''
    print(f"Links to be opened -->")
    [print(f"  '{reference}' : {link}") for reference, link in links]

def DisplayCommands(commands):
    '''
    Displays the commands to be executed from the commands list.
    '''
    print(f"Commands to be executed -->")
    [print("  "+i) for i in commands]

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


####### Main functions ######
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
        if chosen_links: # If user has selected atleast 1 choice.
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


def ParseListItem(li):
    '''
    Segregates a list item into -->
    1. prompt: The instruction.
    2. commands: The snippets to be executed.
    3. links - to any files or sites linked.
    ---
    Parameters:
    li: a list item parsed with bs4.
    '''
    commands_list = []
    for code_tag in li.find_all('code'):
        commands_list.extend(ParseCommands(code_tag))
        code_tag.decompose()
        
    links = ParseLinks(li)
    prompt = li.text.strip()
    result = {
        "prompt" : prompt,
        "commands" : commands_list,
        "links" : links
    }
    return result

def ParseInstructions(htmlList, nestedList=False) -> dict:
    '''
    Returns a dictionary in the following manner:
    key: (index, nested_list_type(ol, ul or None), prompt_if_nested_list)
    value:
        1. If nested - Every list item parsed into a dict using ParsedListItem()
        2. If not nested - The single list item parsed using ParseListItem()
    '''
    parsed_instructions = {}
    instructions = htmlList.find_all('li')
    
    if nestedList:
        
        count = index = 0
        while count < len(instructions):
            item = instructions[count]
            
            if item.ol or item.ul:
                setup_instruct = {}
                if item.ol:
                    nested_list_items = item.ol.find_all('li')
                    n = len(nested_list_items)
                    for j in range(len(nested_list_items)):
                        setup_instruct[j] = ParseListItem(nested_list_items[j])
                    item.ol.decompose()
                    parsed_instructions[(index, 'ol', item.text.strip())] = setup_instruct
                
                else:
                    nested_list_items = item.ul.find_all('li')
                    n = len(nested_list_items)
                    for j in range(len(nested_list_items)):
                        setup_instruct[j] = ParseListItem(nested_list_items[j])
                    item.ul.decompose()
                    parsed_instructions[(index, 'ul', item.text.strip())] = setup_instruct
                
                count += n+1
            
            else:
                parsed_instructions[(index, None)] = ParseListItem(item)
                count += 1
                
            index += 1     
            
    else:
        for i in range(len(instructions)):
            parsed_instructions[i] = ParseListItem(instructions[i])
    
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
        print()
        DisplayLinks(links)
        print()
        if questionary.confirm("Want to open the links?").ask():
            OpenLinks(links)
            print("\nGood to Go!\n")
            
    if commands:
        print()
        DisplayCommands(commands)
        print()
        if questionary.confirm("Want to proceed?").ask():
            ExecuteCommands(commands)
            print("\nGood to Go!\n")
        

def SetupViaSteps(parsed_steps: dict):
    '''
    Setup described by ordered list indicates steps.
    This takes the parsed instructions and sets up via steps.
    '''
    print("The following steps will be followed -->\n")
    for i in parsed_steps.keys():
        prompt, commands, links = parsed_steps[i].values()
        print(f"{i+1}. {prompt}")
        if commands: DisplayCommands(commands)
        if links: DisplayLinks(links)
        print()
    
    if questionary.confirm('Want to continue?').ask():
        for i in parsed_steps.keys():
            prompt, commands, links = parsed_steps[i].values()
            if commands: ExecuteCommands(commands)
            if links: OpenLinks(links)
    
        print("\nGood to Go! \n")

def SetupNestedList(setupHtml):
    '''
    Completely sets up the required setup section
    '''
    parent_list_type = setupHtml.name
    parsed_instructions = ParseInstructions(setupHtml, nestedList=True)
    
    if parent_list_type == 'ul':
        
        prompts = []
        for i,j in parsed_instructions.items():
            if i[1]: prompts.append(i[2])     # If nested
            else: prompts.append(j['prompt']) # If a single list item

        choice = questionary.select("How do you want to set up?", choices=prompts).ask()
        index = prompts.index(choice)
        for i,j in parsed_instructions.items():
            if i[0] == index:
                if i[1]: # Proceeding if nested list found
                    if i[1] == 'ul': SetupViaChoices(j)
                    elif i[1] == 'ol': SetupViaSteps(j)
                else: # Setting up a single list item
                    prompt, commands, links = j.values()
                    if links:
                        DisplayLinks(links)
                        if questionary.confirm("Want to open the links?").ask():
                            OpenLinks(links)
                            print("\nGood to Go!\n")
                            
                    if commands:
                        DisplayCommands(commands)
                        if questionary.confirm("Want to proceed?").ask():
                            ExecuteCommands(commands)
                            print("\nGood to Go!\n")
                            
    elif parent_list_type == 'ol':
        print("\nThese steps will be followed -->\n")
        for key, d in parsed_instructions.items():
            # Display the prompt only if nested list
            if key[1]: print(f"{key[0]+1}. {key[2]}\n") 
            else:
                # Display the commands and links as well if it's a single li
                prompt, commands, links = d.values() 
                print(f"{key[0]+1}. {prompt}")
                if commands: DisplayCommands(commands)
                if links: DisplayLinks(links)
        
        if questionary.confirm("Want to proceed?").ask():
            for i, j in parsed_instructions.items():
                if i[1]:
                    print(f'\n\033[1m {i[0]+1}. {i[2]} \033[0m\n')
                    if i[1] == 'ul': SetupViaChoices(j)
                    elif i[1] == 'ol': SetupViaSteps(j)
                else:
                    prompt, commands, links = j.values()
                    print(f"\033[1m {i[0]+1}. {prompt} \033[0m\n")
                    if commands:
                        DisplayCommands(commands)
                        ExecuteCommands(commands)
                    if links: 
                        DisplayLinks(links)
                        OpenLinks(links)


def main():
        
    path_to_readme = questionary.path("Where is the markdown file for setup?").ask()
    
    if path_to_readme.endswith('.md'):
    
        with open(path_to_readme, 'r') as file:
            string = file.read()
            html = mistune.html(string)

        soup = BeautifulSoup(html, 'html.parser')
        h2 = soup.find_all('h2')

        # Finding the index of "Requirements" &" "Setup" in the file
        setup_heading_index = req_heading_index = None
        for heading in h2:
            if heading.text.lower().startswith("requirement") : 
                req_heading_index = h2.index(heading)
            if "setup" in heading.text.lower():
                setup_heading_index = h2.index(heading)
            if setup_heading_index != None and req_heading_index != None: 
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
                sys.exit()

            # Calling the required functions as per the list type 
            if setup_html.ul or setup_html.ol: SetupNestedList(setup_html)
            else:
                parsed_instructions = ParseInstructions(setup_html)
                if setup_html.name == 'ul': SetupViaChoices(parsed_instructions)
                elif setup_html.name == 'ol': SetupViaSteps(parsed_instructions)
    
    else:
        print("Please provide a valid markdown file path.")

if __name__ == '__main__':
    main()