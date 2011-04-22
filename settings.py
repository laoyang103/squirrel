# -*- coding: utf-8 -*-

# CONFIGURATION

import os


# DB: MongoDB
DB_HOST = 'localhost'
DB_PORT = 27017
DB_NAME = "favorites"


# SAVED PAGES STORE LOCATION
SAVED_PAGES_DIR = os.getcwd() + "\\saved\\" # WARNING! its windows style path. use /saved/ on linux.

# TEMPLATES DIR
TEMPLATES_DIR = os.getcwd() + "\\templates\\"  # WARNING! its windows style path. use /templates/ on linux.

# PAGING
PER_PAGE = 5 # favorites per each page


# ALLOWED IMAGE EXTENSIONS
# used in utils.py
ALLOWED_EXTENSIONS = ('jpg', 'ico', 'png')

# MAXIMUM TITLE LENGTH
MAX_TITLE_LENGTH = 140 # BE SURE TO CHANGE THIS VALUE ALSO IN VALIDATOR AT add.html (javascript)

# MAX IMPORTED FILE SIZE
MAX_IMPORTED_FILE = 5 * 1024 * 1024 # 5 MB