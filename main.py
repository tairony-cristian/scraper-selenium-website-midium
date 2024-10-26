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
        print("Saving data...")
        time.sleep(2)

        df_new = pd.DataFrame(results)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        df_combined.to_csv(file_name, index=False)

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

# Function to process each month's
def process_month(month, driver):
    url = f"https://medium.com/tag/2023/archive/2023/{month}"
    file_name = f"medium-{month_names[month]}.csv"

    # Load existing data
    if os.path.exists(file_name):
        df_existing = pd.read_csv(file_name)
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
        print("Scrolling to the last saved URL...")
        while True:
            time.sleep(5)
            driver.execute_script("window.scrollBy(0, 1800);")
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
    last_height = driver.execute_script("return document.body.scrollHeight")
    scroll_attempts = 0
    max_scroll_attempts = 3  # Number of scroll attempts without changes

    while True:
        try:
            driver.execute_script("window.scrollBy(0, 2400);")
            time.sleep(scroll_pause_time)

            items = driver.find_elements(By.CSS_SELECTOR, "div.l.c div:nth-child(3) > div")
            if not items:  # Stop if no items found
                break

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

                # Saves every 20 records
                if len(results) >= 20:
                    df_existing, existing_urls_set, existing_urls_list = save_data(results, df_existing, file_name, existing_urls_set, existing_urls_list)

            # Check page height to avoid infinite loops
            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                 scroll_attempts += 1
                 print(f"No change in page height. Attempt {scroll_attempts}/{max_scroll_attempts}.")
            else:
                scroll_attempts = 0  # Restart count if page changed
                
            last_height = new_height

          # If attempts to scroll without changing exceed the limit, stop
            if scroll_attempts >= max_scroll_attempts:
                print("Max scroll attempts reached without any change. Stopping.")
                break  

        except (NoSuchWindowException, TimeoutException) as e:
            print(f"Error encountered: {str(e)}. Restarting browser session...")
            df_existing, existing_urls_set, existing_urls_list = save_data(results, df_existing, file_name, existing_urls_set, existing_urls_list)
            driver.quit()
            driver = create_driver()
            driver.get(url)
            driver.maximize_window()
            last_height = 0

    # Saves remaining data after processing
    if results:
        df_existing, existing_urls_set, existing_urls_list = save_data(results, df_existing, file_name, existing_urls_set, existing_urls_list)

    print(f"Month {month_names[month]} completed.")
    

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

# Initialize the driver
driver = create_driver()
start_time = time.time()  # Start time for time control

# Processes the months of December to January
for month in range(9, 0, -1):
    try:
        print(f"Starting processing for the month {month_names[month]}...")
        process_month(month, driver)
    except Exception as e:
        print(f"Error processing month {month_names[month]}: {str(e)}")

driver.quit()

end_time = time.time()
total_time = end_time - start_time
total_minutes = total_time / 60
print(f"Processing completed! Total time: {total_minutes:.2f} minutes.")
