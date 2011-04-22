# -*- coding: utf-8 -*-

# Squirrel. A simple web project written on Python/Web.py for favorites/bookmarks storage.

import web
import cgi
import datetime
import re
from BeautifulSoup import BeautifulSoup # for parsing chrome & ff bookmarks

import db
import utils
import settings
import urllib


urls = (
    "/", "index",
    "/add", "add",
    "/edit/(\d+|\w+)", "edit",
    "/del/(\d+|\w+)", "delete",
    "/search/(.+)/(\d+)", "search",
    "/squery", "squery",
    "/tags/(.+)/(\d+)$", "tags",
    "/tags/(.+)", "tags",
    "/import", "importf",
    "/error", "error",
    "/saved/(\d+|\w+)", "saved_page",
    "/export", "export_download",
    "/page/(\d+)", "page",
    "/chimage/(\d+|\w+)/(\d+)", "change_image",
    )

# NOTE ABOUT TAGS: 
#   * tags seperated by one whitespace!
#   * adding /DIGIT to /tags/mytag like /tags/mytag/1 will 'enable' pagination.
#   * /tags/mytag will show you all results on one page. (no pagination!)
#   * searching across multiple tags: /tags/book/animals/pdf


# template extension
# Those 4 lines taken from here:
# http://groups.google.com/group/webpy/msg/ea6da02dfb9eedc4
# use $:render.ANOTHER_HTML() in template which you want to extend

# use template_globals to import module in template
# ex: template_globals = { 're': re } 

template_globals = {}
render_partial = web.template.render(settings.TEMPLATES_DIR, globals=template_globals)
render = web.template.render(settings.TEMPLATES_DIR, globals=template_globals)
template_globals.update(render=render_partial) 

app = web.application(urls, globals(), autoreload=True)

class index:
    """
    index page shows all favorites
    template: /templates/index.html
    """
    def GET(self):
        favorites = db.page(to_skip=0)
        return render.index(favorites)

class add:
    """
    add new favorite
    template: /templates/add.html
    """
    def GET(self):
        return render.add()
    def POST(self):
        post_sent = web.input() # returns Storage obj  --> <Storage {'url': u'myurl', 'title': u'mytitle' ...}>
        post_sent['date'] = datetime.datetime.now()
        
        # handle 'Get' && 'Save page' checkboxes:
        flag_get_title = post_sent.has_key('get_title')
        flag_save_page = post_sent.has_key('save_page')
        
        # default
        post_sent['page_path'] = None
        post_sent['images'] = ["/static/missing.ico"] # default icon
        if flag_get_title or flag_save_page:
            post_sent = utils.get_page(post_sent, flag_save_page, flag_get_title)
        db.insert_favorite(post_sent)

        raise web.seeother('/') # go home

class edit:
    """ 
    edit favorite.
    template: /templates/view.html
    """
    def GET(self, favorite_id):
        old_favorite = db.load_fav_by_id(favorite_id)    # load(editing) favorite
        return render.edit(favorite_id, old_favorite)    # pass this favorite into the template
        
    def POST(self, favorite_id):
        """
        save changes.
        """

        post_sent = web.input()
        #post_sent['date'] = datetime.datetime.now() # umcomment if you want to update the date!
        
        old_favorite = db.load_fav_by_id(favorite_id) # load it again
        
        flag_get_title = False
        flag_save_page = False
        
        # update post_sent with old page_path
        # if save_page is True it will be overwritten to new page_path
        # otherwise old value used.
        post_sent['page_path'] = old_favorite['page_path']
        
        # checkboxes
        if post_sent.has_key('get_title'):
            flag_get_title = True
        if post_sent.has_key('save_page'):
            db.delete_saved_page(favorite_id) # remove previous page
            flag_save_page = True
        # if any of two flags is True -> call utils.get_page
        if flag_get_title or flag_save_page:
            post_sent = utils.get_page(post_sent, flag_save_page, flag_get_title)

        db.update_favorite(favorite_id, post_sent) # update
        raise web.seeother('/')# go home

    
class delete:
    """ 
    delete favorite and saved page (if exist)
    template: /templates/view.html
    """
    def GET(self, favorite_id):
        db.delete_favorite(favorite_id)
        raise web.seeother('/')

class tags:
    """
    filter favorites by tag
    filter by multiple tags thru changing the path
        like this: /tags/one_tag/second_tag 
        simple ^_^
        
    template: index.html
    """
    
    def GET(self, tag_input, page_num=-1):
        # page_num=-1 --> if page num not specified --> show all matches on single page.
        if tag_input.find('/'): # if there are slashes --> there are multiple tags. slice them.
            tags_splitted = re.split("/", tag_input)
            search_results = db.filter_by_tag(tags_splitted, page_num)
        else:
            search_results = db.filter_by_tag([tag_input], page_num)
        return render.tags(search_results, tag_input, int(page_num))


class importf:
    """
    import favorites from chrome or firefox
    WARNING: not importing folders, _ONLY_ url's and names (-as titles)
    NOTE: all imported favorites have tag 'imported' by default
    """
    def GET(self):
        return render.importf()
       
    def POST(self):
        try:
            post_file = web.input(file={})
        except:
            return "File too large!"
        cgi.maxlen = settings.MAX_IMPORTED_FILE
        if 'file' in post_file:                              # if there is an attached file -> good!
            if post_file['file'].filename.endswith('.html'): # luckily chrome && firefox use same structure for storing bookmarks
                file_contents = post_file['file'].value
                
                soup = BeautifulSoup(file_contents)
                bookmarks = soup.findAll('a')

                # access to attribute: each['ATTRIBUTE']
                for each in bookmarks:
                    # WARNING!: some special characters should be removed or you'll be hitten by:
                    #   UnicodeEncodeError: 'charmap' codec can't encode character u'\xab' in position 51: character maps to <undefined>
                    # or something similiar.
                    title = re.sub("['\$\"<>]",'', each.string)
                    url = each['href']
                    db.insert_favorite( {'url': url, 'title': title, 'description' : 'empty', 'tags': 'imported', 'date': datetime.datetime.now(), 'page_path': None, 'images': ['/static/missing.ico']} )
                return web.seeother("/")
                
            else:
                return web.seeother("/error")   # bad file format
        else:
            return web.seeother("/error")       # no file attached!


class saved_page:
    """
    shows the saved favorite page. favorite ID required.
    """
    def GET(self, favorite_id):
        page_path = db.saved_page_path(favorite_id)
        f = open(page_path,"r")
        html = f.read()
        f.close()
        return html

class export_download:
    """
    WARNING!: TAGS AND DESCRIPTION WILL NOT BE EXPORTED!!!
    returns exported favorites as .html for download.
    """
    
    def GET(self):
        favorites_html = """
        <!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
     It will be read and overwritten.
     DO NOT EDIT! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
    <DT><H3 ADD_DATE="0" PERSONAL_TOOLBAR_FOLDER="true">Imported</H3>
    <DL><p>
        """
        for each in db.load_favorites():
            title = each['title']
            url = each['url']
            favorites_html = favorites_html + "<DT><A HREF=\"" + url.encode('utf-8') + "\">" + title.encode('utf-8') + "</A>\n"
        favorites_html += "\t</DL><p>\n</DL><p>"
        web.header('Content-Type', 'html')
        web.header('Content-disposition', 'attachment; filename=' + 'favorites.html')
        return favorites_html


class search:
    """
    search + pagination
    """
    def GET(self, search_query, page_num):
        """ 
        input: user's query (search_query)
        output: matching results 
        """
        
        path = search_query.split('/') # split query
        
        # FUTURE POSSIBLE BUG: SUPPLYING LESS PARAMETERS WILL CAUSE TO UNEXECPETED RESULTS
        search_for = path[0] # searching query word is always first
        # options are everything else (-options are places you want to search in: title, description etc.)
        options = path[1:]
        options_path = "/".join(options) # build path of options
        search_result = db.search(search_for, options, int(page_num))
        return render.search(search_result, search_for, int(page_num), options_path)

class squery:
    """
    search query. search form handled here.
    used by search.html
    """
    def POST(self):
        post_sent = web.input() # get user's query
            
        checkboxes = ['title', 'url', 'desc', 'tags'] # all checkboxes 
        options = []
        options_path = ''
        for each in checkboxes:
            if post_sent.has_key(each):
                options_path += ( each + '/' ) # build a path (-like /title/tags/ ) of selected checkboxes by user.
                options.append(each) # remember what checkboxes was 'checked'
                
        # quote search_query & redirect to /search/my_query/page_number
        return web.seeother('/search/' + urllib.quote(post_sent['search_query'].encode('utf-8')) + '/' + options_path + '0')
        
class page:
    """
    pagination for index page
    """
    
    def GET(self, page_num):
        favorites = db.page(to_skip=int(page_num))      # get next favorites
        return render.page(favorites, int(page_num))    # show them in the template
        
class change_image:
    def GET(self, favorite_id, img_index):
        db.change_front_image(favorite_id, img_index)
        
        
class error:
    """ 
    stupid error page.
    """
        
    def GET(self):
        return render.error()
        
        
if __name__ == "__main__":
    app.run()