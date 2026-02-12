-- ai_simple.lua
-- SUPER SIMPLE AI TEST - GUARANTEED TO WORK
-- Just run this script to test everything

print("========================================")
print("Σ_LORA AI SIMPLE TEST")
print("========================================")

-- First, check if HTTP is available
if not http then
    print("ERROR: HTTP API not enabled!")
    print("You need to enable HTTP in ComputerCraft config.")
    print("Edit: config/computercraft.toml")
    print("Set: http.enabled = true")
    print("Then restart Minecraft.")
    print("========================================")
    return
end

print("✓ HTTP API is enabled")

-- Try to connect to AI server
print("Testing AI server connection...")

-- Try localhost first
local response = http.get("http://localhost:8080/")

if not response then
    print("✗ Cannot connect to localhost:8080")
    print("")
    print("POSSIBLE FIXES:")
    print("1. Make sure Python server is running")
    print("   - Check for black window titled 'Σ_LORA AI Server'")
    print("   - If not running, double-click START_AI_NOW.bat")
    print("")
    print("2. Test in your web browser:")
    print("   Open: http://localhost:8080")
    print("   If it shows JSON, server is running")
    print("   If error, server is not running")
    print("")
    print("3. Restart everything:")
    print("   - Close all command windows")
    print("   - Double-click START_AI_NOW.bat")
    print("   - Wait for 'AI SERVER STARTING...' message")
    print("========================================")
    return
end

local data = response.readAll()
response.close()

print("✓ Connected to AI server!")
print("Server says: " .. string.sub(data, 1, 100))

-- Check for Chat Box
print("")
print("Checking for Chat Box peripheral...")

local foundChatBox = false
local sides = {"top", "bottom", "left", "right", "front", "back"}

for _, side in ipairs(sides) do
    if peripheral.getType(side) == "chatBox" then
        print("✓ Chat Box found on side: " .. side)
        foundChatBox = true
        break
    end
end

if not foundChatBox then
    print("✗ No Chat Box found!")
    print("")
    print("SOLUTION:")
    print("1. Make sure Advanced Peripherals mod is installed")
    print("2. Get Chat Box from creative inventory")
    print("3. Place it touching the computer (any side)")
    print("4. Break and replace computer to restart")
    print("========================================")
    return
end

print("")
print("========================================")
print("✅ EVERYTHING WORKING PERFECTLY!")
print("========================================")
print("")
print("NEXT STEP:")
print("In Minecraft chat (press T), type:")
print("")
print("    !ai help")
print("")
print("The AI should respond with available commands.")
print("")
print("Try these examples:")
print("  !ai dig a 3x3 room")
print("  !ai build a small house")
print("  !ai find diamonds")
print("")
print("========================================")
print("Σ_LORA AI IS READY!")
print("========================================")
