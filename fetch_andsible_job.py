#!/usr/bin/env python3
import sys
import requests
from bs4 import BeautifulSoup

def fetch_html_content(api_url, job_id, api_token):
    job_url = f"{api_url}/jobs/{job_id}/stdout/"
    headers = {
        'Authorization': f'Bearer {api_token}'
    }
    try:
        response = requests.get(job_url, headers=headers)
        response.raise_for_status()  # Raise exception for non-200 status codes
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching HTML content: {e}")
        return None

def extract_div_content(html_content, class_name):
    soup = BeautifulSoup(html_content, 'html.parser')
    divs = soup.find_all('div', class_=class_name)
    if divs:
        for div in divs:
            print(div.text.strip())
    else:
        print(f"Div with class '{class_name}' not found.")

def main():
    if len(sys.argv) != 3:
        print("Usage: ./script.py <job_id> <class_name>")
        return
    
    job_id = sys.argv[1]
    class_name = sys.argv[2]
    api_url = 'https://automation.aap2.example.com/api/v2'
    api_token = 'your_api_token'
    
    # Fetch HTML content for the specified job ID
    html_content = fetch_html_content(api_url, job_id, api_token)
    if html_content:
        # Extract content of specific <div> based on class name
        extract_div_content(html_content, class_name)

if __name__ == "__main__":
    main()
