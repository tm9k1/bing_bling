# BING BLING

A python3 script to download every Bing Wallpaper that made it to a Windows lockscreen since 2010. (5600+ wallpapers so far)

## Ask me why do this project?

...and I'd ask you WHY ARE BING WALLPAPERS SO DAMN SHARP?

## BEHAVIORAL SPECS

- it creates a couple folders in the script's current directory.
  - webpages: well, it saves webpages here. I didn't need to save webpages but that's how it is right now.
  - Wallpapers: this is where this script downloads new folders.
- webpages are all deleted once the script is done doing its thing
- technical details at the bottom

## DEPENDENCIES

- install using this command:-

   ```bash
   python3 -m pip install tqdm requests beautifulsoup4
   ```

## SCREENSHOTS

- ![start](https://i.imgur.com/37ODx8o.png)
- ![kinda-halfway](https://i.imgur.com/yW5EXuQ.png)
- ![done!](https://user-images.githubusercontent.com/22996531/144054620-68aa96d6-ea76-4aac-9e9f-cdd2dc831776.png)


## FAQs

1. **Oh no I accidentally stopped the script mid-way.. what do I do?**

    If you don't care about the internals, just start the script again and it will handle partially downloaded wallpapers for you.
    >
    - For the interested, any partially downloaded files will have the prefix "**0INCOMPLETE**" (0 to spot such files quickly after a sort).

2. **Oh no I moved my wallpapers and now I'm downloading everything again!**

    The location specified in `wallpaper_save_path` variable (at the top of the script) will be checked for any wallpapers not yet downloaded by the script. If any wallpaper is missing, the script downloads it for you.

    - NOTE: This folder NEED NOT BE EMPTY; i.e. you can point the variable to your wallpapers collection folder, and the script will fill the folder with Bing wallpapers and WON'T remove your other wallpapers.
    - NOTE: The default location of this folder is './Wallpapers/' (the trailing backslash is important!!!!)

## contributions are welcome 🙇‍♂️

## TECHNICAL DETAILS

0. The main idea is to beautifulsoup4 to parse a webpage, figure out the download link and do this for every wallpaper on a given website.

1. We find a website that hosts all bing wallpapers that we would ever need. bwallpaperhd.com  and bingwallpaper.anerg.com are good candidates. Considering the simplicity to parse the webpage, We go for bwallpaperhd.com.

2. We download the webpage using urllib3, a library that is great at one thing - downloading webpages.

3. Next, parse the sitemap for the page and get links for all wallpapers listed there. Use some beautifulsoup4 and google-fu here. Once we're done here, we have successfully parsed links to every wallpaper's own webpage

4. After this, download the webpage of every wallpaper and extract the link to the "Original" wallpaper file, conveniently put in the tag structure: -

    ```html
    ...
    <div class="download">
    <a href="download.link.here/wallpaper.jpg"> Original</a>
    ...
    </div>
    ...

5. Because we have so many extra cores lying around, we use a `ThreadPoolExecutor` to spread work across 20 workers.
    > Q: **Why just 20? Let's do an even 100!**
    >
    > too many workers means less cycles to use and more context switching, so keep it below 20 for low core systems. The library can only handle spreading workload across up to 32 cores, so keep that in mind for the upper limit.

6. Download the wallpaper with the name "0INCOMPLETE_wallpapername.jpg" so we can quickly spot and delete incomplete files. While doing this, also delete any such incomplete download when starting a new one for a given wallpaper.

7. Once downloaded, rename the wallpaper to "wallpapername.jpg". Also remove its corresponding webpage.

8. Once all wallpapers are done downloading, delete the sitemap webpage.

9. Done! Enjoy your new collection! =)
