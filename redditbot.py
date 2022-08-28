#!/usr/env python3

import praw
import feedparser
import time
import pickle
from bs4 import BeautifulSoup
from bs4.element import Tag

# NOTE: For the sake of this script, "latest" means the latest entry from a particular platform. "Last" referrs to the
# last post that the script itself has parsed and uploaded to reddit.

def htmltomd(element, ret='', indent=''):
    if type(element) != Tag:
        return ret
    
    print(indent + element.name)
    
    if element.name == 'br':
        ret += ' \n'
        #return ret
        
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
        ret+='[{}]({})'.format(element.string, element['href'])

    # Convert images to links
    if element.name == 'img':
        ret+='\n[[Image: {}]]({})\n'.format(element['alt'], element['src'])

    if element.name == 'li':
        print(element.string)
        
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
            if type(child) == Tag and child.name != 'br':
                childCount += 1
                ret = htmltomd(child, ret, indent+'\t')
                # Don't += ret because you're already passing ret, and it will return ret +=
                # whatever it has to offer.

        if childCount == 0:
            if element.name in ['p', 'li', 'i', 'em', 'b', 'strong']:
                ret += element.get_text().strip()
                
    # Second half of pre/suffix combinations
    if element.name == 'sup':
        ret+=')'
    elif element.name == 'b' or element.name == 'strong':
        ret+='**'
    elif element.name == 'i' or element.name == 'em':
        ret+='*'
    elif element.name == 'p':
        ret+=' \n'

    #print("ret at depth {}".format(len(indent)))
    #print(ret)
    return ret
        

def main():
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
                output = ''
                htmlContent = BeautifulSoup(entry['content'][0]['value'], 'html.parser')

                for element in htmlContent:
                    output += htmltomd(element)

                #newPost = reddit.subreddit('uvixsandbox').submit(title=entry['title'],selftext=output)
                #print(newPost)
                print('\n\nPRINTING POST FROM {}'.format(entry['published']))
                print(output)

    print('Last post from the news feed was {}'.format(time.strftime('%Y-%m-%d %H:%M:%S',lastPosts['newsFeed'])))
    #print(newsFeedLast)
    #print(newsFeed['entries'][pos]['published'])
    #print(newsFeed['entries'][pos]['content'][0].keys())

    # -- Make a post, grab the `submission` object, reply to it. Also grab the ID of the reply
    title="My Third Bot Post"
    body="Does the subreddit.submit() method return a whole submission object that I can reply to?"
    #newPost = reddit.subreddit('pythonforengineers').submit(title=title,selftext=body,flair_id=None,flair_text=None)
    #newReply = newPost.reply("If you can see this, yes")
    #print(newPost)

    # -- Find posts from a search
    #for thing in reddit.subreddit("pythonforengineers").search('I love python'):
    #    print(thing.title + " - " + thing.author.name + " - " + thing.id)

main()
