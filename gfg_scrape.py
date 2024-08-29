import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import signal
import sys

# Signal handler for graceful exit
def signal_handler(sig, frame):
    print('You pressed Ctrl+C! Exiting gracefully...')
    driver.quit()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(60)
    return driver

def handle_cookie_consent(driver):
    try:
        # Wait for the cookie consent banner to be clickable
        consent_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "cookie-consent-accept"))
        )
        consent_button.click()
        print("Dismissed cookie consent.")
        time.sleep(2)  # Give time for the banner to disappear
    except Exception as e:
        print("No cookie consent banner found or failed to click: ", e)

def expand_content(driver):
    try:
        wait = WebDriverWait(driver, 10)
        # Handle the cookie consent first
        handle_cookie_consent(driver)

        # Scroll into view and attempt to click the image
        expand_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "read-more-container")))
        expand_image = expand_container.find_element(By.TAG_NAME, "img")
        driver.execute_script("arguments[0].scrollIntoView(true);", expand_image)
        expand_image.click()
        print("Clicked read-more image to expand content.")
        time.sleep(2)  # Wait for content to expand
    except Exception as e:
        print(f"No 'read-more-container' or 'img' found or failed to click: {e}")


def get_all_links(url):
    driver.get(url)
    print(f"Loaded page: {url}")
    time.sleep(2)  # Wait for initial content load

    # Handle cookie consent
    handle_cookie_consent(driver)

    # Expand content before collecting links
    expand_content(driver)

    # Collect all links
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    content_divs = soup.find_all('div', class_='text')
    links = []
    if not content_divs:
        print("No 'text' class divs found.")
    for div in content_divs:
        div_links = [a['href'] for a in div.find_all('a', href=True)]
        if div_links:
            links.extend(div_links)
        else:
            print(f"No links found in div: {div}")
    return links

def visit_and_download_links(driver, base_url, links, download_path):
    for link in links:
        full_url = link if link.startswith('http') else base_url + link
        print(f"Processing link: {full_url}")
        try:
            driver.get(full_url)
            print(f"Loaded page: {full_url}")

            # Handle cookie consent
            handle_cookie_consent(driver)

            # Expand content
            expand_content(driver)

            # Save the HTML of the page
            page_source = driver.page_source
            file_name = os.path.join(download_path, f"{link.replace('/', '_').replace(':', '_')}.html")
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(page_source)
            print(f"Saved HTML to {file_name}")

        except Exception as e:
            print(f"Error processing {full_url}: {e}")
            continue

if __name__ == "__main__":
    base_url = 'https://www.geeksforgeeks.org/gate-cs-notes-gq/'  # Your specific URL
    download_path = '/home/vamshi/Downloads/gfg'  # Your specified download path

    if not os.path.exists(download_path):
        os.makedirs(download_path)

    driver = setup_driver()
    try:
        links = get_all_links(base_url)
        if links:
            print(f"Found {len(links)} links to process.")
            visit_and_download_links(driver, base_url, links, download_path)
        else:
            print("No links found to process.")
    finally:
        driver.quit()
