from bs4 import BeautifulSoup
import requests
import string
import json
import glob


DISEASE_URL = 'https://www.mayoclinic.org/diseases-conditions/index?letter='
TESTS_URL = 'https://www.mayoclinic.org/tests-procedures/index?letter='
DRUGS_URL = 'https://www.mayoclinic.org/drugs-supplements/drug-list?letter='

HEADING_TYPE = {
    DISEASE_URL: 'h2',
    TESTS_URL: 'h2',
    DRUGS_URL: 'h3'
}
HEADING_TEXT = {
    DISEASE_URL: 'Overview',
    TESTS_URL: 'Overview',
    DRUGS_URL: 'Descriptions'
}

def get_definition(url, link):
    # Right now, we just grab the first link. This might not always be the right thing to do.
    agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    page = requests.get(link, headers=agent)
    soup = BeautifulSoup(page.content, 'html.parser')

    headings = soup.find_all(HEADING_TYPE[url])
    for h in headings:
        if h.text == HEADING_TEXT[url]:
            return h.find_next_sibling('p').text

def process_letter(url, letter):
    full_url = url + letter
    agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    page = requests.get(full_url, headers=agent)
    soup = BeautifulSoup(page.content, 'html.parser')
    
    concepts = []
    
    lis = soup.find('div', {'id': 'index'}).find_all('li')
    for li in lis:
        link = 'https://www.mayoclinic.org' + li.find('a')['href']
        concept = li.get_text().strip().split('(See:')[0]
        definition = get_definition(url, link)
        
        c = {
            'concept': concept,
            'url': link,
            'definition': definition
        }
        print(concept)
        concepts.append(c)

    return concepts
        


def process_type(url, prefix):
    concepts = []
    for letter in string.ascii_letters[string.ascii_letters.index('A'):]:    
        cs = process_letter(url, letter)
        save_concepts(cs, prefix + letter + '.json')
        concepts += cs
    return concepts


def save_concepts(concepts, fname):
    with open(fname, 'w') as handle:
        json.dump(concepts, handle)

def merge_concepts(con_type):
    concepts = []
    for fname in glob.glob(con_type + '_*.json'):
        with open(fname, 'r') as handle:
            concepts += json.load(handle)

    with open(con_type + '.json', 'w') as handle:
        json.dump(concepts, handle)



concepts = process_type(DRUGS_URL, prefix='drugs_')
merge_concepts('drugs')


