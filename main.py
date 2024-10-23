
#---------------------------- salva os arquivos de mes em mes ----------------------------------------

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchWindowException
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

# Function to save data and display total records
def save_data(results, df_existing, file_name, existing_urls_set, existing_urls_list):
    if results:
        df_new = pd.DataFrame(results)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.to_excel(file_name, index=False)

        total_saved = len(df_combined)
        print(f"Saving {len(results)} new items. Total of {total_saved} items saved to file.")

        df_existing = df_combined
        results.clear()

    return df_existing, existing_urls_set, existing_urls_list

# Function to create a new Chrome session
def create_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_script_timeout(30)
    return driver

# Function to process each month's URL
def process_month(month, driver):
    url = f"https://medium.com/tag/2023/archive/2023/{month}"
    file_name = f"medium-{month_names[month]}.xlsx"

    if os.path.exists(file_name):
        df_existing = pd.read_excel(file_name)
        # Store URLs in both a set (for fast lookup) and a list (to preserve order)
        existing_urls_list = df_existing['URL'].tolist()
        existing_urls_set = set(existing_urls_list)
        print(f"{len(df_existing)} items already saved for the month {month_names[month]}.")
    else:
        df_existing = pd.DataFrame(columns=['Author', 'Title', 'Content', 'Date', 'URL'])
        existing_urls_list = []
        existing_urls_set = set()

    driver.get(url)
    driver.maximize_window()

    # Scroll to last saved URL
    if existing_urls_list:
        scroll_pause_time = 5
        scroll_amount = 1800
        print("Scrolling to the last saved URL...")
        while True:
            time.sleep(scroll_pause_time)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")

            # Check if last URL is visible
            items = driver.find_elements(By.CSS_SELECTOR, "div.l.c div:nth-child(3) > div")
            for item in items:
                try:
                    current_url = item.find_element(By.CSS_SELECTOR, 'div:nth-child(2) > div.l.es.ln > div > a').get_attribute('href')
                    if current_url == existing_urls_list[-1]:
                        print("Reached the last saved URL. Resuming from there...")
                        break
                except Exception:
                    continue
            break

    results = []
    scroll_pause_time = 5
    scroll_amount = 1800
    total_saved_in_session = 0

    while True:
        try:
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(scroll_pause_time)

            items = driver.find_elements(By.CSS_SELECTOR, "div.l.c div:nth-child(3) > div")

            for item in items:
                data = {}
                try:
                    data['Author'] = item.find_element(By.CSS_SELECTOR, 'div:nth-child(1) > div > div:nth-child(1) > div > div.lf.l > div > div > a > p').text
                except Exception:
                    data['Author'] = None
                try:
                    data['Title'] = item.find_element(By.CSS_SELECTOR, "h2").text
                except Exception:
                    data['Title'] = None
                try:
                    data['Content'] = item.find_element(By.CSS_SELECTOR, "h3").text
                except Exception:
                    data['Content'] = None
                try:
                    data['Date'] = item.find_element(By.CSS_SELECTOR, "div:nth-child(1) > div > div:nth-child(2) > div.l.es.ln > div.h.k.j > div > span > div > div.ab.q.nm > span").text
                except Exception:
                    data['Date'] = None
                try:
                    data['URL'] = item.find_element(By.CSS_SELECTOR, 'div:nth-child(2) > div.l.es.ln > div > a').get_attribute('href')
                except Exception:
                    data['URL'] = None

                if data.get('URL') and data['URL'] not in existing_urls_set:
                    results.append(data)
                    existing_urls_set.add(data['URL'])
                    existing_urls_list.append(data['URL'])
                    total_saved_in_session += 1

                if len(results) >= 100:  # Save every 100 records
                    df_existing, existing_urls_set, existing_urls_list = save_data(results, df_existing, file_name, existing_urls_set, existing_urls_list)

            new_height = driver.execute_script("return document.body.scrollHeight")
            last_height = new_height

        except (NoSuchWindowException, TimeoutException) as e:
            print(f"Error encountered: {str(e)}. Restarting browser session...")
            df_existing, existing_urls_set, existing_urls_list = save_data(results, df_existing, file_name, existing_urls_set, existing_urls_list)
            driver.quit()
            driver = create_driver()
            driver.get(url)
            driver.maximize_window()
            last_height = 0

        # Stop scrolling if no more items are loaded
        if len(items) == 0:
            break

    # Save any remaining data after processing
    if results:
        df_existing, existing_urls_set, existing_urls_list = save_data(results, df_existing, file_name, existing_urls_set, existing_urls_list)

    print(f"Month {month_names[month]} completed. Total saved in this session: {total_saved_in_session}")

# Month mapping
month_names = {
    12: "december",
    11: "november",
    10: "october",
    9: "september",
    8: "august",
    7: "july",
    6: "june",
    5: "may",
    4: "april",
    3: "march",
    2: "february",
    1: "january"
}

# Initialize driver
driver = create_driver()

# Process months from December to January
for month in range(12, 0, -1):
    try:
        process_month(month, driver)
    except Exception as e:
        print(f"Error processing month {month_names[month]}: {str(e)}")

driver.quit()

