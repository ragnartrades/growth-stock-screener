from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup

# constants
timeout = 30
holdings_data_xpath = "/html/body/div[3]/div/main/div[2]/div[4]/div[3]/div/div[1]/div/div[1]/div[2]/div/div[2]/div/table/tbody"

# construct the url and headers for the request
symbol = "NVDA"
url = f"https://www.nasdaq.com/market-activity/stocks/{symbol}/institutional-holdings"

# configure selenium to use a headless Firefox browser instance to request data
options = webdriver.FirefoxOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.page_load_strategy = "none"
driver = webdriver.Firefox(options=options)

# perform GET request
driver.get(url)

# load page until holdings table is present in the DOM
try:
    data_present = EC.presence_of_element_located((By.XPATH, holdings_data_xpath))
    WebDriverWait(driver, timeout).until(data_present)
    driver.execute_script("window.stop();")
except TimeoutException:
    print(f"Skipping {symbol} (request timed out)")
    # continue

# extract institutional holdings information from site HTML
soup = BeautifulSoup(driver.page_source, "html.parser")

# the second table on the "institutional-holdings" page has position data
holdings_tables = soup.find_all("tbody", class_="institutional-holdings__body")
active_positions_table = holdings_tables[1]

# extract the number of institutions that have increased or decreased positions
table_rows = list(active_positions_table.children)
increased_row = list(table_rows[0].contents)
decreased_row = list(table_rows[1].contents)

increased_positions = increased_row[1].contents[0]
increased_shares = increased_row[2].contents[0]
decreased_positions = decreased_row[1].contents[0]
decreased_shares = decreased_row[2].contents[0]

# print extracted data to terminal
print(
    f"""Symbol: {symbol}
    Increased Positions: {increased_positions} | Increased Shares: {increased_shares}
    Decreased Positions: {decreased_positions} | Decreased Shares: {decreased_shares}"""
)

# close all Firefox browser instances
driver.quit()