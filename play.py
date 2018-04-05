# <div style="background-color:#000000;width:520px;"><div style="padding:4px;"><iframe src="//media.mtvnservices.com/embed/mgid:arc:video:comedycentral.com:a66f7c66-ed00-11e0-aca6-0026b9414f30" width="512" height="288" frameborder="0" allowfullscreen="true"></iframe></div></div>
#
# iframe src="(.*?)"
# This should get the proper group

import time
import re
from selenium import webdriver

chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument('--headless')
#chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument("--mute-audio")
browser = webdriver.Chrome(chrome_options=chrome_options)

starting_link = 'http://www.cc.com/video-clips/wrsbno/the-daily-show-with-jon-stewart-presidents--day'

try:
    next_link = starting_link
    for _ in range(10):
        browser.get(next_link)
        time.sleep(1)
        # Get the video link.
        embed_button = browser.find_element_by_css_selector('.player_share-button.embed.button')
        embed_button.click()
        embed_text = browser.find_element_by_class_name('page-overlay_copy').text
        match = re.search(r'iframe src="//(.*?)"', embed_text)
        video_link = match.group(1)
        print('https://{}'.format(video_link))
        current_thumb_nail = browser.find_element_by_css_selector('.item.active.is-selected')
        next_thumb_nail = current_thumb_nail.find_element_by_xpath('following-sibling::div')
        anchor = next_thumb_nail.find_element_by_tag_name('a')
        next_link = anchor.get_attribute('href')
    print(next_link)
    browser.close()
except Exception as error:
    browser.close()
    raise error
