import os
import time
import shutil
import itertools
import subprocess
import youtube_dl
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

episode_link = 'http://www.cc.com/episodes/0tro1o/the-daily-show-with-jon-stewart-january-30--2007---neil-degrasse-tyson-season-12-ep-12014'

if os.path.exists('temporary'):
    shutil.rmtree('temporary')
os.makedirs('temporary')
os.makedirs('output', exist_ok=True)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--mute-audio')
browser = webdriver.Chrome(chrome_options=chrome_options)

youtube_dl_options = {'outtmpl': 'temporary{}%(autonumber)s.%(ext)s'.format(os.path.sep)}
episode_date_string = None
with youtube_dl.YoutubeDL(youtube_dl_options) as downloader:
    try:
        next_link = episode_link
        for index in itertools.count():
            browser.get(next_link)
            time.sleep(2)
            current_thumb_nail = browser.find_element_by_css_selector('.item.is-selected')
            if index == 0:
                next_thumb_nail = current_thumb_nail
            else:
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
    except WebDriverException as error:
        browser.quit()
        raise error

episode_date_string = episode_date_string.replace('/', '-')
clip_list = sorted(os.listdir('temporary'))
with open(os.path.join('temporary', 'concat.txt'), 'a+') as concat_file:
    for clip_name in clip_list:
        if not clip_name.startswith('.'):
            concat_file.write('file {}\n'.format(clip_name))
ffmpeg_call_list = ['ffmpeg', '-y', '-f', 'concat', '-i', os.path.join('temporary', 'concat.txt'),
                    os.path.join('output', '{}.mp4'.format(episode_date_string))]
subprocess.call(ffmpeg_call_list)
print('Done.')
