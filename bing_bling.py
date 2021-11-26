#!/usr/bin/python3
import os
from bs4 import BeautifulSoup
import requests
import  concurrent.futures
from tqdm import tqdm
import urllib3

# change these two to whatever you like.
# NOTE: Remember that the next run would again download all wallpapers if you move the wallpapers away from wallpaper_save_path
wallpaper_save_path = './Wallpapers/'
webpages_save_path = './webpages/'

# This is the link I use to get the wallpapers. This site is updated daily, with latest wallpapers at the top.
url = 'https://www.bwallpaperhd.com/sitemap.html'

os.makedirs(wallpaper_save_path, exist_ok=True)
os.makedirs(webpages_save_path, exist_ok=True)

def getWebPage(url: str, page_filename: str):
    # Making the request (The request function returns HTTPResponse object)

    http = urllib3.PoolManager()

    resp = http.request('GET', url)

    if resp.status != 200:
        print('We got a problem. The website is not working.. Error Code: ' + str(resp.status))
        exit()

    # Download the page
    if os.path.exists(webpages_save_path + page_filename):
        os.remove(webpages_save_path + page_filename)
    with open(webpages_save_path + page_filename, 'w', encoding="utf-8") as f:
        f.write(resp.data.decode('utf-8'))


def extract_links_from_sitemap(page_filename: str):
    soup = BeautifulSoup(open(webpages_save_path + page_filename, encoding='utf-8'), features="lxml")
    # print(soup.prettify())
    divs = soup.find_all('div', attrs={'id':'content'})
    list_of_wallpprs = []
    for div in divs:
        h3 = div.find_all('h3', string='Latest WallPapers')
        if h3:
            anchor_tags = div.find_all('a')
            for anchor_tag in anchor_tags:
                # print(anchor_tag)
                wallpaper_name = anchor_tag.contents[0]
                wallpaper_webpage_url = anchor_tag.get('href')
                list_of_wallpprs.append((wallpaper_name, wallpaper_webpage_url))
    return list_of_wallpprs



# this function is instantiated across 40 threads
def download_a_wallpaper(tup: tuple):

    wallpaper_name, wallpaper_webpage_url = tup
    wallpaper_webpage_filename = wallpaper_webpage_url.split('/')[-1]
    wallpaper_filename = wallpaper_webpage_filename[:wallpaper_webpage_filename.find('.')]
    wallpaper_filename = wallpaper_filename + '.jpg'

    if not os.path.exists(wallpaper_save_path + wallpaper_filename):
        getWebPage(wallpaper_webpage_url, wallpaper_webpage_filename)
        soup = BeautifulSoup(open(webpages_save_path + wallpaper_webpage_filename, encoding='utf-8'), features="lxml")
        # print(soup.prettify())
        divs = soup.find_all('div', attrs={'class':'download'})
        for div in divs:
            anchors = div.find_all('a')
            for anchor in anchors:
                if anchor.contents[0].strip().lower() == 'original':
                    wallpaper_url = anchor.get('href')
                    # print(wallpaper_name + ': ' + wallpaper_url)
                    if os.path.exists(wallpaper_save_path + '0INCOMPLETE_' + wallpaper_filename):
                        os.remove(wallpaper_save_path + '0INCOMPLETE_' + wallpaper_filename)

                    response = requests.get(wallpaper_url, stream=True)
                    if response.status_code == 200:
                        with open(wallpaper_save_path + '0INCOMPLETE_' + wallpaper_filename, 'wb') as f:
                            for chunk in response:
                                f.write(chunk)
                    os.rename(wallpaper_save_path + '0INCOMPLETE_' + wallpaper_filename, wallpaper_save_path + wallpaper_filename)
        os.remove(webpages_save_path + wallpaper_webpage_filename)
    return wallpaper_name


## MAIN ACTION IS HERE

page_filename = url.split('/')[-1]

getWebPage(url, page_filename)
list_of_wallpapers = extract_links_from_sitemap(page_filename)
total_wallpapers = len(list_of_wallpapers)

progress_bar = tqdm(range(total_wallpapers), desc="Downloading Wallpapers",colour="blue", bar_format='{l_bar}{bar}| [{n_fmt}/{total_fmt}] [Elapsed: {elapsed}]')

with concurrent.futures.ThreadPoolExecutor(max_workers=20, thread_name_prefix='Wallpaper_Downloader_') as executor:    
    future_to_url = [ executor.submit(download_a_wallpaper, wallpaper_entry) for wallpaper_entry in list_of_wallpapers ]
    
    for future in concurrent.futures.as_completed(future_to_url):
        progress_bar.n += 1
        progress_bar.refresh()
progress_bar.close()
os.remove(webpages_save_path + page_filename)

print('Done! Enjoy your new collection! =)')

