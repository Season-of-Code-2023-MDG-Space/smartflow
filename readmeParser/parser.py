import markdown
from bs4 import BeautifulSoup
import questionary
import sys

with open('readmeParser/template.md', 'r') as file:
    string = file.read()
    html = markdown.markdown(string)

soup = BeautifulSoup(html, 'html.parser')
h2 = soup.find_all('h2')

for i in h2: 
    if "setup" in i.text.lower():
        setup_heading_index = h2.index(i)
        break

l = []

for i in h2[setup_heading_index].next_siblings:
    if i.name == 'h2':
        break
    else:
        if i!='\n':
            l.append(i)

platform = "linux"
for i in range(len(l)):
    if l[i].name=="h3" and l[i].text.lower()==platform:
        setup_html = l[i+1]

if setup_html.name == 'ul':
    # [i.code.decompose() and i.a.decompose() for i in setup_html.find_all('li')]
    choices = [i.text for i in setup_html.find_all('li')]
    choice = questionary.select("How do you wanna setup?", choices=choices).ask()
    for i in setup_html:
        if choice == i.text:
            if i.code:
                print("Commands")
                [print(a.text) for a in i.find_all('code')]
            if i.a:
                print("Links")
                [print(f"{j.text} : {j.get('href')}") for j in i.find_all('a')]
