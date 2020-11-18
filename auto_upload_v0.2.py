#!/usr/bin/python
# Auto Upload v0.2

import sys, os, shutil
import getopt
import pyimgur
import subprocess
import libtorrent as lt
import time
import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from pyvirtualdisplay import Display
import PTN
import json
import re
from pymediainfo import MediaInfo

##### Configuration #####

## Files/Folders

# Working dir where media file/folder is stored, dupe/complete file will be written here and NBL torrent downloaded to before moving to watch folder
workingdir = "/home/foo/rtorrent/download/"

# Webserver directory for mediainfo/screen caps dir
# Set localhosted to True if you want to have the screen caps and mediainfo saved to your webserver dir specified, if not mediainfo & screencaps will be saved to tempdir below
localhosted = False
localdir = "/var/www/html/screencaps/"

# Dir used for mediainfo/screencap files if localhosted = False
tempdir = "/home/foo/tmp/"

# Where to save generated torrent
torrentdir = "/home/foo/rtorrent/upload/"

# File/folder destination for seeding, copytoseeddir must equal true to copy files
copytoseeddir = False
seeddir = "/home/foo/rtorrent/"

# Path to fast resume perl script
fastresumescript = "/home/foo/fast_resume.pl"

# Torrent watch destination (dir needs to exist)
watchdir = "/home/foo/rtorrent/watch/"

# Torrent file name wildcard to move to watch dir
torrentoutputfile = "*Nebulance.io*.torrent"


## Imgur
# Create an app in your imgur account and specify client ID below.
# Upload to imgur if uploadtoimgur = True
uploadtoimgur = False
imgur_client_id = "NOT IN USE"


## NBL Settings
# Automatically upload to NBL
uploadtonbl = True
# Specify your personal announce url
announceurl = "https://nebulance.io:2001/xxxxxxxxxxxxxxxxxxxxxxxxx/announce"
# Site username
username = "foo"
# Site password
password = "YOUR_PASSWORD_HERE"
# Site login url
loginurl = "https://nebulance.io/login.php"
# Site upload url
uploadurl = "https://nebulance.io/upload.php"
# Site my uploads url
torrentlisturl = "https://nebulance.io/torrents.php?type=uploaded&userid=YOUR_UID_HERE"

##### Configuration Ends #####

path = sys.argv[1]
fullpath = workingdir + path

if localhosted:
    outputdir = localdir
else:
    outputdir = tempdir

# Check if file or folder
if os.path.isdir(path):
    folder = True
    name = path
    
    objects = os.listdir(path + "/")
    sofar = 0
    biggestfile = ""
    for item in objects:
        size = os.path.getsize(path + "/" + item)
        if size > sofar:
            if "'" not in item and "," not in item:
                sofar = size
                biggestfile = item
    print("Using " + biggestfile)
    firstfile = path + "/" + biggestfile
else:
    folder = False
    name = path.rsplit( ".", 1 )[ 0 ]
    firstfile = path

# Get media info
media_info = MediaInfo.parse(firstfile)
if media_info.tracks[0].duration:
    duration_in_ms = media_info.tracks[0].duration
    duration_in_min = duration_in_ms / 60000
    duration_in_sec = duration_in_ms / 1000
else:
    duration_in_sec = 60

# Create Screenshots
screencapnum = 4
screncapinterval = round(duration_in_sec / (screencapnum + 1), 0)

screendir = outputdir + name
if os.path.isdir(screendir):
    shutil.rmtree(screendir) 
capdircmd = "mkdir -p " + outputdir + name
os.system(capdircmd)
quality = 0

# Generate screencaps if season with decreasing quality under 2 are under 10mb
if folder:
    screens = []
    while (len(screens) < 2):
        timestamp = 1
        quality+= 1
        for x in range(1,screencapnum+1):
            timestamp = timestamp + screncapinterval
            timestamptxt = str(datetime.timedelta(seconds=timestamp))
            capcmd = "ffmpeg -ss '" + timestamptxt + "' -an -vsync 0 -sn -t 1 -hide_banner -loglevel warning -i " + firstfile + " -y -f mjpeg -q:v " + str(quality) + " " + outputdir + name + "/" + str(x) + ".png"
            print(capcmd)
            os.system(capcmd)
        for i in range (1, screencapnum+1):
            screenfile = screendir + "/" + str(i) + ".png"
            if os.path.getsize(screenfile) < 10000000:
                screens.append(str(i))

    print("Using cap " + screens[0] + " and cap " + screens[1] + " with quality " + str(quality))

print("Files stored in " + screendir)

# Upload Screenshots to Imgur if season
if folder and uploadtoimgur:
    im = pyimgur.Imgur(imgur_client_id)
    uploaded_image1 = im.upload_image(screendir + "/" + screens[0] + ".png", title = name + "_1")
    print(uploaded_image1.link)
    imageurl1 = uploaded_image1.link
    imageurl1 = imageurl1.replace("http://", "https://")
    uploaded_image2 = im.upload_image(screendir + "/" + screens[1] + ".png", title = name + "_2")
    print(uploaded_image2.link)
    imageurl2 = uploaded_image2.link
    imageurl2 = imageurl2.replace("http://", "https://")
    imagecode = "[img]" + imageurl1 + "[/img][img]" + imageurl2 + "[/img]"


# Mediainfo file
print("Generating mediainfo file")
mediainfopath =  outputdir + name + "/_rawmediainfo.txt"
mediainfofixedpath = outputdir + name + "/_mediainfo.txt"

mediainfocmd = "mediainfo " + firstfile + " >> " + mediainfopath
os.system(mediainfocmd)

bad_mediainfo_tags = ['gsst','gstd','gssd','gssd','gshh','Attachements']
with open(mediainfopath) as oldfile, open(mediainfofixedpath, 'w') as newfile:
    for line in oldfile:
        if not any(bad_tag in line for bad_tag in bad_mediainfo_tags):
            newfile.write(line)
oldfile.close()
newfile.close()

mediainfotext = open(mediainfofixedpath, 'r').read()
mediainfotext = unicode(mediainfotext, errors='ignore')


# Create torrent file
torrentname = name + ".torrent"
torrentfile = torrentdir + torrentname
print("Creating torrent " + torrentname)
fs = lt.file_storage()
lt.add_files(fs, path)
t = lt.create_torrent(fs)
t.add_tracker(announceurl, 0)
t.set_priv(True)
lt.set_piece_hashes(t, ".")
torrent = t.generate()    
f = open(torrentfile, "wb")
f.write(lt.bencode(torrent))
f.close()



# Get show name
shownamedata = PTN.parse(torrentname)
print(shownamedata)
showname = shownamedata['title']

# See if PTN finds season/episode
ptnseasonfail = False
try:
    shownamedata['season']
except:
    ptnseasonfail = True

ptnepisodefail = False
try:
    shownamedata['episode']
except:
    ptnepisodefail = True

# Get season/episode number
if not ptnseasonfail and not ptnepisodefail:
    seasonnum = shownamedata['season']
    episodenum = shownamedata['episode']
    seasonepisode = "S" + str(seasonnum).zfill(2) + "E" + str(episodenum).zfill(2)
else:
    seasonnum = re.search("\.([S]\d{1,3})\.", torrentname )
    if seasonnum:
        seasonepisode = seasonnum.group(1)
    else:
        seasonepisode = ""

print("Season/Episode is " + str(seasonepisode))

# Remove season from showname
seasons = []
for x in range(0, 99):
    if x < 10:
        seasons.append(" S0" + str(x))
        showname = showname.replace(seasons[x],"")
    else:
        seasons.append(" S" + str(x))
        showname = showname.replace(seasons[x],"")        

print("Show is " + showname)

# Copy to seeding dir
if copytoseeddir:
    print("Copying " + fullpath)
    if folder:
        if not os.path.isdir(seeddir + path):
            shutil.copytree(fullpath, seeddir + path)
    else:
        shutil.copy2(fullpath, seeddir)

# Upload to website
if uploadtonbl:
    print("Opening Browser to upload")
    display = Display(visible=0, size=(800, 600))
    display.start()

    # Open Browser
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2)
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', workingdir)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'application/x-bittorrent')
    profile.update_preferences()

    browser = webdriver.Firefox(profile)

    # Login
    print("Logging into NBL")
    browser.get(loginurl)
    print(browser.current_url)
    time.sleep(3)
    usernamefield = browser.find_element_by_id("username")
    passwordfield = browser.find_element_by_id("password")
    usernamefield.send_keys(username)
    passwordfield.send_keys(password)
    login_attempt = browser.find_element_by_xpath("//*[@type='submit']")
    login_attempt.submit()
    time.sleep(3)

    # Upload
    print("Uploading to NBL")
    browser.get(uploadurl)
    print(browser.current_url)
    time.sleep(3)
    browser.find_element_by_id("file").send_keys(torrentfile)
    time.sleep(3)
    categoryselect = Select(browser.find_element_by_id("category"))
    if folder:
        categoryselect = categoryselect.select_by_value('3')
    else:
        categoryselect = categoryselect.select_by_value('1')
    time.sleep(3)
    browser.find_element_by_id("media").send_keys(mediainfotext)
    time.sleep(3)
    if folder:
        browser.find_element_by_id("screens").send_keys(imagecode)
        time.sleep(3)

    # browser.execute_script("document.getElementBy('post').click()")
    postbutton = browser.find_element_by_id("post")
    browser.execute_script("arguments[0].click();", postbutton)

    time.sleep(5)

    print("Dupe check")
    print(browser.current_url)
    dupe = False
    possdupe = False

    try:
        browser.find_element_by_name('ignoredupes')
        possdupe = True
    except NoSuchElementException:
        possdupe = False

    if possdupe:
        try:
            browser.find_element_by_partial_link_text(showname + " - " + seasonepisode)
            dupe = True
        except NoSuchElementException:
            dupe = False
            browser.find_element_by_name("ignoredupes").click()
            time.sleep(1)
            # browser.execute_script("document.getElementById('post').click()")
            postbutton = browser.find_element_by_id("post")
            browser.execute_script("arguments[0].click();", postbutton)

    alert = ""
    try:
        alert = browser.find_element_by_class_name("alert").text
    except:
        print "No alert found"

    if 'file already exists' in alert:
        dupe = True

    if dupe:
        dupefile = fullpath + "_DUPE.txt"
        open(dupefile, 'a').close()   
    else:
        time.sleep(5)
        print(browser.current_url)
        time.sleep(5)
        browser.get(torrentlisturl)
        time.sleep(5)
        try:
            browser.find_element_by_css_selector("a[href*='torrents.php?action=download']").click()
            print("Downloaded")
            time.sleep(5)
            fastrescmd = fastresumescript + " -b " + workingdir + " -d " + watchdir + " -r  -v " + torrentoutputfile
            os.system(fastrescmd)
            print("torrent moved")
        except:
            print("No download")
    time.sleep(1)

    # Close Browser
    print("Closing browser")
    browser.quit()
    time.sleep(5)
    display.stop()

    print("Clean up")
    removegeckologcmd = "rm " + workingdir + "geckodriver.log"
    os.system(removegeckologcmd)

# All done - create complete file
donefile = fullpath + "_COMPLETE.txt"
open(donefile, 'a').close()
