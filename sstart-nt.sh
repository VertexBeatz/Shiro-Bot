#!/bin/bash
/bin/sleep 5
source /home/shiro/.bashrc
tmux new-session -d -s sbot
tmux send-keys -t sbot "python3 red.py --co-owner 249863021231341568 --co-owner 147369250540093440 --co-owner 375379325643653121 --co-owner 189213698928148481 --co-owner 300696400021159956 --co-owner 423543009494171658 --co-owner 315949158622167041 --co-owner 155149173732147201" C-m
/bin/sleep 5
tmux send-keys -t sbot "1" C-m
/bin/sleep 3
