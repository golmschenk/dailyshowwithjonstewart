
from selenium import webdriver
import youtube_dl

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument("--mute-audio")
browser = webdriver.Chrome(chrome_options=chrome_options)

starting_link = 'http://www.cc.com/video-clips/wrsbno/the-daily-show-with-jon-stewart-presidents--day'

with youtube_dl.YoutubeDL() as downloader:
    try:
        next_link = starting_link
        for _ in range(10):
            downloader.download([next_link])
            browser.get(next_link)
            embed_button = browser.find_element_by_css_selector('.player_share-button.embed.button')
            current_thumb_nail = browser.find_element_by_css_selector('.item.active.is-selected')
            next_thumb_nail = current_thumb_nail.find_element_by_xpath('following-sibling::div')
            anchor = next_thumb_nail.find_element_by_tag_name('a')
            next_link = anchor.get_attribute('href')
        print(next_link)
        browser.quit()
    except Exception as error:
        browser.quit()
        raise error
