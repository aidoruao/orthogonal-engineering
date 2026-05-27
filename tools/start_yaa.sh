#!/bin/bash
# Start all 4 YAA terminals in WSL2

# Terminal 1: Lean4 Bridge (port 28428)
wt -w 0 new-tab --title "YAA Bridge" bash -c "cd ~/oe-local && python3 tools/lean4_bridge.py; exec bash" &

# Terminal 2: Auto Pusher
wt -w 0 new-tab --title "YAA Auto Pusher" bash -c "cd ~/oe-local && bash auto_push.sh; exec bash" &

# Terminal 3: Dashboard
wt -w 0 new-tab --title "YAA Dashboard" bash -c "bash ~/oe-local/tools/yaa_dashboard.sh; exec bash" &

# Terminal 4: Main Working Terminal (YAA)
wt -w 0 new-tab --title "YAA Main" bash -c "cd ~/oe-local && exec bash" &

echo "All 4 YAA terminals launched."
