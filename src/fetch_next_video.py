import urllib.request
import re
from unidecode import unidecode
import random


def fetch_next_video(artist_name : str):
    artist_name_for_url = re.sub(" ", "+", artist_name)
    html = urllib.request.urlopen('https://www.youtube.com/results?search_query=one+song+from' + str(artist_name_for_url))

    video_ids = re.findall(r'watch\?v=(\S{11})', unidecode(html.read().decode()))
    video_ids = remove_duplicates(video_ids)

    return 'https://www.youtube.com/watch?v=' + random.choice(video_ids)


def remove_duplicates(urls : list):
    unique_urls = []
    [unique_urls.append(url) for url in urls if url not in unique_urls]
    return unique_urls
