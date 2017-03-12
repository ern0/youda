#!/bin/bash

clear ; youda.py 8009 ~/Downloads/youtube ~/Downloads/* /media/nexus7/storage/sdcard0/stuff/* ; exit

if [[ -z `tmux ls | grep youda` ]]; then
	tmux new -d -s youda "youda.py 8009 ~/Downloads/youtube /media/nexus7/storage/sdcard0/stuff/* ; cat"
	tmux split-window "bash ; tmux kill-session -t youda"
	tmux a
else
	curl http://localhost:8009/?q=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3DcwZPaTUe6M8%26t%3D0s
	ls -l ~/Downloads/youtube | grep youda
fi
