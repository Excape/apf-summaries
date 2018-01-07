import requests
from bs4 import BeautifulSoup
import pdfkit
from urllib.parse import urljoin
import re

BASE_URL = "https://wiki.ifs.hsr.ch/APF/"
EXTERNAL_CSS = "pdf-style.css"
TOC_XSL = "toc-style.xsl"

HEADING_REGEX = re.compile('U\d+_\d_(.+)_HS17')


def parse_page(url):
    page_req = requests.get(url)
    return BeautifulSoup(page_req.content, "lxml")


def get_week_urls():
    return [f"{BASE_URL}UebW{week_nr}_HS17"
            for week_nr in range(2, 14)]


def get_pattern_urls(week_urls, practical_group):
    pattern_urls = []
    for week_url in week_urls:
        page = parse_page(week_url)
        links = page.find_all('a')
        relevant_links = filter(lambda l: practical_group in l.get('href', 'none'), links)
        pattern_urls.extend([link['href'] for link in relevant_links])
    return [f"{BASE_URL}wiki.cgi?{pattern_url}&printerfriendly" for pattern_url in pattern_urls]


def sort_patterns(pattern_urls, practical_group):
    return {
        "Posa 1": extract_book_patterns(pattern_urls, practical_group, 1),
        "Security Patterns": extract_book_patterns(pattern_urls, practical_group, 2),
        "Fault Tolerance": extract_book_patterns(pattern_urls, practical_group, 3)
        }


def extract_book_patterns(pattern_urls, practical_group, book_nr):
    """ 1 = Posa1, 2 = Security Patterns, 3 = Fault Tolerance """
    return list(filter(lambda url: f"{practical_group}_{book_nr}" in url, pattern_urls))    


def generate_pdf(outfile, pattern_urls):
    html_string = ""
    for pattern_url in pattern_urls:
        pattern_page = parse_page(pattern_url)
        relative_to_absolute_paths(pattern_page)
        fix_headings(pattern_page)
        html_string += str(pattern_page)

    pdfkit_options = {
        'encoding': "UTF-8",
        'page-size': "A4",
        'margin-top': '1in',
        'margin-right': '1in',
        'margin-bottom': '1in',
        'margin-left': '1in',
        'footer-right': "[page]/[toPage]",
        'footer-font-size': '10'
        }
    toc_options = {'xsl-style-sheet': TOC_XSL}
    pdfkit.from_string(
        html_string, outfile, options=pdfkit_options, css=EXTERNAL_CSS, toc=toc_options)


def relative_to_absolute_paths(page):
    for img in page.find_all('img'):
        if 'src' in img.attrs:
            img['src'] = urljoin(BASE_URL, img['src'])


def fix_headings(page):
    for heading in page.find_all('h1'):
        text = heading.a.contents[0]
        regex_search = re.search(HEADING_REGEX, text)
        heading.string = regex_search.group(1)


if __name__ == "__main__":
    practical_group = "U13"
    pattern_urls = get_pattern_urls(get_week_urls(), practical_group)
    patterns = sort_patterns(pattern_urls, practical_group)

    generate_pdf('posa1.pdf', patterns['Posa 1'])
    generate_pdf('security_patterns.pdf', patterns['Security Patterns'])
    generate_pdf('fault_tolerance.pdf', patterns['Fault Tolerance'])
