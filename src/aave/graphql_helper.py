from pandas._libs import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor

from src.utils import return_driver


def initialize_endpoint():
    return 'https://api.thegraph.com/subgraphs/name/aave/aave-v2'


def tag_to_dict(tag):
    """Recursively convert a BeautifulSoup tag to a focused dictionary."""

    if not tag.name:
        return

    result = {'tag': tag.name}

    # Check if the tag contains 'data-field-name' and 'data-field-type' attributes
    field_name = tag.attrs.get('data-field-name')
    field_type = tag.attrs.get('data-field-type')

    # Use those attributes if they exist
    if field_name and field_type:
        result['field_name'] = field_name
        result['field_type'] = field_type
        print(f"adding {field_name}!")

    children = []
    for child in tag.children:
        child_dict = tag_to_dict(child)
        if child_dict:
            children.append(child_dict)

    # Append children only if they exist
    if children:
        result['children'] = children

    return result


def process_child(child):
    result = {
        'tag': child.get('tag'),
        'field_name': None,
        'field_type': None
    }

    # If the child directly has the attributes
    if child.get('field_name') and child.get('field_type'):
        result['field_name'] = child['field_name']
        result['field_type'] = child['field_type']
    else:
        # For some of the tags, data-field-name and data-field-type can be nested inside.
        # The following tries to extract that.
        for grandchild in child.get('children', []):
            if grandchild.get('tag') == 'span':
                field_name = grandchild.get('field_name')
                field_type = grandchild.get('field_type')
                if field_name and field_type:
                    result['field_name'] = field_name
                    result['field_type'] = field_type

    return result


def process_json_in_parallel(json_structure):
    # Extract top-level children
    children = json_structure.get('children', [])

    # Process children in parallel
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(process_child, children))

    return results


def save_to_json(data, filename="output.json"):
    with open(filename, "w") as outfile:
        json.dump(data, outfile, indent=4)


def fetch_entities(url="https://thegraph.com/hosted-service/subgraph/aave/protocol-v3"):
    import requests
    from bs4 import BeautifulSoup

    def fetch_entities_from_graph():
        # Fetch the HTML content
        driver = return_driver()
        response = driver.get(url)
        # Wait for the button to become clickable and then click it
        wait = WebDriverWait(driver, 5)
        button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.graphiql-un-styled:nth-child(3)")))
        button.click()
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Extract entities using the CSS selector
        entities = soup.select("#query-unknown")[0]

        # Convert the first entity (or adapt as needed) to a JSON-like structure
        # json_structure = process_json_in_parallel(entities)
        json_structure = tag_to_dict(entities)
        save_to_json(json_structure)
        return json_structure

    entities = fetch_entities_from_graph()
    print(entities)
    return entities


def construct_query(token_address):
    # Construct the GraphQL query here
    return ''


def fetch_data(query, variables):
    # Send the query and fetch data here
    return {}

