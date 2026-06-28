from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import os
from datetime import datetime

URL         = "https://coinmarketcap.com/"
TOP_N_COINS = 10
CSV_FILE    = "crypto_prices.csv"
PAGE_WAIT   = 15
HEADLESS    = False


def setup_browser():
    print("")
    print("------------------------------------------------")
    print("  STEP 1 of 6 -> Setting up Chrome browser...")
    print("------------------------------------------------")

    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")
        print("  [INFO] Headless mode ON (no browser window)")
    else:
        print("  [INFO] Browser window will open on screen")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    print("  [OK] Chrome browser is ready!")
    return driver


def open_website(driver):
    print("")
    print("------------------------------------------------")
    print("  STEP 2 of 6 -> Opening CoinMarketCap website...")
    print("------------------------------------------------")

    print(f"  [INFO] URL: {URL}") 
    driver.get(URL)
    print("  [INFO] Waiting for page to fully load...")

    try:
        WebDriverWait(driver, PAGE_WAIT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr"))
        )
        print("  [OK] Page loaded! Coin table is visible.")
    except Exception:
        print("  [WARN] Page took too long. Continuing anyway...")

    print("  [INFO] Waiting 4 seconds for prices to render...")
    time.sleep(4)
    print("  [OK] Ready to scrape!")


def scrape_coins(driver):
    print("")
    print("------------------------------------------------")
    print(f"  STEP 3 of 6 -> Scraping top {TOP_N_COINS} coins...")
    print("------------------------------------------------")

    coins_list = []
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        all_rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        print(f"  [INFO] Found {len(all_rows)} rows on the page")
        print("  [INFO] Extracting data from each row...")
        print("")

        scraped_count = 0
        for row in all_rows:
            if scraped_count >= TOP_N_COINS:
                break
            try:
                rank = row.find_element(By.CSS_SELECTOR, "td:nth-child(2) p").text.strip()
                name = row.find_element(By.CSS_SELECTOR, "p.coin-item-name").text.strip()
                symbol = row.find_element(By.CSS_SELECTOR, "p.coin-item-symbol").text.strip()

                price_raw = row.find_element(By.CSS_SELECTOR, "td:nth-child(4)").text.strip()
                price_clean = price_raw.replace("$", "").replace(",", "")
                try:
                    price_num = float(price_clean)
                    price_str = f"${price_num:,.2f}"
                except ValueError:
                    price_num = 0.0
                    price_str = price_raw

                change_raw = row.find_element(By.CSS_SELECTOR, "td:nth-child(5) span").text.strip()
                change_clean = change_raw.replace("%", "")
                try:
                    change_num = float(change_clean)
                    change_str = f"{change_num:+.2f}%"
                except ValueError:
                    change_num = 0.0
                    change_str = change_raw

                market_cap = row.find_element(By.CSS_SELECTOR, "td:nth-child(8)").text.strip()

                coin = {
                    "Rank": rank, "Name": name, "Symbol": symbol,
                    "Price_USD": price_str, "Change_24h": change_str,
                    "Market_Cap": market_cap, "Timestamp": now,
                }
                coins_list.append(coin)
                scraped_count += 1

                trend = "UP" if change_num >= 0 else "DOWN"
                print(f"  #{rank:<3} {name:<15} ({symbol:<5})  Price: {price_str:<14}  24h: {change_str:<9} [{trend}]")

            except Exception:
                continue

    except Exception as e:
        print(f"  [ERROR] Could not read table: {e}")

    print("")
    print(f"  [OK] Done! Scraped {len(coins_list)} coins successfully.")
    return coins_list


def save_csv(coins_list):
    print("")
    print("------------------------------------------------")
    print("  STEP 4 of 6 -> Saving data to CSV file...")
    print("------------------------------------------------")

    if not coins_list:
        print("  [WARN] No data to save.")
        return None

    df = pd.DataFrame(coins_list)
    print(f"  [INFO] DataFrame shape: {df.shape[0]} rows x {df.shape[1]} columns")

    file_already_exists = os.path.isfile(CSV_FILE)
    if file_already_exists:
        df.to_csv(CSV_FILE, mode="a", header=False, index=False)
        print(f"  [OK] Data APPENDED to existing file: {CSV_FILE}")
    else:
        df.to_csv(CSV_FILE, mode="w", header=True, index=False)
        print(f"  [OK] New file CREATED: {CSV_FILE}")

    print(f"  [INFO] File location: {os.path.abspath(CSV_FILE)}")
    return df


def analyse_data(df):
    print("")
    print("------------------------------------------------")
    print("  STEP 5 of 6 -> Analysing market data...")
    print("------------------------------------------------")

    if df is None or df.empty:
        print("  [WARN] No data to analyse.")
        return

    df["Change_Num"] = (
        df["Change_24h"].str.replace("%", "", regex=False)
        .str.replace("+", "", regex=False).astype(float)
    )

    gainers = df.nlargest(3, "Change_Num")[["Name", "Symbol", "Price_USD", "Change_24h"]]
    print("")
    print("  TOP 3 GAINERS:")
    for _, row in gainers.iterrows():
        print(f"     {row['Name']:<15} {row['Symbol']:<6}  {row['Price_USD']:<14}  {row['Change_24h']}")

    losers = df.nsmallest(3, "Change_Num")[["Name", "Symbol", "Price_USD", "Change_24h"]]
    print("")
    print("  TOP 3 LOSERS:")
    for _, row in losers.iterrows():
        print(f"     {row['Name']:<15} {row['Symbol']:<6}  {row['Price_USD']:<14}  {row['Change_24h']}")

    up_count = len(df[df["Change_Num"] > 0])
    down_count = len(df[df["Change_Num"] < 0])
    flat_count = len(df[df["Change_Num"] == 0])

    print("")
    print(f"  MARKET SUMMARY:")
    print(f"     Coins UP   : {up_count}")
    print(f"     Coins DOWN : {down_count}")
    print(f"     Coins FLAT : {flat_count}")
    print(f"     Total      : {len(df)}")
    print("")
    print("  [OK] Analysis complete!")


def print_summary(coins_list):
    print("")
    print("------------------------------------------------")
    print("  STEP 6 of 6 -> Printing final summary table...")
    print("------------------------------------------------")

    if not coins_list:
        print("  [WARN] No data to display.")
        return

    print("")
    print("=" * 80)
    print(f"  {'#':<4} {'Coin Name':<16} {'Symbol':<7} {'Price (USD)':<15} {'24h Change':<12} Market Cap")
    print("=" * 80)

    for coin in coins_list:
        try:
            chg = float(coin["Change_24h"].replace("%","").replace("+",""))
            arrow = "UP" if chg >= 0 else "DOWN"
        except:
            arrow = " "
        print(f"  {coin['Rank']:<4} {coin['Name']:<16} {coin['Symbol']:<7} "
              f"{coin['Price_USD']:<15} {coin['Change_24h']:<10} {arrow:<5} {coin['Market_Cap']}")

    print("=" * 80)
    print(f"  Scraped at: {coins_list[0]['Timestamp']}")
    print("=" * 80)


def main():
    print("")
    print("=" * 55)
    print("   CRYPTOCURRENCY PRICE TRACKER")
    print("   Source: CoinMarketCap.com")
    print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Target: Top {TOP_N_COINS} cryptocurrencies")
    print(f"   Output: {CSV_FILE}")
    print("=" * 55)

    driver = None
    try:
        driver = setup_browser()
        open_website(driver)
        coins_list = scrape_coins(driver)
        df = save_csv(coins_list)
        analyse_data(df)
        print_summary(coins_list)

        print("")
        print("=" * 55)
        print("   ALL DONE! Project completed successfully.")
        print(f"   Open '{CSV_FILE}' to see your data.")
        print("   Open 'dashboard.html' in browser for charts.")
        print("=" * 55)
        print("")

    except KeyboardInterrupt:
        print("")
        print("  [WARN] Script stopped by user.")
    except Exception as e:
        print("")
        print(f"  [ERROR] Something went wrong: {e}")
        print("  [TIP] Check your internet connection and try again.")
    finally:
        if driver:
            print("")
            print("  [INFO] Closing Chrome browser...")
            driver.quit()
            print("  [OK] Browser closed cleanly.")


if __name__ == "__main__":
    main()
