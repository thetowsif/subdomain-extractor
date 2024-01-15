from flask import Flask, render_template, request
import re
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def extract_domains_from_text(text):
    domain_pattern = re.compile(r'\b(?:https?://)?(?:\*\.)?((?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})\b')
    domains = re.findall(domain_pattern, text)
    return domains


def extract_domains_from_crt_sh(domain):
    url = f'https://crt.sh/?q={domain}'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract domains from the response using a more specific selector
    domain_elements_5th_column = soup.select('table tr > td:nth-of-type(5)')
    domain_elements_6th_column = soup.select('table tr > td:nth-of-type(6)')

    # Extract text content from the fifth and sixth columns individually
    domains_5th_column = [element.get_text(separator=' ') for element in domain_elements_5th_column]
    domains_6th_column = [element.get_text(separator=' ') for element in domain_elements_6th_column]

    # Combine domains from both columns
    all_domains = domains_5th_column + domains_6th_column

    # Split each combined domain and flatten the list
    flattened_domains = [subdomain.strip() for domain in all_domains for subdomain in domain.split()]

    # Remove duplicates and sort the list
    unique_sorted_domains = sorted(list(set(flattened_domains)))

    return unique_sorted_domains



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        domain_to_check = request.form.get('domain_to_check')
        input_text = request.form.get('input_text')

        unique_domains = []

        # Check specific domain
        if domain_to_check:
            additional_domains = extract_domains_from_crt_sh(domain_to_check)
            unique_domains += additional_domains

        # Process bulk text
        if input_text:
            text_domains = extract_domains_from_text(input_text)
            unique_domains += text_domains

        unique_domains = sorted(list(set(unique_domains)))  # Remove duplicates and sort

        return render_template('index.html', domain_to_check=domain_to_check, input_text=input_text, unique_domains=unique_domains)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=8001)
