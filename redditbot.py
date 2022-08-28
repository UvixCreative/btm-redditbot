#!/usr/bin/env python3

import praw
import feedparser
import time
import pickle
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
import logging

subreddit = 'uvixsandbox'

logging.basicConfig(format='[%(asctime)s]:%(name)s:%(lineno)s:%(message)s', level=logging.DEBUG, handlers=[
    logging.FileHandler("redditbot.log"),
    logging.StreamHandler()
])


# NOTE: For the sake of this script, "latest" means the latest entry from a particular platform. "Last" referrs to the
# last post that the script itself has parsed and uploaded to reddit.

def htmltomd(element, ret='', indent=''):
    if type(element) != Tag:
        return ret
    
    if element.name == 'br':
        ret += ' \n'
        
    # Prefixes
    if element.name == 'h1':
        ret+='#'
    elif element.name == 'h2':
        ret+='##'
    elif element.name == 'h3':
        ret+='###'
    elif element.name == 'h4':
        ret+='####'

    # Prefix and suffix combinations
    if element.name == 'sup':
        ret+='^('
    elif element.name == 'b' or element.name == 'strong':
        ret+='**'
    elif element.name == 'i' or element.name == 'em':
        ret+='*'
    elif element.name == 'p':
        ret+=' \n'

    # Anchors (links)
    if element.name == 'a':
        ret+='['

    # Convert images to links
    if element.name == 'img':
        ret+='\n[[Image: {}]]({})\n'.format(element['alt'], element['src'])
        
    childCount = 0
    if element.name == 'ul' or element.name == 'ol':
        ret+=' \n'
        linum = 1
        for child in element.children:
            if type(child) == Tag and child.name == 'li':
                # List bulletin, - if unordered, numeric if ordered
                if element.name == 'ul':
                    ret += "- "
                elif element.name == 'ol':
                    ret += str(linum) + ". "
                    
                ret += htmltomd(child, indent=indent+'\t')
                ret += " \n"

                linum += 1

    else:
        for child in element.children:
            if type(child) == NavigableString:
                ret += str(child).strip()
            elif type(child) == Tag and child.name != 'br':
                childCount += 1
                ret = htmltomd(child, ret, indent+'\t')
                # Don't += ret because you're already passing ret, and it will return ret +=
                # whatever it has to offer.
                
    # Second half of pre/suffix combinations
    if element.name == 'sup':
        ret+=')'
    elif element.name == 'b' or element.name == 'strong':
        ret+='**'
    elif element.name == 'i' or element.name == 'em':
        ret+='*'
    elif element.name == 'p':
        ret+=' \n'
    elif element.name == 'a':
        ret+=']({})'.format(element['href'])

    return ret
        

def main():
    logger = logging.getLogger('redditbot')

    # -- Sign in
    reddit = praw.Reddit(
        user_agent="blackTeaBot",
        client_id="lQR5uub9wKLQWAOyv5oDXA",
        client_secret="LnltMKGPfEqf3GyeJZij7IjBlR264g",
        username="creativityisntreal",
        password="L1m0ismyc@"
    )

    # -- Open "last grabbed" pickle file
    with open('btmBotLastPost.pickle', 'rb') as file:
        lastPosts = pickle.load(file)

    # -- Grab news feed from BTM website
    newsFeed = feedparser.parse('https://www.blackteamotorbikes.com/en-us/blogs/news.atom')
    newsFeed['entries'].reverse() # Reverse for reverse chronological order
    for entry in newsFeed['entries']:
        if entry['published_parsed'] > lastPosts['newsFeed']:
            lastPosts['newsFeed'] = entry['published_parsed'] # Put this here because even if it's NOT text, we don't need to evaluate it next time
            if entry['content'][0]['type'] == "text/html":
                # Get original link
                link = ''
                for item in entry['links']:
                    if item['rel'] == 'alternate':
                        link = item['href']

                # Original publish date
                posted = entry['published']

                # Title
                title = "[BLOG] " + entry['title']
                
                body = ''
                htmlContent = BeautifulSoup(entry['content'][0]['value'], 'html.parser')
                

                for element in htmlContent:
                    body += htmltomd(element)

                body += "\n\n------- \nOriginally published {} at {}".format(posted, link)
                #newPost = reddit.subreddit(subreddit).submit(title=title,selftext=body)
                #print(newPost)

    # -- Grab feed from BTM YouTube
    ytFeed = feedparser.parse('https://www.youtube.com/feeds/videos.xml?channel_id=UC9GqrulJF2X4NlJFhcCXmUA')
    for entry in ytFeed['entries']:
        if entry['published_parsed'] > lastPosts['ytFeed']:
            lastPosts['ytFeed'] = entry['published_parsed']
            title = "[YT] " + entry['title']
            link = entry['link']
            #newPost = reddit.subreddit(subreddit).submit(title=title, url=link)
            #print(newPost)

    # -- Find posts from a search
    #for thing in reddit.subreddit("pythonforengineers").search('I love python'):
    #    print(thing.title + " - " + thing.author.name + " - " + thing.id)

main()
