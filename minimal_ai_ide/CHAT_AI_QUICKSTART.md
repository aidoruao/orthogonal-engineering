# Σ_LORA CHAT AI - QUICK START GUIDE

## 🚀 GET STARTED IN 3 MINUTES

### Step 1: Start the AI Server
```bash
cd minimal_ai_ide
start_chat_ai.bat
```
Server runs at: `http://localhost:8080`

### Step 2: Deploy to Minecraft
```bash
deploy_chat_ai.bat
```

### Step 3: Play Minecraft
1. Launch "Logos_World_01" in Minecraft
2. Find a ComputerCraft computer
3. Attach a **Chat Box** peripheral to any side
4. Computer auto-starts the AI system
5. In Minecraft chat, type: `!ai help`

## 💬 BASIC USAGE

### Chat Commands:
```
!ai help                    - Show this help
!ai dig a 3x3 room         - Dig with safety
!ai build a small house    - Build guidance
!ai find diamonds          - Exploration help
!ai craft diamond pickaxe  - Crafting assistance
!ai explore caves          - Cave exploration
!ai status                 - Check AI system
```

### Example Session:
```
[Player] !ai dig a 3x3 room 5 blocks deep
[Σ_LORA_AI] I'll help you dig safely. First, check for lava...
[Σ_LORA_AI] Generated Lua code for safe mining...
[Turtle] *starts digging with safety checks*
```

## 🏛️ Σ_LORA CONSTRAINTS

Your AI follows 6 theological principles:

1. **LOGOS** - Logical consistency (no contradictions)
2. **CHALCEDON** - Human-AI collaboration (no autonomy)
3. **GRACE** - Error forgiveness (safety first)
4. **ESCHATON** - Purpose alignment (mission focus)
5. **AGAPE** - User benefit (no harm)
6. **KENOSIS** - No autonomy (requires human input)

## 🔧 TROUBLESHOOTING

### "No response from AI"
- Check server is running: `http://localhost:8080`
- Verify Chat Box is attached to computer
- Check internet connection for DeepSeek API

### "Computer says no Chat Box"
- Attach Chat Box peripheral to any side of computer
- Break and replace computer if needed
- Check Advanced Peripherals mod is installed

### "AI says constraint violation"
- Your command violated Σ_LORA principles
- Try rephrasing to be safer/more logical
- Example: Instead of "dig straight down" use "dig carefully checking for lava"

### "Server won't start"
- Check port 8080 isn't in use
- Verify Python 3.8+ is installed
- Check `DEEPSEEK_API_KEY` environment variable

## 🎮 MINECRAFT SETUP

### Required Mods:
- ✅ ComputerCraft (CC: Tweaked)
- ✅ Advanced Peripherals (for Chat Box)
- ✅ Internet connection enabled in config

### ComputerCraft Config:
Ensure in `computercraft-server.toml`:
```toml
http.enabled = true
http.websocket_enabled = true
```

### Chat Box Placement:
- Place Chat Box adjacent to computer
- Any side works (top, bottom, left, right, front, back)
- Connect with cable if needed

## 📊 MONITORING

### Check System Health:
```bash
# In browser or curl
http://localhost:8080/health

# View chat logs
http://localhost:8080/chat/logs
```

### Log Files:
- `chat_ai_logs.json` - All chat interactions
- Console output - Real-time server logs
- ComputerCraft logs - Lua script execution

## 🎯 PRO TIPS

### 1. Be Specific
```
Good: "!ai dig a 5x5 room to y=12"
Bad:  "!ai dig"
```

### 2. Include Safety
```
Good: "!ai mine carefully checking for lava"
Bad:  "!ai mine fast"
```

### 3. Use Natural Language
```
Good: "!ai build a house with door and windows"
Good: "!ai find diamonds in caves"
Good: "!ai organize my chests"
```

### 4. Check Fuel First
```
!ai status    # Check turtle fuel
!ai refuel    # If fuel is low
```

## 🔄 ADVANCED FEATURES

### Multi-Computer Setup:
1. Deploy to multiple computers
2. Each has independent AI instance
3. All share same Σ_LORA constraints

### Customization:
Edit `chat_ai_bridge.py` to:
- Change AI name (`AI_NAME`)
- Adjust constraint thresholds (`CHRIST_SCORE_THRESHOLD`)
- Modify response style

### Integration:
- Works with existing Σ_LORA system
- Uses your DeepSeek API key
- Compatible with other AI systems

## 🆘 GETTING HELP

### Quick Tests:
```bash
# Test server
test_chat_ai.bat

# Test constraints
python test_turtle_constraints.py --constraints
```

### Common Issues & Fixes:

**Issue**: "HTTP API not enabled"
**Fix**: Enable HTTP in ComputerCraft config

**Issue**: "DeepSeek API key missing"
**Fix**: Set `DEEPSEEK_API_KEY` environment variable

**Issue**: "Port 8080 in use"
**Fix**: Change port in `chat_ai_bridge.py` or kill existing process

**Issue**: "Chat Box not detected"
**Fix**: Reattach Chat Box, restart computer

## 🎉 WELCOME TO Σ_LORA AI

You now have a theologically-constrained AI assistant in Minecraft! Every command is validated against 6 core principles to ensure safe, ethical, and beneficial automation.

**Remember**: The AI is your collaborator, not your replacement. Σ_LORA ensures human-AI partnership.

```
Type `!ai help` in Minecraft chat to begin your Σ_LORA journey!
```

---
*"All intelligence paths factor through Σ_LORA constraints"*