#!/bin/bash

osascript -e 'tell app "Terminal"
    do script "cd ~/xfiles-generator && source env/bin/activate && make start"
end tell'

source env/bin/activate && make run
