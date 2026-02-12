-- FIXED AI TEST SCRIPT
-- Tries multiple server addresses to find the AI server

print("========================================")
print("Σ_LORA AI CONNECTION FIX TEST")
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

-- List of possible server addresses to try
local serverAddresses = {
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://0.0.0.0:8080",
    "http://192.168.1.100:8080",  -- Common home network IP
    "http://10.0.0.100:8080"      -- Another common home network IP
}

print("\nTesting server connections...")

local connected = false
local successfulAddress = ""

-- Try each address
for _, address in ipairs(serverAddresses) do
    print("Trying: " .. address)

    local response = http.get(address)

    if response then
        local data = response.readAll()
        response.close()

        -- Check if it's our AI server
        if string.find(data, "Σ_LORA") or string.find(data, "status") then
            print("✓ CONNECTED to: " .. address)
            print("Response: " .. string.sub(data, 1, 100) .. "...")
            connected = true
            successfulAddress = address
            break
        else
            print("  ✗ Wrong server response")
            response.close()
        end
    else
        print("  ✗ No response")
    end

    -- Small delay between attempts
    sleep(0.5)
end

if not connected then
    print("\n✗ COULD NOT CONNECT TO ANY SERVER!")
    print("\nTROUBLESHOOTING:")
    print("1. Make sure Python server is running:")
    print("   python chat_ai_bridge.py")
    print("2. Check if port 8080 is blocked by firewall")
    print("3. Try running server on different port:")
    print("   Edit chat_ai_bridge.py line: PORT = 8081")
    print("4. Check if Minecraft and server are on same PC")
    print("\nTo test manually in browser:")
    print("   Open: http://localhost:8080")
else
    print("\n✓ SUCCESS! Server found at: " .. successfulAddress)

    -- Update the chat_ai.lua file with correct address
    print("\nUpdating chat_ai.lua with correct address...")

    local chatAIFile = fs.open("chat_ai.lua", "r")
    if chatAIFile then
        local content = chatAIFile.readAll()
        chatAIFile.close()

        -- Replace the server URL
        local newContent = string.gsub(content,
            'local AI_SERVER_URL = "http://localhost:8080/chat/message"',
            'local AI_SERVER_URL = "' .. successfulAddress .. '/chat/message"')

        local writeFile = fs.open("chat_ai.lua", "w")
        if writeFile then
            writeFile.write(newContent)
            writeFile.close()
            print("✓ chat_ai.lua updated with: " .. successfulAddress)
        else
            print("✗ Could not update chat_ai.lua")
        end
    else
        print("✗ chat_ai.lua not found")
    end

    -- Check for Chat Box
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
    else
        print("\n✓ EVERYTHING READY!")
        print("In Minecraft chat, type: !ai help")
    end
end

print("\n========================================")
print("TEST COMPLETE")
print("========================================")
