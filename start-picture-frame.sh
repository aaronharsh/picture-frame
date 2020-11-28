#!/bin/bash

(
    echo Started $$ at $( date '+Y-%m-%d %H:%M:%S' ) > /tmp/picture-frame.pid
    cd ~/picture-frame
    git pull
    source .venv/bin/activate
    python run.py
) &> /tmp/picture-frame.log
