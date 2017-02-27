youda.py
========
*Youtube Downloader Automation*

## How to setup ##

  - download this script to your computer, then
    change download path and listen port, if you want
  - install youtube-dl 
    on a Mac: brew install youtube-dl
    on any OS: sudo pip install --upgrade youtube_dl
  - install a context-menu extension in your browser
    e.g. Context Menus for Chrome https://goo.gl/8hgwuB
  - add a custom action for links, which sends the URL to
    http://localhost:8012/q=%s
    where "%s" is the variable name for the selected URL

## How to use ##
  - start this script in a shell window
  - in your browser, right-click in a YouTube link and
    select custom context menu item you've added
  - this script will catch the URL and pass it to youtube-dl
  - do not abort the script until it finish