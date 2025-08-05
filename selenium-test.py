from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

def google_search(query):
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ensure GUI is off
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Set path to chromedriver as per your configuration
    webdriver_service = Service(ChromeDriverManager().install())

    # Choose Chrome Browser
    driver = webdriver.Chrome(service=webdriver_service, options=chrome_options)
    
    driver.get("https://www.google.com/search?q=intext%3A231+%22lcecorp%22")


    print("Google Search Successful!")
        # Get the HTML content of the page
    page_source = driver.page_source

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(page_source, 'html.parser')

    # Now you can use BeautifulSoup functions to find specific elements in the HTML
    # For example, print all the links on the page:
    for link in soup.find_all('a'):
        print(link.get('href'))


    # Note: You can further manipulate the browser or extract information as per your requirements

    driver.quit()

if __name__ == "__main__":
    google_search("test")