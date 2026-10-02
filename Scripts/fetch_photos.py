import urllib.request
import re
import os

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def fetch_url(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read().decode('utf-8', errors='ignore')

def download_img(img_url, out_path):
    req = urllib.request.Request(img_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        content = resp.read()
        with open(out_path, 'wb') as f:
            f.write(content)
    print(f"[PASS] Saved {out_path} ({len(content)} bytes) from {img_url}")

# 1. Aung Kyaw Zaw from Irrawaddy Burmese
try:
    html = fetch_url('https://burma.irrawaddy.com/news/2020/01/31/216348.html')
    m = re.search(r'<meta property="og:image" content="([^"]+)"', html)
    if m:
        img_url = m.group(1)
        print("Found Aung Kyaw Zaw image:", img_url)
        download_img(img_url, 'Data/raw_portraits_IND-RMC-001.jpg')
    else:
        print("No og:image found on Irrawaddy Aung Kyaw Zaw page")
except Exception as e:
    print("Error Aung Kyaw Zaw:", e)
