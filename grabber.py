import json
import base64
import bs4
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

root_download_folder_name = 'downloads'

"""
this code was edited from:
https://github.com/ivangrov/Downloading_Google_Images/blob/main/webscraping_google_images/webscraping_google_images.py
"""

"""
search_query: string | for the google search query. should be formatted correctly
root_folder: string | the relative path where the files will be saved
limit: int | the number of images to save
file_regex: string | the regex of how the image files will be saved
scrap_high_res: bool | if true, it will grab the higher res images, which also takes more time
"""


# the actual function to use to scrap google images for images
def web_scrap_images(search_query, label_folder, file_format='', limit=10, scrap_high_res=False):
    print("Scrapping web for images with the search: " + search_query)
    save_path = root_download_folder_name + '/' + label_folder
    # make this folder if it doesn't exist
    if not os.path.isdir(save_path):
        os.makedirs(save_path)
    # check if there are already files in this folder, start the counting index from there
    prev_files_count = 0
    for path in os.listdir(save_path):
        if os.path.isfile(os.path.join(save_path, path)):
            prev_files_count += 1
    limit_counter = 0
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    search_url = "https://www.google.com/search?q=" + search_query + "&source=lnms&tbm=isch"
    driver.get(search_url)
    containers = load_all_images_in_page(driver, limit)
    total_images_found = int(len(containers) - (len(containers)/25))
    print("Starting download of " + str(min(total_images_found, limit)) + " images")
    # Scrolling all the way back up
    driver.execute_script("window.scrollTo(0, 0);")
    len_containers = len(containers)
    for i in range(1, len_containers + 1):
        if limit_counter >= limit:
            return
        if i % 25 == 0:  # every 25 containers there is a container of "related search" which we want to skip on
            continue
        x_path = """//*[@id="islrg"]/div[1]/div[%s]""" % i
        preview_image_x_path = """//*[@id="islrg"]/div[1]/div[%s]/a[1]/div[1]/img""" % i
        preview_image_element = driver.find_element("xpath", preview_image_x_path)
        preview_image_url = preview_image_element.get_attribute("src")
        driver.find_element("xpath", x_path).click()
        if scrap_high_res:
            time_started = time.time()
            while True:
                image_element = driver.find_element("xpath", """//*[@id="Sva75c"]/div[2]/div/div[2]/div[2]/div[2]/
                c-wiz/div[2]/div[1]/div[1]/div[2]/div/a/img""")
                image_url = image_element.get_attribute('src')
                if image_url != preview_image_url:
                    # print("actual URL", imageURL)
                    break
                else:
                    # making a timeout if the full res image can't be loaded
                    current_time = time.time()

                    if current_time - time_started > 10:
                        print("Timeout! Will download a lower resolution image and move onto the next one")
                        break
            # Downloading image
            try:
                download_image_url(image_url, save_path, i)
                print("Downloaded element %s out of %s total. URL: %s" % (i, len_containers + 1, image_url))
            except:
                print("Couldn't download an image %s, continuing downloading the next one" % i)
        else:
            download_image(preview_image_url, save_path, limit_counter, prev_files_count, total_images_found)
        limit_counter += 1


# scrolling down until the end of the page, loading all the images in process
def load_all_images_in_page(driver, total_images_to_download):
    show_more_results_button_xpath = """//*[@id="islmp"]/div/div/div/div/div[1]/div[2]/div[2]/input"""
    try:
        more_results_button = driver.find_element("xpath", show_more_results_button_xpath)
    except:
        more_results_button = None
        pass
    total_loaded_images = 0
    containers = None
    last_total = 0
    retries = 0
    # scroll down until the end or the total images reached its limit
    while total_loaded_images < total_images_to_download:
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        page_html = driver.page_source
        page_soup = bs4.BeautifulSoup(page_html, 'html.parser')
        containers = page_soup.findAll('div', {'class': "isv-r PNCib MSM1fd BUooTd"})
        total_loaded_images += len(containers) - len(containers)/25  # every 25 divs there is a related search div
        # the button can only be clicked when its displayed
        if more_results_button is not None and more_results_button.is_displayed():
            more_results_button.click()
        if last_total == len(containers):
            retries += 1
            if retries >= 2:
                return containers
        else:
            last_total = len(containers)
    return containers


# gets the src string and decides if it's a base64 format image or an url
def download_image(src, root_folder_name, current_idx, prev_files_idx, total):
    saved_file_name = root_folder_name.split('/')[-1] + "_" + str(current_idx + prev_files_idx).zfill(6)
    if str(src) is None:
        src_type = "None"
        return
    elif str(src).__contains__('data:image'):
        src_type = "Base64"
        download_base64(src, root_folder_name, saved_file_name)
    else:
        src_type = "Image URL"
        download_image_url(src, root_folder_name, saved_file_name)
    print("Downloaded " + str(current_idx+1) + "/" + str(total) + ", " + src_type + ": " + src[0:100] + "...")


# formats the base64 and save it
def download_base64(base64_string, root_folder_name, filename):
    fractions = base64_string.split(',')
    prefix = fractions[0]
    image_format = prefix.split('/')[1].split(';')[0]  # gather the format from the prefix of the base64
    clean_base64 = fractions[1]
    imgdata = base64.b64decode(clean_base64)
    with open(os.path.join(root_folder_name, filename + "." + image_format), 'wb') as f:
        f.write(imgdata)


def download_image_url(url, root_folder_name, filename):
    # write image to file
    response = requests.get(url)
    if response.status_code == 200:
        with open(os.path.join(root_folder_name, filename + ".jpg"), 'wb') as file:
            file.write(response.content)


# load all the labels to gather images for
with open('labels.json') as json_file:
    labels = json.load(json_file)['all_labels']

# creating a directory to save images
if not os.path.isdir(root_download_folder_name):
    os.makedirs(root_download_folder_name)

for label in labels:
    # because the grabber sometimes do not finish the run, skip labels that already have folders
    if os.path.isdir(root_download_folder_name + '/' + label['name']):
        continue
    for query in label['search_query']:
        web_scrap_images(query, label['name'], "", 1000)

