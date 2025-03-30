import requests
import concurrent.futures
import argparse
import json
import csv
import re
import time
import random
import sys
import threading
import itertools
from typing import List, Dict, Tuple
from urllib.parse import quote
from functools import lru_cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Goku ASCII Art
GOKU_ASCII = r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣷⣶⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⣿⣿⣿⣷⡒⢄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣿⣿⣿⣿⣿⣆⠙⡄⠀⠐⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣤⣤⣤⣤⣤⣤⣤⣤⠤⢄⡀⠀⠀⣿⣿⣿⣿⣿⣿⡆⠘⡄⠀⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⢿⣿⣿⣿⣿⣿⣿⣿⣦⡈⠒⢄⢸⣿⣿⣿⣿⣿⣿⡀⠱⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣦⠀⠱⣿⣿⣿⣿⣿⣿⣇⠀⢃⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢿⣿⣿⣿⣿⣿⣿⣷⡄⣹⣿⣿⣿⣿⣿⣿⣶⣾⣿⣶⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣶⣾⣭⣍⡉⠙⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⣠⣶⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠉⠉⠛⠻⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡷⢂⣓⣶⣶⣶⣶⣤⣤⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⢿⣿⣿⣿⠟⢀⣴⢿⣿⣿⣿⠟⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠛⠋⠉⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠤⠤⠤⠤⠙⣻⣿⣿⣿⣿⣿⣿⣾⣿⣿⡏⣠⠟⡉⣾⣿⣿⠋⡠⠊⣿⡟⣹⣿⢿⣿⣿⣿⠿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣤⣶⣤⣭⣤⣼⣿⢛⣿⣿⣿⣿⣻⣿⣿⠇⠐⢀⣿⣿⡷⠋⠀⢠⣿⣺⣿⣿⢺⣿⣋⣉⣉⣩⣴⣶⣤⣤⣄⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠛⠻⠿⣿⣿⣿⣇⢻⣿⣿⡿⠿⣿⣯⡀⠀⢸⣿⠋⢀⣠⣶⠿⠿⢿⡿⠈⣾⣿⣿⣿⣿⡿⠿⠛⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠻⢧⡸⣿⣿⣿⠀⠃⠻⠟⢦⢾⢣⠶⠿⠏⠀⠰⠀⣼⡇⣸⣿⣿⠟⠉⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣾⣶⣽⣿⡟⠓⠒⠀⠀⡀⠀⠠⠤⠬⠉⠁⣰⣥⣾⣿⣿⣶⣶⣷⡶⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠉⠉⠹⠟⣿⣿⡄⠀⠀⠠⡇⠀⠀⠀⠀⠀⢠⡟⠛⠛⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⠋⠹⣷⣄⠀⠐⣊⣀⠀⠀⢀⡴⠁⠣⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣀⠤⠊⢁⡸⠀⣆⠹⣿⣧⣀⠀⠀⡠⠖⡑⠁⠀⠀⠀⠑⢄⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣦⣶⣿⣿⣟⣁⣤⣾⠟⠁⢀⣿⣆⠹⡆⠻⣿⠉⢀⠜⡰⠀⠀⠈⠑⢦⡀⠈⢾⠑⡾⠲⣄⠀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣶⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠖⠒⠚⠛⠛⠢⠽⢄⣘⣤⡎⠠⠿⠂⠀⠠⠴⠶⢉⡭⠃⢸⠃⠀⣿⣿⣿⠡⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⡤⠶⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣋⠁⠀⠀⠀⠀⠀⢹⡇⠀⠀⠀⠀⠒⠢⣤⠔⠁⠀⢀⡏⠀⠀⢸⣿⣿⠀⢻⡟⠑⠢⢄⡀⠀⠀⠀⠀
⠀⠀⠀⠀⢸⠀⠀⠀⡀⠉⠛⢿⣿⣿⣿⣿⣿⣿(toolong)⣿⣿⣿⣿⣷⣄⣀⣀⡀⠀⢸⣷⡀⣀⣀⡠⠔⠊⠀⠀⢀⣠⡞⠀⠀⠀⢸⣿⡿⠀⠘⠀⠀⠀⠀⠈⠑⢤⠀⠀
⠀⠀⢀⣴⣿⡀⠀⠀⡇⠀⠀⠀⠈⣿⣿⣿⣿⣿⣿⣿⣿⣝⡛⠿⢿⣷⣦⣄⡀⠈⠉⠉⠁⠀⠀⠀⢀⣠⣴⣾⣿⡿⠁⠀⠀⠀⢸⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⡜⠀⠀
⠀⢀⣾⣿⣿⡇⠀⢰⣷⠀⢀⠀⠀⢹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣦⣭⣍⣉⣉⠀⢀⣀⣤⣶⣾⣿⣿⣿⢿⠿⠁⠀⠀⠀⠀⠘⠀⠀⠀⠀⠀⠀⠀⠀⠀⡰⠉⢦⠀
⢀⣼⣿⣿⡿⢱⠀⢸⣿⡀⢸⣧⡀⠀⢿⣿⣿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡭⠖⠁⠀⡠⠂⠀⠀⠀⠀⠀⠀⠀⠀⢠⠀⠀⠀⢠⠃⠀⠈⣀
⢸⣿⣿⣿⡇⠀⢧⢸⣿⣇⢸⣿⣷⡀⠈⣿⣿⣇⠈⠛⢿⣿⣿⣿⣿⣿⣿⠿⠿⠿⠿⠿⠿⠟⡻⠟⠉⠀⠀⡠⠊⠀⢠⠀⠀⠀⠀⠀⠀⠀⠀⣾⡄⠀⢠⣿⠔⠁⠀⢸
⠈⣿⣿⣿⣷⡀⠀⢻⣿⣿⡜⣿⣿⣷⡀⠈⢿⣿⡄⠀⠀⠈⠛⠿⣿⣿⣿⣷⣶⣶⣶⡶⠖⠉⠀⣀⣤⡶⠋⠀⣠⣶⡏⠀⠀⠀⠀⠀⠀⠀⢰⣿⣧⣶⣿⣿⠖⡠⠖⠁
⠀⣿⣿⣷⣌⡛⠶⣼⣿⣿⣷⣿⣿⣿⣿⡄⠈⢻⣷⠀⣄⡀⠀⠀⠀⠈⠉⠛⠛⠛⠁⣀⣤⣶⣾⠟⠋⠀⣠⣾⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⠷⠊⠀⢰⠀
⢰⣿⣿⠀⠈⢉⡶⢿⣿⣿⣿⣿⣿⣿⣿⣿⣆⠀⠙⢇⠈⢿⣶⣦⣤⣀⣀⣠⣤⣶⣿⣿⡿⠛⠁⢀⣤⣾⣿⣿⡿⠁⠀⠀⠀⠀⠀⠀⠀⣸⣿⡿⠿⠋⠙⠒⠄⠀⠉⡄
⣿⣿⡏⠀⠀⠁⠀⠀⠀⠉⠉⠙⢻⣿⣿⣿⣿⣷⡀⠀⠀⠀⠻⣿⣿⣿⣿⣿⠿⠿⠛⠁⠀⣀⣴⣿⣿⣿⣿⠟⠀⠀⠀⠀⠀⠀⠀⠀⢠⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰
"""

# Loading Animation Frames
LOADING_FRAMES = [
    "[Goku Voice] Charging Ki... |",
    "[Goku Voice] Charging Ki... /",
    "[Goku Voice] Charging Ki... -",
    "[Goku Voice] Charging Ki... \\",
]

# User-Agents
UA_LIST = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Mobile/15E148 Safari/604.1',
]

# Proxy list (optional)
PROXIES = []

# Session with retries (for scanning mode)
session = requests.Session()
retry_strategy = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("http://", adapter)
session.mount("https://", adapter)

# Load platforms from external JSON file
def load_platforms(file_path: str = 'platforms.json') -> List[Dict[str, str]]:
    """Load platforms from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            platforms = json.load(f)
        if not isinstance(platforms, list) or not all(isinstance(p, dict) and 'name' in p and 'url_template' in p for p in platforms):
            raise ValueError("Invalid platforms.json format")
        return platforms
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        print(f"[Goku Voice] Power source missing or corrupted: {e}. Using default platforms!")
        return [
            {'name': 'Twitter', 'url_template': 'https://twitter.com/{}'},
            {'name': 'GitHub', 'url_template': 'https://github.com/{}'},
        ]

# Loading screen thread
loading_stop = threading.Event()

def loading_screen():
    """Display a fancy loading animation."""
    for frame in itertools.cycle(LOADING_FRAMES):
        if loading_stop.is_set():
            sys.stdout.write('\r' + ' ' * 40 + '\r')
            sys.stdout.flush()
            break
        sys.stdout.write(f'\r{frame}')
        sys.stdout.flush()
        time.sleep(0.2)

@lru_cache(maxsize=256)
def generate_variations(username: str) -> tuple:
    """Generate robust username variations."""
    if not isinstance(username, str) or not username.strip():
        return tuple()
    original = username.strip()
    base = original.lower()
    variations = {original, base}

    if ' ' in original:
        variations.update([original.replace(' ', sep) for sep in ['', '_', '-', '.']])

    for i in '1234':
        variations.update([base + i, i + base, original + i, i + original])

    swaps = {'o': '0', 'l': '1', 'e': '3', 's': '5', 'a': '4', 'i': '1'}
    for orig, new in swaps.items():
        if orig in base:
            variations.add(base.replace(orig, new))
        if orig in original:
            variations.add(original.replace(orig, new))

    for sep in '_-.x':
        variations.update([base + sep, sep + base, original + sep, sep + original])

    variations.update([original.upper(), original.capitalize()])

    for char in '!@#$':
        variations.update([base + char, char + base])

    if re.search(r'(.)\1', base):
        variations.add(re.sub(r'(.)\1', r'\1', base))

    valid_variations = set()
    for var in variations:
        cleaned = var
        if '.tumblr.com' in PLATFORMS[15]['url_template']:
            cleaned = re.sub(r'\.+', '.', var.strip('.'))
        cleaned = re.sub(r'[^a-zA-Z0-9_.-]', '', cleaned) if not any(c in cleaned for c in '@#') else cleaned
        if (cleaned and len(cleaned) > 1 and not cleaned.startswith(('.', '_', '-')) 
            and not cleaned.endswith(('.', '_', '-')) and '..' not in cleaned):
            valid_variations.add(cleaned)
    
    return tuple(valid_variations)

def check_username(args: Tuple[Dict[str, str], str, bool]) -> Tuple[str, bool, Dict]:
    """Error-free username check (for scanning mode)."""
    try:
        platform, original_username, use_proxy = args
        formatted_username = original_username
        if platform['name'] in ['YouTube', 'TikTok', 'Medium', 'Mastodon'] and '@' not in original_username:
            formatted_username = '@' + original_username
        
        url = platform['url_template'].format(quote(formatted_username))
        if not re.match(r'^https?://[a-zA-Z0-9-._]+', url) or '..' in url:
            return platform['name'], False, {
                'url': url, 'status': 'invalid_url', 'username': original_username, 'formatted': formatted_username
            }

        headers = {'User-Agent': random.choice(UA_LIST)}
        proxies = random.choice(PROXIES) if use_proxy and PROXIES else None
        response = session.get(url, headers=headers, proxies=proxies, timeout=3, allow_redirects=False)
        status = response.status_code == 200
        if status and platform['name'] == 'Tumblr' and 'This Tumblr is Empty' in response.text:
            status = False
        return platform['name'], status, {
            'url': url,
            'status': 'active' if status else f'code_{response.status_code}',
            'username': original_username,
            'formatted': formatted_username
        }
    except Exception as e:
        return platform.get('name', 'Unknown'), False, {
            'url': url if 'url' in locals() else 'unknown',
            'status': f'error_{str(e)[:50]}',
            'username': original_username if 'original_username' in locals() else 'unknown',
            'formatted': formatted_username if 'formatted_username' in locals() else 'unknown'
        }

def generate_urls(username: str, verbose: bool = False) -> Dict:
    """Generate URLs for all platforms and variations."""
    global PLATFORMS
    PLATFORMS = load_platforms()
    variations = generate_variations(username)
    if not variations:
        print("\n[Goku Voice] Kamehameha! No valid targets to generate!")
        return {}
    
    results = {var: {'urls': []} for var in variations}
    total_tasks = len(variations) * len(PLATFORMS)
    print(f"\n[Goku Voice] Powering up! Generating {total_tasks} URLs at lightning speed!")
    
    loading_thread = threading.Thread(target=loading_screen)
    loading_thread.start()

    try:
        for var in variations:
            for platform in PLATFORMS:
                formatted_username = var
                if platform['name'] in ['YouTube', 'TikTok', 'Medium', 'Mastodon'] and '@' not in var:
                    formatted_username = '@' + var
                url = platform['url_template'].format(quote(formatted_username))
                if re.match(r'^https?://[a-zA-Z0-9-._]+', url) and '..' not in url:
                    results[var]['urls'].append({platform['name']: {'url': url, 'formatted': formatted_username}})
    except Exception as e:
        print(f"\n[Goku Voice] Whoa! Unexpected power surge: {e}")
    finally:
        loading_stop.set()
        loading_thread.join()

    if verbose:
        for var, data in results.items():
            print(f"\n[Target]: {var}")
            for entry in data['urls']:
                for p, info in entry.items():
                    print(f"  [+] {p}: {info['url']}")
    
    return results

def scan_platforms(username: str, stealth: bool = False, verbose: bool = False) -> Dict:
    """Error-free platform scanning with loading screen."""
    global PLATFORMS
    PLATFORMS = load_platforms()
    variations = generate_variations(username)
    if not variations:
        print("\n[Goku Voice] Kamehameha! No valid targets to scan!")
        return {}
    
    results = {var: {'hits': [], 'misses': []} for var in variations}
    tasks = [(p, v, stealth) for v in variations for p in PLATFORMS]
    total_tasks = len(tasks)
    print(f"\n[Goku Voice] Powering up! Scanning {total_tasks} checks at lightning speed!")
    
    loading_thread = threading.Thread(target=loading_screen)
    loading_thread.start()

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=min(50, total_tasks or 1)) as executor:
            future_to_result = {executor.submit(check_username, task): task for task in tasks}
            completed = 0
            for future in concurrent.futures.as_completed(future_to_result):
                completed += 1
                if verbose and completed % 100 == 0:
                    print(f"\r[Goku Voice] Progress: {completed}/{total_tasks} targets blasted!", end='')
                platform_name, found, details = future.result()
                var = details.get('username', 'unknown')
                if var not in results:
                    results[var] = {'hits': [], 'misses': []}
                if found:
                    results[var]['hits'].append({platform_name: details})
                elif verbose:
                    results[var]['misses'].append(platform_name)
    except Exception as e:
        print(f"\n[Goku Voice] Whoa! Unexpected power surge: {e}")
    finally:
        loading_stop.set()
        loading_thread.join()

    if verbose:
        for var, data in results.items():
            if data['hits']:
                print(f"\n[Target]: {var}")
                for hit in data['hits']:
                    for p, info in hit.items():
                        print(f"  [+] {p}: {info['url']} (Status: {info['status']})")
            elif verbose > 1:
                print(f"\n[Target]: {var} - No hits (Misses: {', '.join(data['misses'])})")
    
    return results

def save_results(results: Dict, format: str = 'json', mode: str = 'scan') -> str:
    """Error-free result saving for both scan and generate modes."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"goku_{mode}_results_{timestamp}.{format}"
    try:
        if not results or not isinstance(results, dict):
            print("[Goku Voice] Nothing to save! Power level too low!")
            return ""
        if format == 'json':
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, separators=(',', ':'))
        else:  # CSV
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if mode == 'scan':
                    writer.writerow(['Variation', 'Platform', 'URL', 'Status'])
                    for var, data in results.items():
                        for hit in data.get('hits', []):
                            for p, info in hit.items():
                                writer.writerow([var, p, info.get('url', ''), info.get('status', '')])
                else:  # generate
                    writer.writerow(['Variation', 'Platform', 'URL'])
                    for var, data in results.items():
                        for entry in data.get('urls', []):
                            for p, info in entry.items():
                                writer.writerow([var, p, info.get('url', '')])
        return filename
    except Exception as e:
        print(f"[Goku Voice] Oops! Couldn't save the power: {e}")
        return ""

def cli_main():
    """Error-free CLI entry with scan and generate modes."""
    parser = argparse.ArgumentParser(description="GokuTrace: Lightning-fast username tracker and URL generator.")
    parser.add_argument('username', nargs='?', default='', help="Target username")
    parser.add_argument('-s', '--stealth', action='store_true', help="Use proxies if available (scan mode only)")
    parser.add_argument('-v', '--verbose', action='count', default=0, help="Verbose output (repeat for more: -vv)")
    parser.add_argument('-o', '--output', choices=['json', 'csv'], default='json', help="Output format")
    parser.add_argument('-g', '--generate', action='store_true', help="Generate URLs instead of scanning")
    try:
        args = parser.parse_args()
        if not args.username:
            raise ValueError("No username provided!")
    except (SystemExit, ValueError) as e:
        print(f"[Goku Voice] Huh? Invalid command! Try: python script.py <username> [-s] [-v] [-o json|csv] [-g]")
        return

    print(GOKU_ASCII)
    start_time = time.time()
    if args.generate:
        results = generate_urls(args.username, args.verbose)
        mode = 'generate'
    else:
        results = scan_platforms(args.username, args.stealth, args.verbose)
        mode = 'scan'
    filename = save_results(results, args.output, mode)
    elapsed = time.time() - start_time
    if filename:
        if mode == 'scan':
            hits = sum(len(data.get('hits', [])) for data in results.values())
            print(f"\n[Goku Voice] It's over 9000! Scan complete in {elapsed:.2f}s! Found {hits} hits. Saved to {filename}")
        else:
            urls = sum(len(data.get('urls', [])) for data in results.values())
            print(f"\n[Goku Voice] URLs powered up in {elapsed:.2f}s! Generated {urls} URLs. Saved to {filename}")
    else:
        print(f"\n[Goku Voice] Power drained in {elapsed:.2f}s! No results saved.")

if __name__ == "__main__":
    cli_main()
