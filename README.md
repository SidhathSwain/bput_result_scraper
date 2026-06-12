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

## Safety & Rate Limiting
Please be responsible. Do not set `MAX_STUDENTS` to massive numbers like 10,000 to scrape the entire university, as this may result in your IP address being temporarily blocked by the university's firewall.
