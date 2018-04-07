import os
import time
import shutil
import itertools
import subprocess
import youtube_dl
from selenium import webdriver

episode_link = 'http://www.cc.com/video-clips/wbjagy/the-daily-show-with-jon-stewart-headlines---rockey-road-to-dc'

if os.path.exists('temporary'):
    shutil.rmtree('temporary')
os.makedirs('temporary')

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument("--mute-audio")
browser = webdriver.Chrome(chrome_options=chrome_options)

youtube_dl_options = {'outtmpl': 'temporary/%(autonumber)s.%(ext)s'}
episode_date_string = None
with youtube_dl.YoutubeDL(youtube_dl_options) as downloader:
    try:
        next_link = episode_link
        for index in itertools.count():
            browser.get(next_link)
            time.sleep(1)
            embed_button = browser.find_element_by_css_selector('.player_share-button.embed.button')
            current_thumb_nail = browser.find_element_by_css_selector('.item.is-selected')
            next_thumb_nail = current_thumb_nail.find_element_by_xpath('following-sibling::div')
            anchor = next_thumb_nail.find_element_by_tag_name('a')
            anchor_header = anchor.find_element_by_class_name('meta-wrap').find_element_by_class_name('header')
            anchor_date_string = anchor_header.find_elements_by_tag_name('span')[1].text
            if episode_date_string is None:
                episode_date_string = anchor_date_string
            if anchor_date_string != episode_date_string:
                break
            next_link = anchor.get_attribute('href')
            downloader.download([next_link])
        print(next_link)
        browser.quit()
    except Exception as error:
        browser.quit()
        raise error

episode_date_string = episode_date_string.replace('/', '-')
clip_list = sorted(os.listdir('temporary'))
with open('temporary/concat.txt', 'a+') as concat_file:
    for clip_name in clip_list:
        concat_file.write('file {}\n'.format(clip_name))
ffmpeg_call_list = ['ffmpeg', '-y', '-f', 'concat', '-i', 'temporary/concat.txt',
                    'output/{}.mp4'.format(episode_date_string)]
subprocess.call(ffmpeg_call_list)
