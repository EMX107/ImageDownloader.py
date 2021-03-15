from selenium import webdriver  # you need to download chrome.exe and the chromedriver.exe , otherwise you have to modify the code
from bs4 import BeautifulSoup
from PIL import Image
import requests
import time
import os


ECOSIA_IMAGE = 'https://www.ecosia.org/images?q='
HTML_SAVE_FOLDER = 'webpages'
IMAGE_SAVE_FOLDER = 'images'
GET_FULLSIZED_IMAGES = False

USR_AGENT = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
}



def image_is_corrupted(image_path):
    try:
        with Image.open(image_path) as img:
            img.verify()
        return False
    except:
        return True


def download_image(img_url):
    try:
        return requests.get(img_url, headers=USR_AGENT).content
    except:
        return None


def parse_for_images(html):
    soup = BeautifulSoup(html, 'html.parser')
    if GET_FULLSIZED_IMAGES:
        return [img.get('href') for img in soup.find_all('a', {'class': 'image-result__link'})]
    else:
        return [img.get('src') for img in soup.find_all('img', {'class': 'image-result__image'})]


def get_web_page(url, n_images):
    driver = webdriver.Chrome() # if chromedriver.exe is not added to the %path% , you need to set the file path as an argument to the constructer
    driver.get(url)
    while len(parse_for_images(driver.page_source)) <= n_images * 1.1:  # search for 10% more images then wanted, because of some images could be corrupted or not available
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    html = driver.page_source
    driver.quit()
    return html



if __name__ == '__main__':
    # user specifyed values
    query = input('what images you are looking for? ')
    n_images = int(input('how many images do you want? '))

    time_stamp = str(int(time.time()))

    image_set = time_stamp + ' - ' + query
    search_url = ECOSIA_IMAGE + query.replace(' ', '+')


    # create save folders
    if not os.path.exists(HTML_SAVE_FOLDER):
        os.mkdir(HTML_SAVE_FOLDER)
    if not os.path.exists(IMAGE_SAVE_FOLDER):
        os.mkdir(IMAGE_SAVE_FOLDER)
    if not os.path.exists(IMAGE_SAVE_FOLDER + '\\' + image_set):
        os.mkdir(IMAGE_SAVE_FOLDER + '\\' + image_set)

    temp_file_path = IMAGE_SAVE_FOLDER + '\\' + image_set + '\\temp.png'
    

    # get raw html
    print('\nsearching for images...')
    html = get_web_page(search_url, n_images)


    # save the webpage
    html_file_path = HTML_SAVE_FOLDER + '\\' + time_stamp + ' - ' + query + '.html'
    with open(html_file_path, 'wb') as html_file:
        html_file.write(html.encode())


    # get all image links
    image_links = parse_for_images(html)
    print(f'\nfound {len(image_links)} images')


    # download the images
    print('\nstart download...')
    img_count = 0
    for index, image_link in enumerate(image_links):
        if img_count < n_images:
            # download the image
            image_binary = download_image(image_link)
            
            # check if the download was successfull
            if not image_binary:
                continue
            with open(temp_file_path, 'wb') as temp_file:
                temp_file.write(image_binary)
            if image_is_corrupted(temp_file_path):
                continue
            
            # save image
            with open(IMAGE_SAVE_FOLDER + '\\' + image_set + '\\' + str(img_count) + '.png', 'wb') as image_file:
                image_file.write(image_binary)
            
            # add image link to the info file
            with open(IMAGE_SAVE_FOLDER + '\\' + image_set + '\\' + 'info.txt', 'a') as info_file:
                info_file.write(str(img_count) + '\t- ' + image_link + '\n')
            
            print(str(img_count) + '\t- ' + image_link)
            img_count += 1
        else:
            break
    
    os.remove(temp_file_path)
    print('\ndone.')