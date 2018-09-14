from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyvirtualdisplay import Display
import pandas as pd
from time import sleep, time
import os
import glob


# start the virtual display
display = Display(visible=0, size=(1024, 768))
display.start()

# get zipcodes
df = pd.read_table(
    ('https://www2.census.gov/geo/docs/maps-data/data/'
     'rel/zcta_county_rel_10.txt'),
    delimiter=',')
bay_area_zips = df[(df['STATE'] == 6) & (df['COUNTY'].isin(
    [1, 13, 41, 55, 75, 81, 85, 95, 97]))]['ZCTA5'].values
num_zips = len(bay_area_zips)

# log into REIS
login_url = 'https://se.reis.com/account/doLogin'

driver = webdriver.Chrome()
options = webdriver.ChromeOptions()
options.add_argument("download.default_directory=~/Downloads")
driver.get(login_url)

email = driver.find_element_by_id("inputEmail")
password = driver.find_element_by_id("inputPassword")
email.send_keys("gardner.max@gmail.com")
password.send_keys("Qd3mTd6Zi")

sign_in_button = driver.find_element(By.XPATH, '''//button[@type="submit"]''')
sign_in_button.click()
sleep(5)
assert driver.current_url == 'https://se.reis.com/'
landing_page_url = driver.current_url

# loop through zipcodes
sttm = time()
scraped_zips = list(set([string.split('_')[3] for string in glob.glob(
    '/home/max/Downloads/reis_properties_v2*.xlsx')]))
zips_to_scrape = list(set([
    zipcode for zipcode in bay_area_zips if str(zipcode) not in scraped_zips]))
print('Already scraped {0} zipcodes. Getting the remaining {1} now.'.format(
    str(len(scraped_zips)), str(len(zips_to_scrape))))

for i, zipcode in enumerate(zips_to_scrape):

    if driver.current_url != landing_page_url:
        driver.get(landing_page_url)

    # search
    search_bar = driver.find_element_by_id("searchString")
    search_bar.send_keys(str(zipcode))
    search_button = driver.find_element_by_class_name("search-button")
    sleep(5)
    search_button.click()
    sleep(10)

    # extract results
    list_view_button = driver.find_element_by_class_name("btn-list")
    sleep(5)
    try:
        list_view_button.click()
    except WebDriverException:
        sleep(10)
        try:
            list_view_button.click()
        except WebDriverException:
            sleep(20)
            list_view_button.click()

    num_results = driver.find_element_by_class_name("results-span").text

    min_elapsed = round((time() - sttm) / 60, 1)
    min_per_zip = min_elapsed / (i + 1)
    min_remaining = round(min_per_zip * (len(zips_to_scrape) - (i + 1)), 1)
    print(
        'Found {0} properties in zipcode {1} ({2} of {3}) '
        '// {4} min. elapsed // {5} min remaining'.format(
            num_results, str(zipcode), i, str(len(zips_to_scrape)),
            min_elapsed, min_remaining))

    if int(num_results.replace(',', '')) <= 500:
        if int(num_results) <= 2:
            open('/home/max/Downloads/reis_properties_{0}_all.xlsx'.format(
                str(zipcode)), 'a').close()
            continue
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "btn-export")))
        export_menu_button = driver.find_element_by_class_name("btn-export")
        sleep(10)
        try:
            export_menu_button.click()
        except WebDriverException:
            sleep(25)
            export_menu_button.click()

        sleep(30)
        download_all_button = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((
                By.XPATH, '''//input[@type="radio" and @value="2"]''')))
        assert download_all_button.find_element(By.XPATH, '..').text == 'All'
        download_all_button.click()
        sleep(2)
        assert download_all_button.get_property("checked")
        excel_export_button = driver.find_element(
            By.XPATH, '''//input[@type="radio" and @value="x"]''')
        excel_export_button.click()
        sleep(2)
        assert excel_export_button.get_property("checked")
        download_button = driver.find_element(
            By.XPATH,
            '''//button[@class="dropdown-item text-center btn-download"]''')
        download_button.click()
        sleep(40)
        try:
            os.rename(
                '/home/max/Downloads/ReisPropertyReport.xlsx',
                '/home/max/Downloads/reis_properties_v2_{0}_all.xlsx'.format(
                    str(zipcode)))
        except OSError:
            print('Nothing downloaded for zipcode {0}'.format(
                zipcode))
            open('/home/max/Downloads/reis_properties_v2_{0}_all.xlsx'.format(
                str(zipcode)), 'a').close()
        sleep(20)

    else:
        num_pages = max([
            int(x.text) for x in driver.find_elements(
                By.XPATH, "//li[@class='page-item']/a") if len(x.text) > 0])

        for page_num in range(num_pages):
            WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "btn-export")))
            export_menu_button = driver.find_element_by_class_name(
                "btn-export")
            sleep(5)
            print('Downloading results from page {0} of {1}'.format(
                str(page_num + 1), str(num_pages)))
            try:
                export_menu_button.click()
            except WebDriverException:
                sleep(20)
                export_menu_button.click()
            sleep(5)

            # download only results on the current page
            download_current_page_button = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((
                    By.XPATH, '''//input[@type="radio" and @value="1"]''')))
            assert download_current_page_button.find_element(
                By.XPATH, '..').text == 'Current Page'
            download_current_page_button.click()
            sleep(2)
            assert download_current_page_button.get_property("checked")
            excel_export_button = driver.find_element(
                By.XPATH, '''//input[@type="radio" and @value="x"]''')
            excel_export_button.click()
            sleep(2)
            assert excel_export_button.get_property("checked")
            download_button = driver.find_element(
                By.XPATH,
                "//button[@class='dropdown-item text-center btn-download']")
            download_button.click()
            sleep(7)
            os.rename(
                '/home/max/Downloads/ReisPropertyReport.xlsx',
                '/home/max/Downloads/reis_properties_v2_{0}_{1}.xlsx'.format(
                    str(zipcode), str(page_num + 1).zfill(2)))

            if page_num == num_pages - 1:
                break

            # click over to the next page
            all_page_buttons = driver.find_elements(
                By.XPATH, "//li[@class='page-item']/a")
            if len(all_page_buttons) == 0:
                print('Actually found only 1 page of results...moving on.')
                break
            else:
                all_page_buttons[-1].click()
                sleep(3)
        sleep(5)
