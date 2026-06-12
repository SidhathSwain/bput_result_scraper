import csv
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

MAX_STUDENTS = 450
THROTTLE_DELAY = 1.5 

def get_target_list(filename="results.csv"):
    existing_data = {}
    if os.path.exists(filename):
        with open(filename, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_data[row["REGNO"]] = row

    targets = []
    for i in range(1, MAX_STUDENTS + 1):
        reg_no = f"2401289{i:03d}"
        if reg_no not in existing_data:
            targets.append(reg_no)
        elif existing_data[reg_no]["SGPA"] in ["N/A", "", "None"] or existing_data[reg_no]["NAME"] == "Unknown":
            targets.append(reg_no)
            
    return targets, existing_data

def scrape_missing_bput_results():
    targets, all_student_data = get_target_list()
    
    if not targets:
        print(f"All {MAX_STUDENTS} students have been checked! Nothing to redo.")
        return list(all_student_data.values())
        
    print(f"Found {len(targets)} students to check/redo. Running with safe throttling delays...")

    options = webdriver.EdgeOptions()
    # options.add_argument("--headless") # Uncomment to run silently
    driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 12) 
    
    for reg_no in targets:
        print(f"Processing Registration No: {reg_no}")
        
        try:
            driver.get("https://results.bput.ac.in/")
            time.sleep(THROTTLE_DELAY)
            
            session_select = Select(wait.until(EC.presence_of_element_located((By.ID, "select-Session"))))
            session_select.select_by_value("Even-(2025-26)")
            
            driver.find_element(By.ID, "rollno").send_keys(reg_no)
            driver.find_element(By.ID, "dob").send_keys("2000-01-01")
            driver.find_element(By.ID, "btnViewStudentReseltsList").click()
            
            def data_loaded(d):
                swal = d.find_elements(By.ID, "swal2-title")
                if swal and swal[0].is_displayed():
                    return True
                rows = d.find_elements(By.CSS_SELECTOR, "#tbl-results-list tbody tr")
                return len(rows) > 0

            try:
                wait.until(data_loaded)
            except TimeoutException:
                pass 
                
            time.sleep(0.5)

            swal_popup = driver.find_elements(By.ID, "swal2-title")
            if swal_popup and swal_popup[0].is_displayed() and "Invalid Details" in swal_popup[0].text:
                print(f"  -> Student does not exist.")
                all_student_data[reg_no] = {"REGNO": reg_no, "NAME": "Unknown", "BRANCH": "Unknown", "SGPA": "N/A"}
                try:
                    driver.find_element(By.CSS_SELECTOR, ".swal2-confirm").click()
                    time.sleep(0.5)
                except:
                    pass
                continue
            
            rows = driver.find_elements(By.CSS_SELECTOR, "#tbl-results-list tbody tr")
            clicked_4th_sem = False
            for row in rows:
                if "4th" in row.text.lower() and "semester" in row.text.lower():
                    row.find_element(By.TAG_NAME, "a").click()
                    clicked_4th_sem = True
                    break
            
            if not clicked_4th_sem:
                print(f"  -> No 4th Semester record found for {reg_no}")
                all_student_data[reg_no] = {"REGNO": reg_no, "NAME": "Unknown", "BRANCH": "Unknown", "SGPA": "N/A"}
                continue
                
            wait.until(EC.visibility_of_element_located((By.ID, "lblRollNo")))
            
            try:
                WebDriverWait(driver, 8).until(
                    lambda d: "SGPA" in d.find_element(By.ID, "lblSgpa").text and len(d.find_element(By.ID, "lblSgpa").text.strip()) > 6
                )
            except TimeoutException:
                print(f"  -> Warning: SGPA field loading took too long for {reg_no}, attempting extraction anyway.")
            
            time.sleep(THROTTLE_DELAY)

            name = driver.find_element(By.ID, "lblStudentName").text.strip()
            branch = driver.find_element(By.ID, "lblBranch").text.strip()
            
            sgpa_element = driver.find_element(By.ID, "lblSgpa").text.strip()
            sgpa = sgpa_element.replace("SGPA :", "").strip() if sgpa_element else "N/A"
            
            if name:
                all_student_data[reg_no] = {
                    "REGNO": reg_no,
                    "NAME": name,
                    "BRANCH": branch,
                    "SGPA": sgpa
                }
                print(f"  -> Success: {name} | SGPA: {sgpa}")
                
        except Exception as e:
            print(f"  -> Critical timeout or navigation break on {reg_no}")
            if reg_no not in all_student_data:
                all_student_data[reg_no] = {"REGNO": reg_no, "NAME": "Unknown", "BRANCH": "Unknown", "SGPA": "N/A"}
            
        time.sleep(0.5)

    driver.quit()
    return list(all_student_data.values())

def sort_by_sgpa(data):
    def get_sgpa_value(student):
        try:
            return float(student["SGPA"])
        except ValueError:
            return -1.0 
    return sorted(data, key=get_sgpa_value, reverse=True)

def save_to_csv(data, filename="results.csv"):
    if not data: return
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["REGNO", "NAME", "BRANCH", "SGPA"])
        writer.writeheader()
        writer.writerows(data)
    print(f"\nUpdated {filename} with all records.")

def generate_html_dashboard(data, filename="dashboard.html"):
    if not data: return
    valid_students = [s for s in data if s["NAME"] != "Unknown"]
    
    cards_html = ""
    rank = 1
    for student in valid_students:
        cards_html += f"""
        <div class="card">
            <div class="rank-badge">#{rank}</div>
            <h3>{student['NAME']}</h3>
            <p><strong>Reg No:</strong> <span class="reg">{student['REGNO']}</span></p>
            <p><strong>Branch:</strong> {student['BRANCH']}</p>
            <p class="sgpa">SGPA: {student['SGPA']}</p>
        </div>
        """
        rank += 1

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>4th Semester Results Dashboard</title>
    <style>
        :root {{
            --bg-main: #f4f7f6; --text-main: #333; --text-sub: #555; --card-bg: white;
            --accent: #192f46; --accent-sgpa: #002ED3; --border: #eee; --input-bg: white;
            --input-border: #ccc; --card-shadow: rgba(0,0,0,0.05); --hover-shadow: rgba(0,0,0,0.1);
            --footer-bg: #192f46; --footer-text: #ffffff; --footer-link: #90caf9;
        }}
        body.dark-mode {{
            --bg-main: #121212; --text-main: #f0f0f0; --text-sub: #aaa; --card-bg: #1e1e1e;
            --accent: #90caf9; --accent-sgpa: #64b5f6; --border: #333; --input-bg: #2c2c2c;
            --input-border: #444; --card-shadow: rgba(0,0,0,0.3); --hover-shadow: rgba(0,0,0,0.5);
            --footer-bg: #1a1a1a; --footer-text: #aaaaaa; --footer-link: #64b5f6;
        }}
        
        html, body {{ height: 100%; margin: 0; padding: 0; }}
        body {{ 
            font-family: 'Segoe UI', sans-serif; background-color: var(--bg-main); 
            color: var(--text-main); display: flex; flex-direction: column;
            transition: background-color 0.3s, color 0.3s; 
        }}
        
        .main-content {{ flex: 1 0 auto; padding: 20px; }}
        .header-container {{ display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto 20px auto; }}
        h1 {{ color: var(--accent); margin: 0; text-align: center; flex-grow: 1; }}
        .theme-toggle {{ background: var(--card-bg); color: var(--text-main); border: 1px solid var(--border); padding: 8px 16px; border-radius: 20px; cursor: pointer; font-weight: bold; transition: all 0.2s; }}
        .theme-toggle:hover {{ background: var(--accent); color: var(--bg-main); }}
        .search-container {{ display: flex; justify-content: center; margin-bottom: 30px; }}
        #searchInput {{ width: 100%; max-width: 600px; padding: 15px; font-size: 16px; background-color: var(--input-bg); color: var(--text-main); border: 1px solid var(--input-border); border-radius: 8px; box-shadow: 0 2px 4px var(--card-shadow); outline: none; transition: border-color 0.2s, background-color 0.3s; }}
        #searchInput:focus {{ border-color: var(--accent-sgpa); }}
        .grid-container {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; max-width: 1200px; margin: 0 auto; }}
        .card {{ position: relative; background: var(--card-bg); border-radius: 10px; padding: 25px; box-shadow: 0 4px 6px var(--card-shadow); border-top: 4px solid var(--accent); transition: transform 0.2s, box-shadow 0.2s; }}
        .card:hover {{ transform: translateY(-5px); box-shadow: 0 8px 15px var(--hover-shadow); }}
        .rank-badge {{ position: absolute; top: -10px; right: 15px; background: var(--accent-sgpa); color: white; padding: 5px 10px; border-radius: 20px; font-weight: bold; font-size: 0.9rem; }}
        .card h3 {{ margin: 0 0 15px 0; color: var(--accent); font-size: 1.2rem; border-bottom: 1px solid var(--border); padding-bottom: 10px; padding-right: 30px; }}
        .card p {{ margin: 8px 0; font-size: 0.95rem; color: var(--text-sub); }}
        .sgpa {{ font-weight: bold; color: var(--accent-sgpa) !important; font-size: 1.15rem !important; margin-top: 15px !important; }}
        .no-results {{ text-align: center; grid-column: 1 / -1; font-size: 1.2rem; color: var(--text-sub); display: none; }}
        
        .landing-footer {{
            width: 100%; box-sizing: border-box; background-color: var(--footer-bg);
            color: var(--footer-text); padding: 30px 20px; border-top: 1px solid var(--border);
            transition: background-color 0.3s, color 0.3s; margin-top: auto; 
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            text-align: center; gap: 8px;
        }}
        .landing-footer .footer-content {{ font-size: 0.95rem; letter-spacing: 0.3px; margin: 0; }}
        .landing-footer a {{ color: var(--footer-link); text-decoration: none; font-weight: 500; transition: opacity 0.2s; }}
        .landing-footer a:hover {{ text-decoration: underline; opacity: 0.9; }}
    </style>
</head>
<body>
    <div class="main-content">
        <div class="header-container">
            <div style="width: 100px;"></div>
            <h1>BPUT 4th Semester Results</h1>
            <button class="theme-toggle" onclick="toggleTheme()" id="themeBtn">🌙 Dark Mode</button>
        </div>
        <div class="search-container">
            <input type="text" id="searchInput" placeholder="Search by Name, Registration No, or Branch..." onkeyup="filterCards()">
        </div>
        <div class="grid-container" id="cardsContainer">
            {cards_html}
            <div class="no-results" id="noResultsMsg">No matching students found.</div>
        </div>
    </div>

    <div class="landing-footer">
        <div class="footer-content">
            &copy; 2026 Sidharth Swain. All Rights Reserved.
        </div>
        <div class="footer-content">
            Contact: <a href="mailto:sidharthswain.cse2028@trident.ac.in">sidharthswain.cse2028@trident.ac.in</a>
        </div>
    </div>

    <script>
        if (localStorage.getItem('theme') === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {{
            document.body.classList.add('dark-mode');
            document.getElementById('themeBtn').innerText = '☀️ Light Mode';
        }}
        function toggleTheme() {{
            const body = document.body; const btn = document.getElementById('themeBtn');
            body.classList.toggle('dark-mode');
            if (body.classList.contains('dark-mode')) {{ localStorage.setItem('theme', 'dark'); btn.innerText = '☀️ Light Mode'; }}
            else {{ localStorage.setItem('theme', 'light'); btn.innerText = '🌙 Dark Mode'; }}
        }}
        function filterCards() {{
            const input = document.getElementById('searchInput').value.toLowerCase();
            const cards = document.getElementsByClassName('card'); let visibleCount = 0;
            for (let i = 0; i < cards.length; i++) {{
                const cardText = cards[i].innerText.toLowerCase();
                if (cardText.includes(input)) {{ cards[i].style.display = "block"; visibleCount++; }}
                else {{ cards[i].style.display = "none"; }}
            }}
            document.getElementById('noResultsMsg').style.display = visibleCount === 0 ? "block" : "none";
        }}
    </script>
</body>
</html>
"""
    with open(filename, mode="w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated ranked dashboard at {os.path.abspath(filename)}")

if __name__ == "__main__":
    raw_data = scrape_missing_bput_results()
    sorted_data = sort_by_sgpa(raw_data)
    save_to_csv(sorted_data)
    generate_html_dashboard(sorted_data)
    print("Process Complete Safely.")
