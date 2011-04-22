# -*- coding: utf-8 -*-

# various helpful functions

import httplib
import re
import sys
from BeautifulSoup import BeautifulSoup
import datetime
import os
import settings

def get_page(post_sent, flag_save_page, flag_get_title):
    """
    grab_title() -- extracts and returns title from <title></title> tags
    save_page_copy() -- saves page(text only) and returns a path.
    used by: main.py -> class edit, class add
    """
    
    url = re.sub("http:\/\/","",post_sent['url']) # remove http://  -> [http://]www.example.com/my/path
    
    try:
            path = re.search("(\/(.+|.?))", url).group(0) # get path www.example.com[/my/path]
    except AttributeError: # it's only www.example.com. then add '/'.
            path = '/'
            url = url + '/'

    ind = url.find("/") # host is all characters until the first /
    host = url[0:ind]

    conn = httplib.HTTPConnection(host)
    
    try: # catch failure.
        conn.request("GET", path)
    except: # failure
        #post_sent.pop('save_page') # page will not be saved
        if flag_get_title:
            post_sent['title'] = url
        return post_sent
    
    response = conn.getresponse() # --a think about adding timeout!
    if (response.status == 200) and (response.msg.getmaintype() == 'text'): # if response is OK (200) AND response main type is 'text' then
        html = response.read()
        soup = BeautifulSoup(html)
    else: # on bad response OR on bad maintype --> page will not be saved
        #post_sent.pop('save_page')
        if flag_get_title:
            post_sent['title'] = url
        return post_sent
        
    conn.close()
    
    # function to grab links on images
    def grab_links(): 
            link_tag = soup.findAll('link') # <link href
            a_tag = soup.findAll('a') # <a href=
            img_tag = soup.findAll('img') # <img src=
        
            grabbed = [] # every link we find we'll store it here

            # accessing attributes
            try:        
                for each in a_tag:
                    grabbed.append(each['href'])
            except:
                pass
        
            try:
                for each in img_tag:
                    grabbed.append(each['src'])
            except:
                pass

            try:        
                for each in link_tag:
                    grabbed.append(each['href'])
            except:
                pass
            links = []
            # select links only with allowed extension (defined in settings.py)
            for each in grabbed:
                for ext in settings.ALLOWED_EXTENSIONS:
                    if each.endswith(ext): # it's an allowed extension
                        if each[0] == '/': # it's a path
                            print host+'/'+each[1:]
                            links.append("http://www." + host+'/' + each[1:]) # remove '/' from link because host already have slash!
                        else:
                            links.append(each) # it's a link
                        break
            print links
            return links
        
        
    def grab_title():
        try: # try to find the page <title>
            title = re.sub("\s+", " ", soup.html.head.title.string)
            if len(title) > settings.MAX_TITLE_LENGTH: # cut title if it's above max allowed length
                title = title[0:settings.MAX_TITLE_LENGTH]
        except: # failure. use url as title.
            title = 'None'
        return title
        
    def save_page_copy():
        dateobj = datetime.datetime.now()
        page_path = host + '-' + str(dateobj.day) + '-' + str(dateobj.month) + '-' + str(dateobj.year) + '--' + str(dateobj.hour) + '-' + str(dateobj.minute) + '-' + str(dateobj.second)
        page_path = settings.SAVED_PAGES_DIR + page_path + '.html'
        f = open(page_path, "w")
        f.write(html)
        f.close()
        return page_path


    if flag_save_page:
        post_sent['page_path'] = save_page_copy()

    if flag_get_title:
        post_sent['title'] = grab_title()

    post_sent['images'] = grab_links()
    post_sent['images'].append("/static/missing.ico") # default '/static/missing.ico' icon
    return post_sent