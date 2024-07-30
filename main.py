import os
import requests
import pandas as pd
from urllib.parse import urljoin
import yaml

GITHUB_API_URL = "https://api.github.com"
OPENAI_API_URL = "https://api.openai.com/v1/engines/davinci-codex/completions"
GITHUB_TOKEN = 'your_github_token'
OPENAI_API_KEY = 'your_openai_api_key'

# Headers for GitHub API
headers = {
    'Authorization': f'token {GITHUB_TOKEN}'
}

# Headers for OpenAI API
openai_headers = {
    'Authorization': f'Bearer {OPENAI_API_KEY}',
    'Content-Type': 'application/json'
}

def get_repo_files(repo_url, file_extensions):
    owner, repo = repo_url.rstrip('/').split('/')[-2:]
    contents_url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents"
    return fetch_files(contents_url, file_extensions)

def fetch_files(contents_url, file_extensions, path=""):
    response = requests.get(contents_url, headers=headers)
    response.raise_for_status()
    items = response.json()
    files = []

    for item in items:
        if item['type'] == 'file' and any(item['name'].endswith(ext) for ext in file_extensions):
            files.append(item['download_url'])
        elif item['type'] == 'dir':
            files += fetch_files(item['url'], file_extensions, path + item['name'] + '/')

    return files

def download_file(file_url):
    response = requests.get(file_url)
    response.raise_for_status()
    return response.text

def check_infringement(content):
    data = {
        "prompt": f"Check this content for copyright and trademark infringements:\n\n{content}",
        "max_tokens": 150
    }
    response = requests.post(OPENAI_API_URL, headers=openai_headers, json=data)
    response.raise_for_status()
    return response.json().get('choices')[0].get('text').strip()

def main(repo_url, output_csv):
    file_extensions = ['.md', '.xml', '.json', '.yaml']
    files = get_repo_files(repo_url, file_extensions)

    results = []

    for file_url in files:
        content = download_file(file_url)
        infringement = check_infringement(content)
        results.append({'file_url': file_url, 'infringement': infringement})

    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")

if __name__ == "__main__":
    repo_url = "https://github.com/beckn/sandbox"
    output_csv = "infringements_report.csv"
    main(repo_url, output_csv)

