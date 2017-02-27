youda.py
========
*Youtube Downloader Automation*

## How to setup ##

  - download this script to your computer
  - install youtube-dl <br />
    on a Mac: brew install youtube-dl <br />
    on any OS: sudo pip install --upgrade youtube_dl
  - install a context-menu extension in your browser <br />
    e.g. Context Menus for Chrome https://goo.gl/8hgwuB
  - add a custom action for links, which sends the URL to <br />
    http://localhost:8012/q=%s <br />
    where "%s" is the variable name for the selected URL


## How to use ##
  - start this script in a shell window: <br />
    youda.py 8009 ~/Downloads/youtube
  - in your browser, right-click in a YouTube link and <br />
    select custom context menu item you've added
  - this script will catch the URL and call youtube-dl with it
  - do not abort the script until it finishes