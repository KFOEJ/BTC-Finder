import time
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import init, Fore, Back

counter = 0  # Initialize the counter

# Initialize colorama
init(autoreset=True)

# Suppress TensorFlow Lite warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
logging.getLogger('tensorflow').setLevel(logging.FATAL)

# Set up headed Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless=new")  # Uncomment for headless mode
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=chrome_options)

try:
    driver.get("https://privatekeys.pw/keys/bitcoin/1")
    print(f"{Fore.LIGHTBLUE_EX}🌐 Navigated to: {driver.current_url}")

    # Handle consent button
    try:
        consent_button = driver.find_element(By.CLASS_NAME, "fc-button-label")
        consent_button.click()
        print(f"{Fore.GREEN}✔️ Consent button clicked.")
    except NoSuchElementException:
        print(f"{Fore.RED}❌ Consent button not found.")

    while True:
        time.sleep(0.6)  # 120 requests/min max

        # Increment the counter for each iteration
        counter += 1

        # Initialize balance as 0
        final_balance = "0 BTC"

        # Close Google ad if it appears
        try:
            ad_close_button = driver.find_element(By.CSS_SELECTOR, "div#dismiss-button[aria-label='Close ad']")
            ad_close_button.click()
            print(f"{Fore.YELLOW}⚠️ Google ad detected and closed.")
            time.sleep(1)  # Wait a bit before continuing
        except NoSuchElementException:
            pass  # No ad detected, continue the process

        # Attempt to close overlay if present
        try:
            overlay = driver.find_element(By.CLASS_NAME, "fc-dialog-overlay")
            if overlay.is_displayed():
                print(f"{Fore.CYAN}⚠️ Overlay detected. Attempting to close...")
                close_button = driver.find_element(By.CLASS_NAME, "fc-close")
                close_button.click()
                time.sleep(1)
        except:
            pass  # No overlay detected

        # Wait for iframe to disappear if it's blocking the element
        try:
            WebDriverWait(driver, 5).until(EC.invisibility_of_element_located((By.ID, "aswift_2")))
            print(f"{Fore.GREEN}✔️ Iframe ad disappeared.")
        except TimeoutException:
            print(f"{Fore.RED}❌ Timeout while waiting for iframe to disappear.")
            try:
                # Try to click the iframe close button directly if still present
                iframe_close_button = driver.find_element(By.CSS_SELECTOR, "div#dismiss-button[aria-label='Close ad']")
                iframe_close_button.click()
                print(f"{Fore.YELLOW}⚠️ Iframe close button clicked directly.")
            except NoSuchElementException:
                pass  # If no iframe close button, continue

        # Scroll to the Random button to bring it into view
        try:
            random_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Random"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", random_button)
            time.sleep(0.5)

            # Attempt to click using JavaScript if not clickable by normal means
            driver.execute_script("arguments[0].click();", random_button)
            time.sleep(0.6)
            current_url = driver.current_url
            print(f"{Fore.LIGHTBLUE_EX}🌐 Navigated to: {current_url}")
        except ElementClickInterceptedException as e:
            print(f"{Fore.RED}❌ Error clicking Random button: {str(e)}")
            continue

        # Check BTC balance
        try:
            final_balance_element = driver.find_element(
                By.CSS_SELECTOR,
                ".js-balances-bitcoin .final"
            )
            final_balance = final_balance_element.text.strip().replace('BTC', '').strip()
            print(f"{Fore.YELLOW}💰 BTC Balance found: {Fore.GREEN}{final_balance} BTC")

            if final_balance not in ["", "0"]:
                # Save URL with balance
                with open("positive_balances.txt", "a") as f:
                    f.write(f"{current_url} | Balance: {final_balance} BTC\n")
                print(f"{Fore.MAGENTA}✅ Balance > 0. URL saved: {Fore.LIGHTBLUE_EX}{current_url}")
        except NoSuchElementException:
            print(f"{Fore.RED}❌ No BTC balance found on the page.")

        # Display the rolling counter and balance with background color
        print(f"{Back.LIGHTCYAN_EX}{Fore.BLACK}🔁 Checked: {counter} | 💸 Balance: {final_balance} BTC{Back.RESET}")

except KeyboardInterrupt:
    print(f"{Fore.RED}\n🛑 Script interrupted by user.")
finally:
    driver.quit()
    print(f"{Fore.CYAN}🔚 Browser closed.")
