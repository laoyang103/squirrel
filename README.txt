
# ABOUT
contact: edoomik@gmail.com

Squirrel. A simple web project written on Python/Web.py for favorites/bookmarks storage.

# FEATURES:
	-- search
	-- filter favorites by multiple tags
	-- import your favorites from Firefox && Chrome
	-- export
	-- save local copy(text only) of favorite


# INSTALLATION

1. Web.py 0.34
http://webpy.org/static/web.py-0.34.tar.gz
	-cd to downloaded archive
	-python setup.py install

2. BeautifulSoup 3.2.0
http://www.crummy.com/software/BeautifulSoup/#Download
	-cd to downloaded archive
	-python setup.py install

3. MongoDB 1.8.1
http://www.mongodb.org/downloads
	-unpack
	-add unpacked folder path to your system environment variable
	-create folder named data in /mongodb-root/
	-create folder named db in /mongodb-root/data


4. setuptools-0.6c11.win32-py2.7.exe
http://pypi.python.org/pypi/setuptools#files
	-add C:\Python2.7\Scripts to your system environment variable (assuming your python installed on C:)

5. install pymongo 1.10.1
from cmd: easy_install pymongo


6. configure projects /settings.py file.

7. launch web app:
	-launch mongodb: mongod -dbpath=C:\mongodb-bin\data\db -port 27017
	-cd to your squirrel root dir
	-python squirrel.py

8. enjoy.
