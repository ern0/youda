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
    http://localhost:8009/q=%s <br />
    where "%s" is the variable name for the selected URL

## How to use ##
  - start this script in a shell window: <br />
      youda.py <port> [<download-dir> [<check-dir> [<check-dir>...]]] <br />
    example:
      youda.py 8009 ~/Downloads/youtube /media/nexus7/storage/sdcard0/Podcasts/ <br />
    If you specify download-dirs, duplications will be also <br />
    checked in these directories
  - in your browser, right-click in a YouTube link and <br />
    select custom context menu item you've added
  - this script will catch the URL and call youtube-dl with it

## Under the hood ##
  - when you add a file, the web server thread creates a placeholder file
  - the processing thread scans the directory, picks first placeholder file, 
    then replaces it with the downloaded file
  - upon counter overflow, the items above 555 will appear before others,
    e.g. the order will be: 910, 911, 922, 930, 001, 002, 003
  - because the queue is stored in files, script can be restarted
