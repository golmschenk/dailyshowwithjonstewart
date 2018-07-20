"""
Code for getting a list of all the episode links.
"""
import os
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
        browser.get(episode_guide_link)
        time.sleep(5)
        first_episode_found = False
        print('Listing all episodes. This needs to wait for the site\'s javascript as it repeatedly clicks a "load '
              'more" button, so it will take a little while.')
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


if __name__ == '__main__':
    pass
    #generate_unwatched_list(include_colbert_report=False)
