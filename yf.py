from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common import TimeoutException
import sys
import csv

def scrape_stock(driver, ticker_symbol):
    # URL of the target page
    url = f'https://finance.yahoo.com/quote/{ticker_symbol}'

    # visit the target page
    driver.get(url)

    try:
        # wait up to 5 seconds for the consent modal to show up
        consent_overlay = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.consent-overlay')))

        # click the 'Accept all' button
       # accept_all_button = consent_overlay.find_element(By.CSS_SELECTOR, '.accept-all')
       # accept_all_button.click()
    except TimeoutException:
        print('Cookie consent overlay missing')

    # the data collected from the target page
    stock = { 'ticker': ticker_symbol }

    # scraping the stock data from the price indicators
    regular_market_price = driver \
        .find_element(By.CSS_SELECTOR, f'[data-symbol="{ticker_symbol}"][data-field="regularMarketPrice"]') \
        .text
    regular_market_change = driver \
        .find_element(By.CSS_SELECTOR, f'[data-symbol="{ticker_symbol}"][data-field="regularMarketChange"]') \
        .text
    regular_market_change_percent = driver \
        .find_element(By.CSS_SELECTOR, f'[data-symbol="{ticker_symbol}"][data-field="regularMarketChangePercent"]') \
        .text \
        .replace('(', '').replace(')', '')

    stock['regular_market_price'] = regular_market_price
    stock['regular_market_change'] = regular_market_change
    stock['regular_market_change_percent'] = regular_market_change_percent

    # scraping the stock data from the "Summary" table
    previous_close = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="PREV_CLOSE-value"]').text
    open_value = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="OPEN-value"]').text
    bid = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="BID-value"]').text
    ask = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="ASK-value"]').text
    days_range = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="DAYS_RANGE-value"]').text
    week_range = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="FIFTY_TWO_WK_RANGE-value"]').text
    volume = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="TD_VOLUME-value"]').text
    avg_volume = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="AVERAGE_VOLUME_3MONTH-value"]').text
    market_cap = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="MARKET_CAP-value"]').text
    beta = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="BETA_5Y-value"]').text
    pe_ratio = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="PE_RATIO-value"]').text
    eps = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="EPS_RATIO-value"]').text
    earnings_date = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="EARNINGS_DATE-value"]').text
    dividend_yield = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="DIVIDEND_AND_YIELD-value"]').text
    ex_dividend_date = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="EX_DIVIDEND_DATE-value"]').text
    year_target_est = driver.find_element(By.CSS_SELECTOR, '#quote-summary [data-test="ONE_YEAR_TARGET_PRICE-value"]').text

    stock['previous_close'] = previous_close
    stock['open_value'] = open_value
    stock['bid'] = bid
    stock['ask'] = ask
    stock['days_range'] = days_range
    stock['week_range'] = week_range
    stock['volume'] = volume
    stock['avg_volume'] = avg_volume
    stock['market_cap'] = market_cap
    stock['beta'] = beta
    stock['pe_ratio'] = pe_ratio
    stock['eps'] = eps
    stock['earnings_date'] = earnings_date
    stock['dividend_yield'] = dividend_yield
    stock['ex_dividend_date'] = ex_dividend_date
    stock['year_target_est'] = year_target_est

    return stock

# if there are no CLI params
if len(sys.argv) <= 1:
    print('Ticker symbol CLI argument missing!')
    sys.exit(2)

options = Options()
options.add_argument('--headless=new')

# initialize a web driver instance to control a Chrome window
driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install()),
    options=options
)

# the array containing all scraped data
stocks = []

# scraping all market securities
for ticker_symbol in sys.argv[1:]:
    stocks.append(scrape_stock(driver, ticker_symbol))

# close the browser and free up the resources
driver.quit()

# to use it as the header of the output CSV file
csv_header = stocks[0].keys()

# export the scraped data to CSV
with open('stocks-scraped.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, csv_header)
    dict_writer.writeheader()
    dict_writer.writerows(stocks)