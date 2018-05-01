#!/bin/bash
/bin/sleep 5
source /home/shiro/.bashrc
tmux new-session -d -s sbot
tmux send-keys -t sbot "python3 launcher.py" C-m
/bin/sleep 5
tmux send-keys -t sbot "3" C-m
/bin/sleep 3
tmux send-keys -t sbot "1" C-m
/bin/sleep 10
tmux send-keys -t sbot C-m
/bin/sleep 3
tmux send-keys -t sbot "0" C-m
/bin/sleep 3
tmux send-keys -t sbot "0" C-m
/bin/sleep 3
tmux send-keys -t sbot "cd" C-m
/bin/sleep 3
tmux send-keys -t sbot "tmux kill-session -t sbot" C-m
/bin/sleep 3