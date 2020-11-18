# Semi-Auto-Uploader

This has been tested and works with [Debian 10 Buster](https://www.debian.org/News/2019/20190706).

This script is designed to make uploading as easy as possible using a simple one line command from the terminal it will create screenshots and upload them to Imgur and create the torrent, upload it to NBL and fast resume in rtorrent and seed to NBL.

We will be using the [rtinst seedbox script](https://github.com/arakasi72/rtinst).

```sudo bash -c "$(wget --no-check-certificate -qO - https://raw.githubusercontent.com/arakasi72/rtinst/master/rtsetup)"```

**Now you will need to install the some python libraries, dependencies & tools:**

`sudo apt-get install build-essential && sudo apt install python-pip`

`sudo pip install setuptools wheel`

`sudo pip install pyimgur selenium pyvirtualdisplay parse-torrent-name pymediainfo`

**Next install the module named libtorrent:**

`sudo apt-get install python-libtorrent`

**Now install xvfb and geckodrive**r:

`sudo apt-get install xvfb`

`sudo wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz`

`tar -xvzf geckodriver*` & `chmod +x geckodriver`

`sudo mv geckodriver /usr/local/bin/`

**Next navigate to /usr/local and download and install Firefox:**

`cd /usr/local`

`sudo wget http://ftp.mozilla.org/pub/firefox/releases/68.0/linux-x86_64/en-US/firefox-68.0.tar.bz2`

`tar xjf firefox*`

`sudo ln -s /usr/local/firefox/firefox /usr/bin/firefox`

**You will need to install some packages:**

`sudo apt-get install libgtk-3-dev`

**This will fix the hidden ^M chars in the perl script:**

`sudo apt-get install dos2unix`

**You will need to install Cpan and at the very minimum install the following module:**

`sudo cpan` & `install Convert::Bencode_XS`

**Open up your favorite text editor and copy/paste/save the following and name them correctly as needed. Once done place both files in:**

`/home/username`

**You will need to do for both files**

`chmod a+x`

**You will need to in the correct location to initiate the script:**

```/home/username/rtorrent/download```

**Now execute the script with one line for example:**

`python ~/auto_upload_v0.2.py diners.drive.ins.and.dives.s30e07.international.infusion.hdtv.x264-w4f.mkv`

That is pretty much it!
