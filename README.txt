╔══════════════════════════════════════════════════════╗
║      CRYPTOCURRENCY PRICE TRACKER — FULL GUIDE      ║
║      Project by: Swetha                              ║
╚══════════════════════════════════════════════════════╝


PROJECT FILES YOU NEED:
─────────────────────────────────────────────────────
  crypto_tracker.py  → Main Python scraper
  dashboard.html     → Visual dashboard
  requirements.txt   → Library list
  README.txt         → This file


STEP 1 — INSTALL LIBRARIES
─────────────────────────────────────────────────────
Open VS Code → press Ctrl + ` to open Terminal
Type this and press Enter:

   pip install selenium webdriver-manager pandas

Wait until you see "Successfully installed"


STEP 2 — RUN THE PYTHON SCRIPT
─────────────────────────────────────────────────────
In VS Code Terminal type:

   python crypto_tracker.py

What happens:
  → Chrome opens automatically
  → Goes to coinmarketcap.com
  → Scrapes Top 10 coins
  → Saves crypto_prices.csv file
  → Prints results in terminal
  → Chrome closes


STEP 3 — VIEW THE DASHBOARD
─────────────────────────────────────────────────────
1. Find dashboard.html in your folder
2. Right-click → Open with Chrome
3. Click the "Load CSV File" button
4. Select crypto_prices.csv
5. Dashboard loads with:
     ✅ 4 stat cards (total, price, gainers, losers)
     ✅ Full coin table with search box
     ✅ Bar chart for 24h changes
     ✅ Donut chart for market sentiment
     ✅ Top 5 Gainers list
     ✅ Top 5 Losers list


TROUBLESHOOTING
─────────────────────────────────────────────────────
Problem: ModuleNotFoundError
Fix:     pip install selenium webdriver-manager pandas

Problem: Chrome doesn't open
Fix:     Make sure Google Chrome is installed

Problem: No data / timeout error
Fix:     Check internet connection, run script again

Problem: Dashboard shows nothing
Fix:     Run Python script first, then load CSV


TECHNOLOGIES USED:
─────────────────────────────────────────────────────
  Python           → main language
  Selenium         → opens and controls Chrome
  webdriver_manager→ auto-installs ChromeDriver
  pandas           → saves data to CSV
  HTML + CSS + JS  → dashboard visuals

╔══════════════════════════════════════════════════════╗
║  Run script → Load CSV → See Dashboard  ✅           ║
╚══════════════════════════════════════════════════════╝