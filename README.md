# BPUT Result Scraper & Dashboard Generator

This tool automates the process of fetching semester results from the BPUT (Biju Patnaik University of Technology) portal using Python and Selenium. It retrieves the target semester's SGPA for a batch of students, saves the data to a CSV file, and generates a fully interactive, searchable HTML dashboard with a Dark Mode toggle.

## Prerequisites

You need Python installed on your system along with the Microsoft Edge browser. The script requires two external Python packages to control the browser.

Install them using pip:
```bash
pip install selenium webdriver-manager
```

## How to Run

1. Save the Python script (e.g., `bput_scraper.py`) in a folder.
2. Open your terminal (or PowerShell).
3. Navigate to the folder where you saved the script.
4. Execute the script:
   ```bash
   python bput_scraper.py
   ```
5. Once finished, you will find `results.csv` and `dashboard.html` in the same directory. Open `dashboard.html` in any web browser to view your ranked leaderboard.

## Customizing the Script for Your Needs

### 1. Changing the Registration Number Format
If you are from a different college or a different batch, your registration numbers will look different (e.g., `230983401` to `230983499`). 

Locate this line in the `get_target_list` function:
```python
reg_no = f"2401289{i:03d}"
```
* **Explanation:** `2401289` is the year and college prefix. `{i:03d}` takes the loop variable `i` and formats it as a 3-digit number (e.g., 001, 002, 010).
* **To Tweak:** If your prefix is `2309834` and your suffix is only 2 digits, change it to:
  ```python
  reg_no = f"2309834{i:02d}" 
  ```

### 2. Changing the Range of Students
By default, the script scans up to a specific limit to save time. 

Find this variable at the top of the script:
```python
MAX_STUDENTS = 450
```
Change `450` to the total number of students in your batch (e.g., `120`, `600`, etc.).

### 3. Semantics: Changing the Semester and Session
The university portal updates its dropdowns every year. You must update the script to match the exact text shown on the BPUT website.

**To change the Session:**
Locate this line:
```python
session_select.select_by_value("Even-(2025-26)")
```
Change `"Even-(2025-26)"` to the exact value attribute of the session you want to check (e.g., `"Odd-(2024-25)"`).

**To change the Semester:**
Locate this block:
```python
if "4th" in row.text.lower() and "semester" in row.text.lower():
```
If you want to pull 2nd Semester results instead, simply change `"4th"` to `"2nd"`.

### 4. Adjusting the Speed (Throttling)
BPUT's servers can be slow. If the script is missing students or crashing, increase the delay buffer.
Find this line at the top:
```python
THROTTLE_DELAY = 1.5 
```
Increase it to `2.0` or `3.0` for a slower, more reliable scrape.

## Responsible Use, Fair Use & Commercialization Disclaimer

This project is intended for educational, research, and personal academic analysis purposes only.

By using this software, you agree to comply with all applicable laws, regulations, and the terms of service of any website or platform accessed through the tool. Users are solely responsible for ensuring that their use of this project is lawful and authorized.

### Fair Use Guidelines

* Only collect data that you are permitted to access.
* Respect website rate limits and avoid excessive automated requests.
* Do not use this tool to disrupt, degrade, or interfere with the operation of university systems or other online services.
* Do not attempt to bypass security controls, authentication mechanisms, or access restrictions.

### Data Privacy

* Academic results and related information may constitute personal or sensitive data.
* Users should obtain appropriate consent before collecting, sharing, publishing, or processing information relating to other individuals.
* Any dashboards, reports, rankings, or analyses generated using this tool should be handled responsibly and in accordance with applicable privacy laws and institutional policies.

### Commercial Use Restrictions

Unless expressly permitted by the data owner and the applicable terms governing the source website, the data collected through this tool must not be:

* Sold, licensed, sublicensed, or redistributed for profit;
* Incorporated into commercial products or paid services;
* Used for advertising, marketing, lead generation, or profiling activities;
* Republished at scale for commercial advantage.

### No Affiliation

This project is an independent tool and is not affiliated with, endorsed by, sponsored by, or officially associated with Biju Patnaik University of Technology (BPUT) or any related institution.

### Disclaimer of Liability

The authors and contributors of this project provide it "as is" without warranties of any kind. They assume no responsibility for misuse of the software, violations of website terms, privacy breaches, inaccurate data, or any legal consequences arising from its use. Users assume all risks and responsibilities associated with operating this tool.

## Safety & Rate Limiting
Please be responsible. Do not set `MAX_STUDENTS` to massive numbers like 10,000 to scrape the entire university, as this may result in your IP address being temporarily blocked by the university's firewall.
