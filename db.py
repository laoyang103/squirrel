# -*- coding: utf-8 -*-

# database related

# Database: MongoDB
# NOTE: 32-bit builds are limited to around 2GB of data. 
#   See http://blog.mongodb.org/post/137788967/32-bit-limitations for more information.

 
import pymongo
import bson
import settings
import re
import os

# database connection
connection = pymongo.Connection(settings.DB_HOST, settings.DB_PORT)
db = connection[settings.DB_NAME]


def insert_favorite(web_input):
    """ 
    insert into database new favorite 
    page_path - if user decides to save the page then [page_path] have to be provided, otherwise it's --> None.
    used by: squirrel.py -> class add
    template: /templates/add.html
    """
    favorite = {
                "url":          web_input["url"],           # url (string)
                "title":        web_input["title"],         # title (string)
                "description":  web_input["description"],   # page description (string)
                "tags":         web_input["tags"].lower().split(" "), # tags stored as array -> ['tag1', 'tag2', 'tag3']
                "date":         web_input["date"],          # datetime (datetime object)
                "page_path":    web_input["page_path"],     # page path -> full path(string) or None
                "images":       web_input["images"]         # urls of various images that were recognized on page (array)
                }
    
    db.favorites.insert(favorite)
    
    
def load_favorites():
    """ 
    load all favorites.
    used by: squirrel.py -> class index
    template: /templates/index.html
    """
    return db.favorites.find() # returns a Cursor instance ( iterable:  for i in cursor_object )
    
    
def load_fav_by_id(favorite_id):
    """ 
    load favorite by ID 
    loads data into form at /templates/edit.html
    used by: squirrel.py -> class edit
    template: /templates/index.html, /templates/search.html
    """
    # find and return only one favorite
    return db.favorites.find_one( {"_id": bson.ObjectId(favorite_id)} )


def update_favorite(favorite_id, web_input):
    """ 
    update favorite by ID.
    used by: squirrel.py -> class edit
    template: /templates/edit.html
    note: add "date" : web_input["date"] to update date time after each edit.
        (-in addition, uncomment related datetime lines in squirrel.py/class edit)
    """
    favorite = db.favorites.find_one( {"_id" : bson.ObjectId(favorite_id)} )
    db.favorites.update( {"_id" : bson.ObjectId(favorite_id)}, {"$set" : {"url" : web_input["url"], "title" : web_input["title"], "description": web_input["description"], "tags" : web_input["tags"].lower().split(" "), "page_path": web_input["page_path"]} } )
    
   
def delete_favorite(favorite_id):
    """ 
    delete favorite AND it's saved page.
    used by: squirrel.py -> class delfav
    template: /templates/index.html, /templates/search.html
    """

    favorite = db.favorites.find_one( {"_id" : bson.ObjectId(favorite_id)} )
    try:
        os.remove(os.path.normcase(favorite['page_path']))
    except: # can't delete (doesnt exist? no permission?)
        pass
    
    db.favorites.remove( {"_id" : bson.ObjectId(favorite_id)} )
    

def search(search_query, opts, to_skip):
    """
    search.
    used by: class search, class squery
    template: /templates/search.html
    """
    reg = re.compile(search_query, re.I | re.U) # ignore case & unicode flags
    query_params = []
    for each in opts: # create parameters for mongodb
        query_params.append({each: reg})

    return db.favorites.find({"$or" : query_params}, skip=to_skip*settings.PER_PAGE).sort([("_id",pymongo.DESCENDING)]).limit(settings.PER_PAGE)

    

def filter_by_tag(tag_input, to_skip):
    """ 
    search for favorites by tag.
    used by: squirrel.py -> class tags
    template: /templates/index.html, /templates/search.html
    """
    
    # $all --> favorite must include all tags in order to be accepted.
    # can be changed to $or
    if to_skip == -1: # then let's show ALL favorites containing those tags
        return db.favorites.find( {"tags": {"$all": tag_input} }, sort=[('_id', pymongo.DESCENDING)])
        
    return db.favorites.find( {"tags": {"$all": tag_input} }, sort=[('_id', pymongo.DESCENDING)], skip=int(to_skip)*settings.PER_PAGE, limit=settings.PER_PAGE)

def saved_page_path(favorite_id):
    """ 
    returns page's path (favorite id is required!)
    used by: squirrel.py -> class saved_page
    """
    favorite = db.favorites.find_one( {"_id" : bson.ObjectId(favorite_id)} )
    return favorite["page_path"]

        
def page(to_skip):
    """
    input: to_skip -- number of pages to skip.
    returns number of [settings.PER_PAGE] favorites in descending order (from new to old).
    used by: class page, class index
    template: /templates/page.html
    """
    
    # NOTE: maybe i'll try to optimize it later 
    # keywords for further look: indexes, descending order, datetime as index
    return db.favorites.find(sort=[('_id', pymongo.DESCENDING)], skip=to_skip*settings.PER_PAGE, limit=settings.PER_PAGE)
    

def change_front_image(favorite_id, img_index):
    """
    changes front image of the favorite.
    input:  favorite_id
            img_index -- new image index
    output: no. every time user clicks on image, it changes.
    template: /templates/edit.html
    used by: class change_image
    """
    img_index = int(img_index)
    favorite = db.favorites.find_one( {"_id" : bson.ObjectId(favorite_id)} )
    # swap between images path's, new selected image goes to [0] index.
    images = favorite['images']
    old_front_image = images[0] # [0] image is the front image
    images[0] = images[img_index] # set new front image
    images[img_index] = old_front_image
    db.favorites.update( {"_id" : bson.ObjectId(favorite_id)}, {"$set" : {"images": images} } )
    
    
def delete_saved_page(favorite_id):
    """ 
    delete _only_ favorite's saved page
    used by: squirrel.py -> class edit
    template: /templates/edithtml
    """

    favorite = db.favorites.find_one( {"_id" : bson.ObjectId(favorite_id)} )
    
    # remove the page from disk && update page_path to 'empty'.
    try:
        
        os.remove(os.path.normcase(favorite['page_path']))
        db.favorites.update( {"_id" : bson.ObjectId(favorite_id)}, {"$set" : {"page_path": 'empty'} } )

        favorite = db.favorites.find_one( {"_id" : bson.ObjectId(favorite_id)} )
        print "FAVORITE page_path changed to: " + favorite['page_path']
    except:
        pass
    