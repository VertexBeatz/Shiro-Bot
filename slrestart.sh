#!/bin/bash
tmux kill-session -t sbot
/bin/sleep 5
source /home/shiro/.bashrc
tmux new-session -d -s sbot
tmux send-keys -t sbot "python3 launcher.py" C-m
/bin/sleep 5
tmux send-keys -t sbot "1" C-m
/bin/sleep 3
tmux attach-session -t sbot
