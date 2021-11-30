#!/usr/bin/python3
import os
from bs4 import BeautifulSoup
import requests
import  concurrent.futures
from tqdm import tqdm

# change these two to whatever you like.
# NOTE: Remember that the next run would again download all wallpapers if you move the wallpapers away from wallpaper_save_path
wallpaper_save_path = './Wallpapers/'
webpages_save_path = './webpages/'

# This is the link I use to get the wallpapers. This site is updated daily, with latest wallpapers at the top.
sitemap_url = 'https://www.bwallpaperhd.com/sitemap.html'

sitemap_filename = webpages_save_path + sitemap_url.split('/')[-1]

# download a file at download_url to file_name
def download_a_file(download_url: str, file_name: str):
    incomplete_file_name = file_name[:file_name.rfind('/')+1] + '0INCOMPLETE_'+ file_name[file_name.rfind('/')+1:]

    # remove any stale download of the file
    if os.path.exists(incomplete_file_name):
        os.remove(incomplete_file_name)

    # download the file
    response = requests.get(download_url, stream=True)
    if response.status_code == 200:

        # write it as 0INCOMPLETE_filename so we can ensure removal of stale files later
        # NOTE: This is not a silver bullet, but it's better than keeping our fingers crossed
        with open(incomplete_file_name, 'wb') as f:
            for chunk in response:
                f.write(chunk)

    # rename the file to filename if we received the whole file
    os.rename(incomplete_file_name, file_name)

# returns a list of tuples as [(Wallpaper Name, http://wallpaper.webpage/url.html),...]
def extract_links_from_sitemap(sitemap_url: str, sitemap_filename: str):

    # remove any stale download of the sitemap
    if os.path.exists(sitemap_filename):
        os.remove(sitemap_filename)

    # download the sitemap
    download_a_file(sitemap_url, sitemap_filename)
    soup = BeautifulSoup(open(sitemap_filename, encoding='utf-8'), "html.parser")
    # print(soup.prettify())
    divs = soup.find_all('div', attrs={'id':'content'})
    list_of_wallpprs = []
    for div in divs:
        h3 = div.find_all('h3', string='Latest WallPapers')
        if h3:
            anchor_tags = div.find_all('a')
            for anchor_tag in anchor_tags:
                wallpaper_name = anchor_tag.contents[0]
                wallpaper_webpage_url = anchor_tag.get('href')
                list_of_wallpprs.append((wallpaper_name, wallpaper_webpage_url))
    return list_of_wallpprs

# expects the tuples from list_of_wallpapers as [(Wallpaper Name, http://wallpaper.webpage/url.html),...]
def download_a_wallpaper(tup: tuple):

    wallpaper_name, wallpaper_webpage_url = tup
    wallpaper_webpage_filename = wallpaper_webpage_url.split('/')[-1]
    wallpaper_filename = wallpaper_webpage_filename[:wallpaper_webpage_filename.find('.')]
    wallpaper_filename = wallpaper_filename + '.jpg' # hopefully they won't ditch jpg anytime soon!

    if not os.path.exists(wallpaper_save_path + wallpaper_filename):
        if not os.path.exists(webpages_save_path + wallpaper_webpage_filename):
            download_a_file(wallpaper_webpage_url, webpages_save_path + wallpaper_webpage_filename)
        soup = BeautifulSoup(open(webpages_save_path + wallpaper_webpage_filename, encoding='utf-8'), "html.parser")
        divs = soup.find_all('div', attrs={'class':'download'})
        for div in divs:
            anchors = div.find_all('a')
            for anchor in anchors:
                if anchor.contents[0].strip().lower() == 'original':
                    wallpaper_url = anchor.get('href')
                    print(wallpaper_name + ': ' + wallpaper_url)
                    download_a_file(wallpaper_url, wallpaper_save_path + wallpaper_filename)
        os.remove(webpages_save_path + wallpaper_webpage_filename)

    return wallpaper_name

## MAIN ACTION IS HERE

# make the necessary directories in case they don't exist
os.makedirs(wallpaper_save_path, exist_ok=True)
os.makedirs(webpages_save_path, exist_ok=True)

# extract the list of wallpapers with links to each wallpaper's own webpage
list_of_wallpapers = extract_links_from_sitemap(sitemap_url, sitemap_filename)
# get the total count of wallpapers we can expect by the end of processing
total_wallpapers = len(list_of_wallpapers)
# Create a progress bar so user knows what's going on
progress_bar = tqdm(range(total_wallpapers), desc="Downloading Wallpapers",colour="blue", bar_format='{l_bar}{bar}| [{n_fmt}/{total_fmt}] [Elapsed: {elapsed}]')

# Start distributing work across multiple threads. 20 seems to be a safe count for now.
with concurrent.futures.ThreadPoolExecutor(max_workers=20, thread_name_prefix='Wallpaper_Downloader_') as executor:
    future_to_url = [ executor.submit(download_a_wallpaper, wallpaper_entry) for wallpaper_entry in list_of_wallpapers ]

    for future in concurrent.futures.as_completed(future_to_url):
        progress_bar.n += 1
        progress_bar.refresh()

progress_bar.close()
# clean up the downloaded sitemap webpage
os.remove(sitemap_filename)

print('Done! Enjoy your new collection! =)')
