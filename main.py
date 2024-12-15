from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import time

last_order = None
monitor_timer = 600 # In seconds
timeout_timer = 60 # In seconds


def setup_driver():
    options = FirefoxOptions()
    options.add_argument('--headless')
    driver = webdriver.Firefox(options=options)
    return driver


def get_last_order(driver):
    wait = WebDriverWait(driver, 10)
    table = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table")))
    table_rows = table.find_elements(By.TAG_NAME, "tr")[1:]

    if not table_rows:
        return None

    cells = table_rows[0].find_elements(By.TAG_NAME, "td")
    return {
        'order_id': cells[0].text,
        'type': cells[1].text,
        'sell_amount': cells[2].text,
        'buy_amount': cells[3].text,
        'status': cells[7].text
    }


def monitor_transactions(monitor_wallet_address):
    global last_order

    while True:
        try:
            driver = setup_driver()
            url = f"https://explorer.cow.fi/address/{monitor_wallet_address}"
            driver.get(url)
            current_order = get_last_order(driver)

            if not current_order:
                print(f"Error occurred at {time.strftime('%Y-%m-%d %H:%M:%S')} - couldn't fetch data.")
            if not last_order:
                last_order = current_order
                print(f"Initial order ID set: {last_order['order_id']}")
            elif current_order['order_id'] != last_order['order_id']:
                print(
                    f'New order detected at {time.strftime('%Y-%m-%d %H:%M:%S')}!\n'
                    f'Order ID: {current_order['order_id']}\n'
                    f'Type: {current_order['type']}\n'
                    f'Sell Amount: {current_order['sell_amount'].replace('\n', ' ')}\n'
                    f'Buy Amount: {current_order['buy_amount'].replace('\n', ' ')}\n'
                    f'Status: {current_order['status']}')
                last_order = current_order

            time.sleep(monitor_timer)
        except KeyboardInterrupt:
            print("Exiting...")
            exit(0)
        except Exception as e:
            print(f"Error occurred at {time.strftime('%Y-%m-%d %H:%M:%S')} - {e}")
            time.sleep(timeout_timer)
        finally:
            driver.quit()


if __name__ == "__main__":
    wallet_address = "0x5be9a4959308A0D0c7bC0870E319314d8D957dBB"
    print(f"Starting monitoring at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    monitor_transactions(wallet_address)