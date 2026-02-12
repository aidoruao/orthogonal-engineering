-- SUPER SIMPLE AI TEST SCRIPT
-- This will test if everything is working

print("========================================")
print("Σ_LORA AI SIMPLE TEST")
print("========================================")

-- Check if HTTP is enabled
if not http then
    print("ERROR: HTTP API not enabled!")
    print("Enable it in ComputerCraft config:")
    print("  config/computercraft.toml")
    print("  http.enabled = true")
    print("========================================")
    return
end

print("✓ HTTP API is enabled")

-- Test connection to AI server
print("Testing connection to AI server...")
local response = http.get("http://localhost:8080/")

if not response then
    print("✗ Cannot connect to AI server!")
    print("Make sure Python server is running:")
    print("  python chat_ai_bridge.py")
    print("========================================")
    return
end

local data = response.readAll()
response.close()

print("✓ Connected to AI server!")
print("Server response: " .. string.sub(data, 1, 100) .. "...")

-- Check if Chat Box is attached
print("\nChecking for Chat Box...")
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
    print("Attach Chat Box to any side of computer")
    print("(Advanced Peripherals mod required)")
end

print("\n========================================")
print("TEST COMPLETE")
print("========================================")
print("NEXT STEPS:")
print("1. Make sure Python server is running")
print("2. Attach Chat Box to computer")
print("3. In Minecraft chat, type: !ai help")
print("========================================")
