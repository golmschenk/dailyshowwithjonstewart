"""
Code for getting a list of all the episode links.
"""
from datetime import datetime, date
import os
import re
import time
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException


episode_list_file_name_suffix = '_episode_list.txt'


def obtain_episode_list(show='daily_show', output_path=None):
    if output_path is None:
        output_path = '{}{}'.format(show, episode_list_file_name_suffix)
    if show == 'daily_show':
        episode_guide_link = 'http://www.cc.com/shows/the-daily-show-with-jon-stewart/episode-guide'
        first_episode_name = 'January 11, 1999 - Michael J. Fox'
    elif show == 'colbert_report':
        episode_guide_link = 'http://www.cc.com/shows/the-colbert-report/episode-guide'
        first_episode_name = 'October 17, 2005 - Stone Phillips'
    else:
        raise ValueError('{} is not an available show option.'.format(show))
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--mute-audio')
    browser = webdriver.Chrome(chrome_options=chrome_options)
    try:
        first_episode_found = False
        print('Listing all episodes. This needs to wait for the site\'s javascript as it repeatedly clicks a "load '
              'more" button, so it will take a little while.')
        browser.get(episode_guide_link)
        time.sleep(5)
        while not first_episode_found:
            first_episodes = browser.find_elements_by_xpath("//*[contains(text(), '{}')]".format(first_episode_name))
            if len(first_episodes) > 0:
                first_episode_found = True
            else:
                load_more_button = browser.find_element_by_css_selector('.L001_line_list_load-more')
                browser.execute_script("arguments[0].click();", load_more_button)
        episode_list_element = browser.find_element_by_css_selector('.L001_line_list')
        episode_containers = reversed(episode_list_element.find_elements_by_tag_name('li'))
        with open(output_path, 'w') as episode_link_list_file:
            for episode_container in episode_containers:
                try:
                    episode_link = episode_container.find_element_by_tag_name('a').get_attribute('href')
                except NoSuchElementException:
                    print('One episode container had no anchor element.')
                    continue
                episode_link_list_file.write(episode_link)
                episode_link_list_file.write('\n')
    except WebDriverException as error:
        browser.quit()
        raise error
    print('Done.')
    return output_path


def generate_unwatched_list(include_daily_show=True, include_colbert_report=True):
    list_file_paths_to_include = []
    if include_daily_show:
        daily_show_episode_list_file_path = 'daily_show{}'.format(episode_list_file_name_suffix)
        if not os.path.exists(daily_show_episode_list_file_path):
            print('Getting Daily Show list...')
            obtain_episode_list('daily_show', daily_show_episode_list_file_path)
        list_file_paths_to_include.append(daily_show_episode_list_file_path)
    if include_colbert_report:
        colbert_report_episode_list_file_path = 'colbert_report{}'.format(episode_list_file_name_suffix)
        if not os.path.exists(colbert_report_episode_list_file_path):
            print('Getting Colbert Report list...')
            obtain_episode_list('colbert_report', colbert_report_episode_list_file_path)
        list_file_paths_to_include.append(colbert_report_episode_list_file_path)
    episode_list = []
    for list_file_path in list_file_paths_to_include:
        with open(list_file_path) as list_file:
            episode_list += list_file.readlines()
    episode_list = [episode for episode in episode_list if episode != '\n']  # Remove empty lines.
    episode_list = list(dict.fromkeys(episode_list))  # Remove duplicates.
    episode_list.sort(key=episode_date_from_link)  # Order by date.
    with open('unwatched_episode_list.txt', 'w') as unwatched_episode_list_file:
        unwatched_episode_list_file.writelines(episode_list)


def episode_date_from_link(episode_link):
    date_pattern = r'-([a-z]+)-(\d{1,2})--(\d{4})-(-|season)'
    match = re.search(date_pattern, episode_link)
    year = int(match.group(3))
    # Handle all the misspellings in the links.
    month_string = match.group(1).replace('feburary', 'february').replace(
        'februrary', 'february').replace('janurary', 'january').replace('januraray', 'january')
    month = datetime.strptime(month_string, '%B').month
    day = int(match.group(2))
    return date(year=year, month=month, day=day)

if __name__ == '__main__':
    generate_unwatched_list()
