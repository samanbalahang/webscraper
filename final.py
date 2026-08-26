import os
import csv
import time

from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    StaleElementReferenceException,
)


# ============================================================
# CONFIG
# ============================================================

load_dotenv()

USERNAME = os.getenv("VIC_USERNAME")
PASSWORD = os.getenv("VIC_PASSWORD")

if not USERNAME:
    raise RuntimeError("VIC_USERNAME is missing from .env")

if not PASSWORD:
    raise RuntimeError("VIC_PASSWORD is missing from .env")


BASE_URL = "https://vic.ir"

PROVINCE_URL = "https://vic.ir/company/province"

MAX_COMPANIES_PER_PROVINCE = 1000

# Province processing settings.
# 1 = start from the first province
# 2 = start from the second province
# 3 = start from the third province, etc.
start_Provincy = 1

# If True, create one CSV file for each province.
# If False, create only one CSV file: province_1.csv
separate_Provinces = True

# $ is replaced with the province number.
file_template = "province_$"

if start_Provincy < 1:
    raise ValueError("start_Provincy must be 1 or greater.")

if "$" not in file_template:
    raise ValueError("file_template must contain '$'.")

MAX_RETRIES = 3

PAGE_TIMEOUT = 30

RETRY_WAIT = 5

OUTPUT_DIRECTORY = os.path.dirname(__file__)


# ============================================================
# DRIVER
# ============================================================

driver_path = os.path.join(
    os.path.dirname(__file__),
    "geckodriver.exe"
)

service = Service(driver_path)

driver = webdriver.Firefox(
    service=service
)

wait = WebDriverWait(
    driver,
    PAGE_TIMEOUT
)


# ============================================================
# HELPERS
# ============================================================

def clean_text(text):
    """
    Remove unnecessary whitespace.
    """

    if text is None:
        return ""

    return " ".join(text.split())


def wait_for_page():
    """
    Wait until the browser reports that the document
    has finished loading.
    """

    WebDriverWait(
        driver,
        PAGE_TIMEOUT
    ).until(
        lambda d: d.execute_script(
            "return document.readyState"
        ) == "complete"
    )


# ============================================================
# LOGIN STATUS
# ============================================================

def is_logged_in():
    """
    Check whether the current page shows the logged-in user.

    Logged in:
        کتیبه ناجی

    Logged out:
        عضویت
    """

    try:

        user_caption = driver.find_element(
            By.ID,
            "UserNameCaption"
        )

        text = clean_text(
            user_caption.text
        )

        print(
            f"Login status: [{text}]"
        )

        return text == "کتیبه ناجی"

    except (
        TimeoutException,
        WebDriverException,
        StaleElementReferenceException
    ):

        print(
            "Could not find UserNameCaption."
        )

        return False


# ============================================================
# OPEN URL
# ============================================================

def open_url(
    url,
    expected_selector=None,
    retries=MAX_RETRIES,
    check_login=True
):
    """
    Open URL.

    Before opening a URL, check whether the session
    is still logged in.

    If logged out:
        login again

    After navigation, check login again.
    """

    for attempt in range(1, retries + 1):

        try:

            # =================================================
            # CHECK LOGIN BEFORE NAVIGATION
            # =================================================

            if check_login:

                if not is_logged_in():

                    print()
                    print(
                        "Session is NOT logged in."
                    )

                    print(
                        "Logging in again..."
                    )

                    if not login():

                        raise Exception(
                            "Login failed."
                        )

                    if not is_logged_in():

                        raise Exception(
                            "Login verification failed."
                        )

                    print(
                        "Re-login successful."
                    )

            # =================================================
            # OPEN URL
            # =================================================

            print()
            print(
                f"Opening ({attempt}/{retries}):"
            )

            print(
                url
            )

            driver.get(url)

            wait_for_page()

            # Give website time to populate content.
            time.sleep(2)

            # =================================================
            # CHECK LOGIN AFTER NAVIGATION
            # =================================================

            if check_login:

                if not is_logged_in():

                    print()
                    print(
                        "Session expired after "
                        "opening this URL."
                    )

                    print(
                        "Logging in again..."
                    )

                    if not login():

                        raise Exception(
                            "Re-login failed."
                        )

                    if not is_logged_in():

                        raise Exception(
                            "Still not logged in."
                        )

                    # Re-open requested URL.
                    print(
                        "Re-opening requested URL..."
                    )

                    driver.get(url)

                    wait_for_page()

                    time.sleep(2)

                    if not is_logged_in():

                        raise Exception(
                            "Still not logged in."
                        )

            # =================================================
            # CHECK EXPECTED ELEMENT
            # =================================================

            if expected_selector:

                WebDriverWait(
                    driver,
                    PAGE_TIMEOUT
                ).until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            expected_selector
                        )
                    )
                )

            print(
                "Page loaded successfully."
            )

            return True

        except (
            TimeoutException,
            WebDriverException,
            StaleElementReferenceException,
            Exception,
        ) as e:

            print()
            print(
                "Page validation failed:"
            )

            print(
                f"{type(e).__name__}: {e}"
            )

            if attempt < retries:

                print(
                    f"Waiting {RETRY_WAIT} seconds "
                    f"before retry..."
                )

                time.sleep(RETRY_WAIT)

            else:

                print(
                    "Maximum retries reached."
                )

    return False


# ============================================================
# LOGIN
# ============================================================

def login():

    print()
    print(
        "========================================"
    )

    print(
        "LOGIN"
    )

    print(
        "========================================"
    )

    # IMPORTANT:
    #
    # check_login=False
    #
    # Otherwise open_url() would call login()
    # again and create recursive login calls.

    if not open_url(
        PROVINCE_URL,
        expected_selector=".login",
        check_login=False
    ):

        print(
            "Could not open province page."
        )

        return False

    # ========================================================
    # CLICK .login
    # ========================================================

    print(
        "Clicking .login..."
    )

    try:

        login_button = wait.until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    ".login"
                )
            )
        )

        driver.execute_script(
            """
            arguments[0].scrollIntoView({
                block: 'center'
            });
            """,
            login_button
        )

        driver.execute_script(
            "arguments[0].click();",
            login_button
        )

    except Exception as e:

        print(
            "Could not click .login:"
        )

        print(
            repr(e)
        )

        return False

    time.sleep(1)

    # ========================================================
    # USERNAME
    # ========================================================

    print(
        "Waiting for username..."
    )

    try:

        email = wait.until(
            EC.visibility_of_element_located(
                (
                    By.ID,
                    "Email"
                )
            )
        )

        driver.execute_script(
            """
            arguments[0].scrollIntoView({
                block: 'center'
            });
            """,
            email
        )

        email.click()

        email.clear()

        email.send_keys(
            USERNAME
        )

        print(
            "Username entered."
        )

    except Exception as e:

        print(
            "Could not enter username:"
        )

        print(
            repr(e)
        )

        return False

    # ========================================================
    # PASSWORD
    # ========================================================

    print(
        "Waiting for password..."
    )

    try:

        password = wait.until(
            EC.visibility_of_element_located(
                (
                    By.ID,
                    "Password"
                )
            )
        )

        driver.execute_script(
            """
            arguments[0].scrollIntoView({
                block: 'center'
            });
            """,
            password
        )

        password.click()

        password.clear()

        password.send_keys(
            PASSWORD
        )

        print(
            "Password entered."
        )

    except Exception as e:

        print(
            "Could not enter password:"
        )

        print(
            repr(e)
        )

        return False

    # ========================================================
    # SUBMIT
    #
    # <input type="submit" value="ورود">
    # ========================================================

    print(
        "Waiting for ورود button..."
    )

    try:

        login_submit = wait.until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    'input[type="submit"][value="ورود"]'
                )
            )
        )

        driver.execute_script(
            """
            arguments[0].scrollIntoView({
                block: 'center'
            });
            """,
            login_submit
        )

        time.sleep(0.5)

        print(
            "Clicking ورود..."
        )

        driver.execute_script(
            "arguments[0].click();",
            login_submit
        )

        print(
            "Login button clicked."
        )

    except Exception as e:

        print(
            "Could not click login submit:"
        )

        print(
            repr(e)
        )

        return False

    # ========================================================
    # WAIT FOR LOGIN NAVIGATION
    # ========================================================

    try:

        wait_for_page()

    except TimeoutException:

        print(
            "Login navigation timed out."
        )

    time.sleep(3)

    print(
        "Current URL:"
    )

    print(
        driver.current_url
    )

    # ========================================================
    # VERIFY LOGIN
    # ========================================================

    if is_logged_in():

        print(
            "LOGIN SUCCESSFUL."
        )

        return True

    print(
        "LOGIN VERIFICATION FAILED."
    )

    return False


# ============================================================
# GET PROVINCE URLS
# ============================================================

def get_province_urls():

    print()
    print(
        "========================================"
    )

    print(
        "GETTING PROVINCES"
    )

    print(
        "========================================"
    )

    if not open_url(
        PROVINCE_URL,
        expected_selector="li.Province a"
    ):

        raise RuntimeError(
            "Could not load province list."
        )

    province_elements = driver.find_elements(
        By.CSS_SELECTOR,
        "li.Province a"
    )

    provinces = []

    for element in province_elements:

        try:

            name = clean_text(
                element.text
            )

            href = element.get_attribute(
                "href"
            )

            if not href:
                continue

            if href.startswith("/"):
                href = BASE_URL + href

            provinces.append(
                {
                    "name": name,
                    "url": href
                }
            )

        except StaleElementReferenceException:

            continue

    print(
        f"Found {len(provinces)} provinces."
    )

    return provinces


# ============================================================
# GET COMPANY URLS
# ============================================================

def get_company_urls(province):

    print()
    print(
        "----------------------------------------"
    )

    print(
        f"Province: {province['name']}"
    )

    print(
        f"URL: {province['url']}"
    )

    print(
        "----------------------------------------"
    )

    # ========================================================
    # OPEN PROVINCE
    # ========================================================

    if not open_url(
        province["url"],
        expected_selector=(
            "div.main_content"
        )
    ):

        print(
            f"Could not load province: "
            f"{province['name']}"
        )

        return []

    # ========================================================
    # CHECK main_content
    # ========================================================

    try:

        main_content = wait.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "div.main_content"
                )
            )
        )

        # ----------------------------------------------------
        # Wait if main_content is initially empty.
        # ----------------------------------------------------

        try:

            WebDriverWait(
                driver,
                PAGE_TIMEOUT
            ).until(
                lambda d: clean_text(
                    d.find_element(
                        By.CSS_SELECTOR,
                        "div.main_content"
                    ).text
                ) != ""
            )

        except TimeoutException:

            print(
                "main_content remained empty."
            )

            return []

        main_content = driver.find_element(
            By.CSS_SELECTOR,
            "div.main_content"
        )

        main_text = clean_text(
            main_content.text
        )

        if not main_text:

            print(
                "main_content is empty."
            )

            return []

        print(
            "main_content contains data."
        )

    except Exception as e:

        print(
            "Could not read main_content:"
        )

        print(
            repr(e)
        )

        return []

    # ========================================================
    # GET COMPANY LINKS
    # ========================================================

    try:

        WebDriverWait(
            driver,
            PAGE_TIMEOUT
        ).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "div.main_content ol li a.ComItem"
                )
            )
        )

    except TimeoutException:

        print(
            "No ComItem links found."
        )

        return []

    company_elements = driver.find_elements(
        By.CSS_SELECTOR,
        "div.main_content ol li a.ComItem"
    )

    companies = []

    for element in company_elements:

        try:

            name = clean_text(
                element.text
            )

            href = element.get_attribute(
                "href"
            )

            if not href:
                continue

            if href.startswith("/"):
                href = BASE_URL + href

            companies.append(
                {
                    "name": name,
                    "url": href
                }
            )

        except StaleElementReferenceException:

            continue

    print(
        f"Found {len(companies)} companies "
        f"in this province."
    )

    # ========================================================
    # ONLY FIRST 100 COMPANIES
    # ========================================================

    companies = companies[
        :MAX_COMPANIES_PER_PROVINCE
    ]

    print(
        f"Will process {len(companies)} "
        f"companies for this province."
    )

    return companies


# ============================================================
# READ div.Title
# ============================================================

def read_title_section(data):

    """
    Read:

        div.Title .display-field

    Example:

        استان: تهران
        نشانی پستی: ...
        کد پستی:
        تلفن: 88832200
    """

    title_elements = driver.find_elements(
        By.CSS_SELECTOR,
        "div.Title"
    )

    if not title_elements:

        print(
            "div.Title does not exist."
        )

        return False

    found_data = False

    for title in title_elements:

        try:

            title_text = clean_text(
                title.text
            )

            # ------------------------------------------------
            # Title exists but is empty.
            # ------------------------------------------------

            if not title_text:

                continue

            display_fields = title.find_elements(
                By.CSS_SELECTOR,
                ".display-field"
            )

            for field in display_fields:

                try:

                    text = clean_text(
                        field.text
                    )

                    # Ignore empty / whitespace-only fields.
                    if not text:
                        continue

                    if ":" in text:

                        key, value = text.split(
                            ":",
                            1
                        )

                        key = clean_text(
                            key
                        )

                        value = clean_text(
                            value
                        )

                        if key:

                            data[key] = value

                            found_data = True

                    else:

                        data.setdefault(
                            "other",
                            ""
                        )

                        if data["other"]:

                            data["other"] += " | "

                        data["other"] += text

                        found_data = True

                except StaleElementReferenceException:

                    continue

        except StaleElementReferenceException:

            continue

    return found_data


# ============================================================
# READ aside.CompanyRigth
# ============================================================

def read_company_right(data):

    """
    Fallback when div.Title has no useful data.

    Reads:

        .CompanyInfo
        .CompanyInfoDetail
    """

    print(
        "Trying aside.CompanyRigth..."
    )

    aside_elements = driver.find_elements(
        By.CSS_SELECTOR,
        "aside.CompanyRigth"
    )

    if not aside_elements:

        print(
            "aside.CompanyRigth not found."
        )

        return False

    aside = aside_elements[0]

    try:

        info_names = aside.find_elements(
            By.CSS_SELECTOR,
            ".CompanyInfo"
        )

        info_values = aside.find_elements(
            By.CSS_SELECTOR,
            ".CompanyInfoDetail"
        )

        print(
            f"Found {len(info_names)} "
            f"CompanyInfo fields."
        )

        found_data = False

        count = min(
            len(info_names),
            len(info_values)
        )

        for i in range(count):

            try:

                key = clean_text(
                    info_names[i].text
                )

                value = clean_text(
                    info_values[i].text
                )

                if not key:
                    continue

                key = key.rstrip(":")

                data[key] = value

                found_data = True

            except StaleElementReferenceException:

                continue

        return found_data

    except Exception as e:

        print(
            "Error reading CompanyRigth:"
        )

        print(
            repr(e)
        )

        return False


# ============================================================
# GET COMPANY DATA
# ============================================================

def get_company_data(
    company,
    province_name
):

    print()
    print(
        f"Company: {company['name']}"
    )

    # ========================================================
    # OPEN COMPANY URL
    # ========================================================

    if not open_url(
        company["url"],
        expected_selector="body"
    ):

        print(
            "Could not load company page."
        )

        return None

    time.sleep(1)

    # ========================================================
    # BASE DATA
    # ========================================================

    data = {
        "province": province_name,
        "company_name": company["name"],
        "company_url": company["url"],
    }

    # ========================================================
    # FIRST: div.Title
    # ========================================================

    print(
        "Checking div.Title..."
    )

    title_found = read_title_section(
        data
    )

    if title_found:

        print(
            "Company address information "
            "found in div.Title."
        )

    else:

        print(
            "div.Title is empty or has no "
            "useful display-field data."
        )

        # ====================================================
        # FALLBACK: aside.CompanyRigth
        # ====================================================

        right_found = read_company_right(
            data
        )

        if right_found:

            print(
                "Company information found "
                "in aside.CompanyRigth."
            )

        else:

            print(
                "No company information found."
            )

    # ========================================================
    # CHECK RESULT
    # ========================================================

    if len(data) <= 3:

        print(
            "No useful company data collected."
        )

        return None

    # ========================================================
    # PRINT RESULT
    # ========================================================

    print()
    print(
        "Data collected:"
    )

    for key, value in data.items():

        print(
            f"  {key}: {value}"
        )

    return data


# ============================================================
# OUTPUT FILE
# ============================================================

def get_output_file(province_index):
    """
    Build the CSV path from file_template.

    When separate_Provinces is True, the province number is used.
    When separate_Provinces is False, all data is written to
    province_1.csv.
    """

    file_number = province_index if separate_Provinces else 1

    filename = file_template.replace("$", str(file_number)) + ".csv"

    return os.path.join(
        OUTPUT_DIRECTORY,
        filename
    )


# ============================================================
# RESUME FROM EXISTING CSV
# ============================================================

def get_existing_csv_count(output_file):
    """
    Return the number of existing company data rows in a CSV.

    The CSV header is not counted.

    If the file does not exist, return 0.
    If the file exists but is empty or cannot be read, return 0.
    """

    if not os.path.exists(output_file):
        return 0

    try:
        with open(
            output_file,
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            reader = csv.reader(file)

            # Skip header.
            try:
                next(reader)
            except StopIteration:
                return 0

            count = sum(
                1
                for row in reader
                if row and any(
                    clean_text(value)
                    for value in row
                )
            )

            return count

    except (OSError, csv.Error) as e:

        print()
        print(
            f"Could not read existing CSV: {output_file}"
        )
        print(
            f"{type(e).__name__}: {e}"
        )

        return 0


def load_existing_csv_rows(output_file):
    """
    Load existing CSV rows so they are preserved when the file
    is rewritten after adding new companies.
    """

    if not os.path.exists(output_file):
        return []

    try:
        with open(
            output_file,
            "r",
            newline="",
            encoding="utf-8-sig"
        ) as file:

            reader = csv.DictReader(file)

            if not reader.fieldnames:
                return []

            return [
                dict(row)
                for row in reader
                if row and any(
                    clean_text(value)
                    for value in row.values()
                )
            ]

    except (OSError, csv.Error) as e:

        print()
        print(
            f"Could not load existing CSV: {output_file}"
        )
        print(
            f"{type(e).__name__}: {e}"
        )

        return []


# ============================================================
# SAVE CSV
# ============================================================

def save_csv(rows, output_file):

    if not rows:

        print(
            "No data to save."
        )

        return

    # ========================================================
    # BUILD COLUMNS
    # ========================================================

    fieldnames = []

    for row in rows:

        for key in row.keys():

            if key not in fieldnames:

                fieldnames.append(key)

    # ========================================================
    # WRITE CSV
    # ========================================================

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore"
        )

        writer.writeheader()

        for row in rows:

            writer.writerow(row)

    print()
    print(
        f"CSV saved: {output_file}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    all_rows = []

    try:

        # ====================================================
        # 1. LOGIN
        # ====================================================

        if not login():

            raise RuntimeError(
                "Initial login failed."
            )

        # ====================================================
        # 2. GET PROVINCES
        # ====================================================

        provinces = get_province_urls()

        if not provinces:

            raise RuntimeError(
                "No provinces found."
            )

        # ====================================================
        # 3. LOOP PROVINCES
        # ====================================================

        for province_index, province in enumerate(
            provinces,
            start=1
        ):

            # ------------------------------------------------
            # Skip provinces before start_Provincy.
            # start_Provincy is 1-based.
            # ------------------------------------------------

            if province_index < start_Provincy:

                print(
                    f"Skipping province {province_index}: "
                    f"{province['name']}"
                )

                continue

            print()
            print()
            print(
                "========================================"
            )

            print(
                f"PROVINCE "
                f"{province_index}/"
                f"{len(provinces)}"
            )

            print(
                province["name"]
            )

            print(
                "========================================"
            )

            # =================================================
            # RESUME FROM EXISTING CSV
            # =================================================

            output_file = get_output_file(
                province_index
            )

            # When provinces are separated, the CSV count belongs
            # only to this province.
            #
            # When separate_Provinces is False, province_1.csv is
            # the single cumulative file, so resume is based on the
            # rows already collected for the current province.
            if separate_Provinces:

                existing_count = get_existing_csv_count(
                    output_file
                )

            else:

                existing_rows_for_all = load_existing_csv_rows(
                    output_file
                )

                existing_count = sum(
                    1
                    for row in existing_rows_for_all
                    if clean_text(
                        row.get("province", "")
                    ) == clean_text(
                        province["name"]
                    )
                )

            print()
            print(
                f"Existing CSV: {output_file}"
            )

            print(
                f"Existing companies in CSV: "
                f"{existing_count}"
            )

            # -------------------------------------------------
            # If this province already has the maximum number
            # of companies, do not process it again.
            # -------------------------------------------------

            if existing_count >= MAX_COMPANIES_PER_PROVINCE:

                print(
                    f"Province already has "
                    f"{MAX_COMPANIES_PER_PROVINCE} "
                    f"companies."
                )

                print(
                    "Skipping this province."
                )

                # Load the existing rows so the final total
                # remains accurate.
                existing_rows = load_existing_csv_rows(
                    output_file
                )

                all_rows.extend(existing_rows)

                continue

            # ------------------------------------------------
            # Get company URLs.
            #
            # This function already limits them to the first
            # MAX_COMPANIES_PER_PROVINCE companies.
            # ------------------------------------------------

            companies = get_company_urls(
                province
            )

            if not companies:

                print(
                    "No companies found."
                )

                print(
                    "Moving to next province."
                )

                continue

            # ------------------------------------------------
            # Make sure we do not try to skip more companies
            # than actually exist on the website.
            # ------------------------------------------------

            resume_count = min(
                existing_count,
                len(companies)
            )

            if resume_count > 0:

                print()
                print(
                    f"RESUME MODE: skipping first "
                    f"{resume_count} companies."
                )

                print(
                    f"Starting from company "
                    f"{resume_count + 1}."
                )

            else:

                print()
                print(
                    "No existing companies found."
                )

                print(
                    "Starting from company 1."
                )

            # ------------------------------------------------
            # Load existing rows.
            #
            # They must be kept when the CSV is rewritten.
            # ------------------------------------------------

            existing_file_rows = load_existing_csv_rows(
                output_file
            )

            if separate_Provinces:

                province_rows = existing_file_rows

            else:

                # In combined mode, keep the complete existing CSV
                # when saving, but only count this province's rows
                # for resume purposes.
                province_rows = existing_file_rows

            # Existing rows are already represented in the output
            # file. Keep them in all_rows for reporting only.
            all_rows.extend(existing_file_rows)

            # =================================================
            # 4. LOOP COMPANIES
            # =================================================

            for company_index, company in enumerate(
                companies,
                start=1
            ):

                # ------------------------------------------------
                # RESUME:
                # Skip companies already represented in CSV.
                # ------------------------------------------------

                if company_index <= existing_count:

                    print()
                    print(
                        f"Skipping company "
                        f"{company_index}/"
                        f"{len(companies)} "
                        f"(already in CSV)"
                    )

                    continue

                print()
                print(
                    "========================================"
                )

                print(
                    f"COMPANY "
                    f"{company_index}/"
                    f"{len(companies)}"
                )

                print(
                    "========================================"
                )

                try:

                    data = get_company_data(
                        company,
                        province["name"]
                    )

                    if data:

                        all_rows.append(
                            data
                        )

                        province_rows.append(
                            data
                        )

                        # ------------------------------------------------
                        # Save after every successful company.
                        #
                        # IMPORTANT:
                        # save_csv() rewrites the file, but because
                        # province_rows contains the old CSV rows plus
                        # the new row, existing data is preserved.
                        # ------------------------------------------------

                        save_csv(
                            province_rows,
                            output_file
                        )

                except Exception as e:

                    print()
                    print(
                        "ERROR PROCESSING COMPANY"
                    )

                    print(
                        company["url"]
                    )

                    print(
                        f"{type(e).__name__}: {e}"
                    )

                    print(
                        "Moving to next company..."
                    )

                    continue

        # ====================================================
        # FINISHED
        # ====================================================

        print()
        print(
            "========================================"
        )

        print(
            "SCRAPING FINISHED"
        )

        print(
            "========================================"
        )

        print(
            f"Total companies collected/loaded: "
            f"{len(all_rows)}"
        )

    except Exception as e:

        print()
        print(
            "========================================"
        )

        print(
            "FATAL ERROR"
        )

        print(
            "========================================"
        )

        print(
            f"{type(e).__name__}: {e}"
        )

        # Each province is saved after every successful company,
        # so completed work is already present in the CSV files.

        raise

    finally:

        print()
        print(
            "Closing Firefox..."
        )

        driver.quit()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()