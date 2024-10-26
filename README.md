# Web Scraping Automation with Selenium and Pandas

This project is a Python-based web scraper that extracts data from Medium's archive pages, saves the content in CSV files, and handles various exceptions during the scraping process. It uses Selenium for browser automation and Pandas for data manipulation. The scraper processes multiple months' worth of Medium articles and efficiently stores the data in CSV format.

## Table of Contents
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Customization](#customization)
- [Project Structure](#project-structure)
- [Error Handling](#error-handling)
- [Contributing](#contributing)
- [License](#license)

## Features
- Web scraping of articles from Medium by month.
- Extracted information includes: **Author**, **Title**, **Content**, **Date**, and **URL**.
- Saves data incrementally in CSV files.
- Handles browser exceptions (timeouts, window errors) and restarts sessions if necessary.
- Automatically scrolls through the page to detect new content.
- Stops scraping after a set number of attempts if no new content is found.

## Technologies Used
- **Python:** Version 3.x
- **Selenium:** For web browser automation.
- **Pandas:** For data manipulation and saving data to CSV files.
- **webdriver_manager:** Automatically manages the ChromeDriver installation for Selenium.

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/tairony-cristian/scraper-selenium-website-midium.git
    ```

2. **Create a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # For Linux/macOS
    venv\Scripts\activate     # For Windows
    ```

3. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Ensure Chrome is installed on your machine, as Selenium will use ChromeDriver for automation.**

## Usage

1. **Run the script:**
    ```bash
    python main.py
    ```

2. The script will automatically start scraping articles from Medium’s archive pages for the months specified. 

Data for each month will be saved in separate CSV files named after the corresponding month (e.g., `medium-september.csv`, `medium-august.csv`).

## Customization

You can modify the range of months to be scraped by adjusting the loop in the main section of `main.py`:

```python
for month in range(12, 0, -1):
    ...
```

## Project Structure
├── main.py                  # Main script for web scraping
├── requirements.txt         # Required Python libraries
├── README.md                # Project documentation


## Error Handling
Timeouts and NoSuchWindowException are handled during the scraping process. If encountered, the browser session will restart automatically.
After a set number of failed scroll attempts (default is 3), the script will stop scraping for that month and move on to the next one.

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests to improve the functionality, performance, or error handling of the scraper.

## License
This project is licensed under the MIT License.