@echo off
echo Starting YAA terminals...
wt -w 0 new-tab --title "YAA Bridge" wsl bash -c "cd ~/oe-local && python3 tools/lean4_bridge.py; exec bash"
wt -w 0 new-tab --title "YAA Auto Pusher" wsl bash -c "bash ~/oe-local/auto_push.sh; exec bash"
wt -w 0 new-tab --title "YAA Dashboard" wsl bash -c "bash ~/oe-local/tools/yaa_dashboard.sh; exec bash"
echo All 3 YAA terminals launched.
pause
