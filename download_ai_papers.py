import os
import re
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from datetime import datetime

def save_pdf(url, save_path):    """Save PDF from URL to file path"""
    try:
        with requests.get(url, stream=True, timeout=10) as r:
            r.raise_for_status()
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return True
    except Exception as e:
        print(f'Failed to download {url}: {e}')
        return False

def get_neurips(years, out_dir="NeurIPS"):
    """Scrape NeurIPS papers from proceedings.neurips.cc"""
    print('\n[NeurIPS]')
    base_url = "https://proceedings.neurips.cc/paper/"
    os.makedirs(out_dir, exist_ok=True)

    for year in years:
        url = f"{base_url}{year}"
        try:
            rsp = requests.get(url, timeout=10)
            if rsp.status_code != 200:
                print(f"{year} NeurIPS page not found")
                continue
            soup = BeautifulSoup(rsp.text, "html.parser")
            papers = soup.select("li a")
            for a in tqdm(papers, desc=f"NeurIPS {year}"):
                paper_title = a.text.strip().replace('/', '-')
                paper_url = "https://proceedings.neurips.cc" + a['href']
                try:
                    paper_html = requests.get(paper_url, timeout=10)
                    soup_paper = BeautifulSoup(paper_html.text, "html.parser")
                    pdf_link = None
                    for link in soup_paper.select("a[href$='.pdf']"):
                        if 'Paper' in link.text or 'paper' in link.text.lower():
                            pdf_link = link["href"]
                            if not pdf_link.startswith('http'):
                                pdf_link = "https://proceedings.neurips.cc" + pdf_link
                            break
                    if pdf_link:
                        file_name = os.path.join(out_dir, f'{year}_{paper_title}.pdf')
                        save_pdf(pdf_link, file_name)
                except Exception as e:
                    print(f"Error processing {paper_title}: {e}")
        except Exception as e:
            print(f"Error fetching {year} NeurIPS: {e}")

def get_iclr(years, out_dir="ICLR"):
    """Scrape ICLR papers from openreview.net"""
    print('\n[ICLR]')
    base_url = "https://openreview.net/group?id=ICLR.cc/{}/Conference"
    os.makedirs(out_dir, exist_ok=True)
    
    for year in years:
        try:
            accepted_url = f'https://openreview.net/group?id=ICLR.cc/{year}/Conference#accepted-papers'
            html = requests.get(accepted_url, timeout=10).text
            soup = BeautifulSoup(html, 'html.parser')
            papers = soup.select("a.note-title")
            
            if not papers:
                print(f"No papers found for ICLR {year}")
                continue
                
            for a in tqdm(papers, desc=f"ICLR {year}"):
                title = a.text.strip().replace('/', '-')
                link = a['href']
                if not link.startswith('http'):
                    link = "https://openreview.net" + link
                try:
                    note_html = requests.get(link, timeout=10).text
                    pdf_match = re.search(r'href="(https://openreview.net/pdf\?id=[\w\-]+)"', note_html)
                    if pdf_match:
                        pdf_url = pdf_match.group(1)
                        file_name = os.path.join(out_dir, f"{year}_{title}.pdf")
                        save_pdf(pdf_url, file_name)
                except Exception as e:
                    print(f"Error processing {title}: {e}")
        except Exception as e:
            print(f"Error fetching {year} ICLR: {e}")

def get_icml(years, out_dir="ICML"):
    """Scrape ICML papers from proceedings.mlr.press"""
    print('\n[ICML]')
    vol_map = {
        2025: "v245", 2024: "v235", 2023: "v202", 2022: "v162", 2021: "v139"
    }
    
    for year in years:
        try:
            out_dir_year = os.path.join(out_dir, str(year))
            os.makedirs(out_dir_year, exist_ok=True)
            vol = vol_map.get(year)
            if not vol:
                print(f"Year {year} not configured for ICML volume.")
                continue
            url = f'https://proceedings.mlr.press/{vol}/'
            html = requests.get(url, timeout=10).text
            soup = BeautifulSoup(html, "html.parser")
            papers = soup.select("div.paper a.title")
            
            for a in tqdm(papers, desc=f"ICML {year}"):
                title = a.text.strip().replace('/', '-')
                paper_div = a.find_parent('div', {'class': 'paper'})
                pdf_a = paper_div.select_one("a[href$='.pdf']") if paper_div else None
                if pdf_a:
                    pdf_link = pdf_a['href']
                    if not pdf_link.startswith('http'):
                        pdf_link = 'https://proceedings.mlr.press' + pdf_link
                    file_name = os.path.join(out_dir_year, f"{title}.pdf")
                    save_pdf(pdf_link, file_name)
        except Exception as e:
            print(f"Error fetching {year} ICML: {e}")

def get_aaai(years, out_dir="AAAI"):
    """Scrape AAAI papers from ojs.aaai.org"""
    print('\n[AAAI]')
    vol_map = {
        2025: "AAAI-25", 2024: "AAAI-24", 2023: "AAAI-23", 2022: "AAAI-22", 2021: "AAAI-21"
    }
    
    for year in years:
        try:
            out_dir_year = os.path.join(out_dir, str(year))
            os.makedirs(out_dir_year, exist_ok=True)
            vol = vol_map.get(year)
            if not vol:
                print(f"Year {year} not found in AAAI")
                continue
            url = f"https://ojs.aaai.org/index.php/AAAI/issue/view/{vol}"
            html = requests.get(url, timeout=10).text
            soup = BeautifulSoup(html, "html.parser")
            papers = soup.select("h5.media-heading > a")
            
            for a in tqdm(papers, desc=f"AAAI {year}"):
                title = a.text.strip().replace('/', '-')
                paper_url = a['href']
                if not paper_url.startswith('http'):
                    paper_url = 'https://ojs.aaai.org' + paper_url
                try:
                    paper_html = requests.get(paper_url, timeout=10).text
                    soup_paper = BeautifulSoup(paper_html, 'html.parser')
                    pdf_link_tag = soup_paper.select_one("a[href$='.pdf']")
                    if pdf_link_tag:
                        pdf_url = pdf_link_tag['href']
                        if not pdf_url.startswith('http'):
                            pdf_url = 'https://ojs.aaai.org' + pdf_url
                        file_name = os.path.join(out_dir_year, f"{title}.pdf")
                        save_pdf(pdf_url, file_name)
                except Exception as e:
                    print(f"Error processing {title}: {e}")
        except Exception as e:
            print(f"Error fetching {year} AAAI: {e}")

def get_acl(years, out_dir="ACL"):
    """Scrape ACL papers from aclanthology.org"""
    print('\n[ACL]')
    os.makedirs(out_dir, exist_ok=True)
    
    for year in years:
        try:
            url = f"https://aclanthology.org/events/acl-{year}/"
            html = requests.get(url, timeout=10).text
            soup = BeautifulSoup(html, "html.parser")
            papers = soup.select('div.paper')
            
            for paper in tqdm(papers, desc=f"ACL {year}"):
                title_tag = paper.select_one('a.title')
                if not title_tag:
                    continue
                title = title_tag.text.strip().replace('/', '-')
                pdf_link = paper.select_one('a[href$=".pdf"]')
                if pdf_link:
                    pdf_url = pdf_link['href']
                    if not pdf_url.startswith('http'):
                        pdf_url = "https://aclanthology.org" + pdf_url
                    file_name = os.path.join(out_dir, f"{year}_{title}.pdf")
                    save_pdf(pdf_url, file_name)
        except Exception as e:
            print(f"Error fetching {year} ACL: {e}")


def get_ijcai(years, out_dir="IJCAI"):
    """Scrape IJCAI papers from ijcai.org"""
    print('\n[IJCAI]')
    
    for year in years:
        try:
            out_dir_year = os.path.join(out_dir, str(year))
            os.makedirs(out_dir_year, exist_ok=True)
            url = f"https://www.ijcai.org/proceedings/{year}/"
            html = requests.get(url, timeout=10).text
            soup = BeautifulSoup(html, 'html.parser')
            papers = soup.select("li.paper > a")
            
            for a in tqdm(papers, desc=f"IJCAI {year}"):
                title = a.text.strip().replace('/', '-')
                pdf_url = a['href']
                if not pdf_url.startswith('http'):
                    pdf_url = 'https://www.ijcai.org' + pdf_url
                file_name = os.path.join(out_dir_year, f"{title}.pdf")
                save_pdf(pdf_url, file_name)
        except Exception as e:
            print(f"Error fetching {year} IJCAI: {e}")

if __name__ == "__main__":
    # Last 3 years (2023, 2024, 2025)
    years = [2025, 2024, 2023]
    
    print("="*60)
    print("AI Conference Paper Scraper")
    print("Scraping: ICLR, NeurIPS, ICML, AAAI, ACL, IJCAI")
    print("Years:", years)
    print("="*60)
    
    get_neurips(years)
    get_iclr(years)
    get_icml(years)
    get_aaai(years)
    get_acl(years)
    get_ijcai(years)
    
    print("\n" + "="*60)
    print("Scraping completed!")
    print("="*60)
