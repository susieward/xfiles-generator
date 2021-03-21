#!/bin/bash

sudo -S systemctl stop xfiles-generator
cd ~/xfiles-generator
unset GIT_DIR
git pull
source env/bin/activate
pip3 install -r requirements.txt
deactivate
cd ~/
sudo -S systemctl start xfiles-generator
