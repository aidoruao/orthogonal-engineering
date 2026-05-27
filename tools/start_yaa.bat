@echo off
wt -w 0 new-tab --title "YAA Bridge" wsl bash -c "/usr/bin/python3 /home/idor/oe-local/tools/lean4_bridge.py"
wt -w 0 new-tab --title "YAA Auto Pusher" wsl bash -c "/usr/bin/bash /home/idor/oe-local/auto_push.sh"
wt -w 0 new-tab --title "YAA Dashboard" wsl bash -c "/usr/bin/bash /home/idor/oe-local/tools/yaa_dashboard.sh"
