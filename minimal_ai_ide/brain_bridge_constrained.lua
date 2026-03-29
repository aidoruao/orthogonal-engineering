-- brain_bridge_constrained.lua
-- Σ_LORA Constrained Turtle Brain Bridge for ComputerCraft
-- Connects to Python constraint server for Σ_LORA theological constraint validation
-- Place this file in your ComputerCraft computer/turtle as "brain.lua"

-- ==================== CONFIGURATION ====================

local CONSTRAINT_SERVER_URL = "http://localhost:8000/turtle/command"
local FALLBACK_DIRECT_API = false  -- If true, fall back to direct DeepSeek API if server fails
local API_KEY = os.getenv("DEEPSEEK_API_KEY") or "[API_KEY_REDACTED]"  -- Only used if fallback is needed
local API_URL = "https://api.deepseek.com/v1/chat/completions"

-- ==================== LOGGING SYSTEM ====================

local function log(message, level)
    local timestamp = os.time()
    local timeStr = os.date("%H:%M:%S", timestamp)
    local levelStr = level or "INFO"

    local logMessage = string.format("[%s] [%s] %s", timeStr, levelStr, message)
    print(logMessage)

    -- Also write to log file if possible
    local logFile = "/brain_bridge.log"
    local file = fs.open(logFile, "a")
    if file then
        file.writeLine(logMessage)
        file.close()
    end
end

local function logError(message)
    log(message, "ERROR")
end

local function logWarning(message)
    log(message, "WARNING")
end

local function logInfo(message)
    log(message, "INFO")
end

local function logDebug(message)
    log(message, "DEBUG")
end

-- ==================== TURTLE POSITION TRACKER ====================
-- Maintains {x, y, z, facing} dead-reckoning state and reads sign invariants
-- via turtle.inspect(). Position data is included in every constraint-server
-- request so the server can perform spatial (not just lexical) validation.
--
-- Facing encoding: 0=north, 1=east, 2=south, 3=west (CC:Tweaked convention)
-- Signs are read on inspect() calls; the sign text is forwarded to the server
-- as part of the command context so invariant anchors can be checked.

local TurtlePositionTracker = {}
TurtlePositionTracker.__index = TurtlePositionTracker

function TurtlePositionTracker.new(startX, startY, startZ, startFacing)
    local self = setmetatable({}, TurtlePositionTracker)
    self.x = startX or 0
    self.y = startY or 0
    self.z = startZ or 0
    -- facing: 0=north, 1=east, 2=south, 3=west
    self.facing = startFacing or 0
    self.sign_cache = {}  -- last sign texts read via turtle.inspect()
    return self
end

-- Cardinal direction deltas: north(0), east(1), south(2), west(3)
local FACING_DX = {[0]=0,  [1]=1, [2]=0,  [3]=-1}
local FACING_DZ = {[0]=-1, [1]=0, [2]=1,  [3]=0}

function TurtlePositionTracker:moveForward()
    self.x = self.x + FACING_DX[self.facing]
    self.z = self.z + FACING_DZ[self.facing]
    logDebug(string.format("Position: (%d, %d, %d) facing=%d", self.x, self.y, self.z, self.facing))
end

function TurtlePositionTracker:moveBack()
    self.x = self.x - FACING_DX[self.facing]
    self.z = self.z - FACING_DZ[self.facing]
    logDebug(string.format("Position: (%d, %d, %d) facing=%d", self.x, self.y, self.z, self.facing))
end

function TurtlePositionTracker:moveUp()
    self.y = self.y + 1
    logDebug(string.format("Position: (%d, %d, %d) facing=%d", self.x, self.y, self.z, self.facing))
end

function TurtlePositionTracker:moveDown()
    self.y = self.y - 1
    logDebug(string.format("Position: (%d, %d, %d) facing=%d", self.x, self.y, self.z, self.facing))
end

function TurtlePositionTracker:turnLeft()
    -- Use (facing + 3) % 4 for portable subtraction (avoids negative modulo ambiguity)
    self.facing = (self.facing + 3) % 4
    logDebug(string.format("Position: (%d, %d, %d) facing=%d", self.x, self.y, self.z, self.facing))
end

function TurtlePositionTracker:turnRight()
    self.facing = (self.facing + 1) % 4
    logDebug(string.format("Position: (%d, %d, %d) facing=%d", self.x, self.y, self.z, self.facing))
end

function TurtlePositionTracker:getPosition()
    return {x = self.x, y = self.y, z = self.z, facing = self.facing}
end

--- Read sign text from the block directly in front of the turtle using
--- turtle.inspect(). Parses MC 1.20+ double-sided sign format:
---   data.state.front_text.messages / data.state.back_text.messages
--- Returns a table {front={...}, back={...}} or nil if no sign is found.
function TurtlePositionTracker:inspectSign()
    if not turtle then return nil end
    local success, data = turtle.inspect()
    if not success or not data then return nil end
    if not (data.name and data.name:find("sign")) then return nil end

    local state = data.state or {}
    local front_raw = (state.front_text or {}).messages or {}
    local back_raw  = (state.back_text  or {}).messages or {}

    local function parseMessages(msgs)
        local lines = {}
        for _, msg in ipairs(msgs) do
            if type(msg) == "string" then
                -- JSON-encoded message: {"text":"LINE"} or {"text":"Line with \"quotes\""}
                -- Strip outer braces then extract the "text" value, handling escaped quotes.
                local inner = msg:match("^%s*{(.+)}%s*$")
                local text
                if inner then
                    -- Match "text":"..." accounting for backslash-escaped chars
                    text = inner:match('"text"%s*:%s*"((?:[^"\\]|\\.)*)"')
                    if not text then
                        -- Fallback: capture up to first unescaped quote
                        text = inner:match('"text"%s*:%s*"([^"]*)"')
                    end
                end
                table.insert(lines, text or msg)
            elseif type(msg) == "table" then
                table.insert(lines, msg.text or "")
            end
        end
        return lines
    end

    local sign = {
        front = parseMessages(front_raw),
        back  = parseMessages(back_raw),
        block = data.name,
    }
    self.sign_cache[#self.sign_cache + 1] = sign
    logInfo("Sign read: front=" .. table.concat(sign.front, "|") ..
            " back=" .. table.concat(sign.back, "|"))
    return sign
end

--- Return a context table with current position and any sign data.
--- This is merged into the constraint-server payload so the server can
--- perform spatial (not just lexical) constraint checking.
function TurtlePositionTracker:buildContext()
    local ctx = {
        position = self:getPosition(),
        sign_cache = self.sign_cache,
    }
    return ctx
end

-- Module-level position tracker instance (initialised lazily)
local _posTracker = nil

local function getPositionTracker()
    if not _posTracker then
        _posTracker = TurtlePositionTracker.new(0, 0, 0, 0)
        logInfo("TurtlePositionTracker initialised at (0,0,0) facing north")
    end
    return _posTracker
end

-- ==================== CONSTRAINT SERVER COMMUNICATION ====================

local function callConstraintServer(command, turtleId, context)
    logInfo("Calling Σ_LORA constraint server...")

    -- Merge position and sign data into context for spatial constraint checking
    local posTracker = getPositionTracker()
    local spatialCtx = posTracker:buildContext()
    context = context or {}
    for k, v in pairs(spatialCtx) do
        context[k] = v
    end
    -- Also inspect the block in front before sending (reads sign invariants)
    local sign = posTracker:inspectSign()
    if sign then
        context.sign_in_front = sign
    end

    -- Prepare request payload
    local payload = {
        command = command,
        turtle_id = turtleId or "unknown",
        context = context,
        require_confirmation = true
    }

    -- Add turtle-specific context if available
    if turtle then
        payload.context = payload.context or {}
        payload.context.fuel_level = turtle.getFuelLevel()
        payload.context.fuel_limit = turtle.getFuelLimit()
        payload.context.is_turtle = true

        -- Get inventory summary
        local inventory = {}
        for slot = 1, 16 do
            local item = turtle.getItemDetail(slot)
            if item then
                inventory[slot] = {
                    name = item.name,
                    count = item.count
                }
            end
        end
        payload.context.inventory = inventory
    end

    local requestBody = textutils.serializeJSON(payload)
    local headers = {
        ["Content-Type"] = "application/json"
    }

    logDebug("Request payload: " .. requestBody)

    -- Make HTTP request
    local response = http.post(CONSTRAINT_SERVER_URL, requestBody, headers)

    if not response then
        logError("Constraint server connection failed")
        return nil, "Constraint server unreachable"
    end

    local responseText = response.readAll()
    response.close()

    logDebug("Server response: " .. responseText)

    -- Parse response
    local success, data = pcall(textutils.unserializeJSON, responseText)

    if not success then
        logError("Failed to parse server response: " .. responseText)
        return nil, "Invalid server response"
    end

    if data.error then
        logError("Server error: " .. data.error)
        return nil, data.error
    end

    if not data.success then
        local errorMsg = data.error or "Constraint validation failed"
        if data.constraints then
            -- Log which constraints failed
            local failedConstraints = {}
            for constraint, satisfied in pairs(data.constraints) do
                if not satisfied then
                    table.insert(failedConstraints, constraint)
                end
            end
            if #failedConstraints > 0 then
                errorMsg = errorMsg .. " (Failed: " .. table.concat(failedConstraints, ", ") .. ")"
            end
        end
        logError("Constraint validation failed: " .. errorMsg)
        return nil, errorMsg
    end

    if not data.lua_code then
        logError("Server returned success but no Lua code")
        return nil, "No Lua code generated"
    end

    logInfo(string.format("Σ_LORA validation passed! Christ score: %.2f", data.christ_score or 0))

    -- Log constraint results
    if data.constraints then
        local constraintResults = {}
        for constraint, satisfied in pairs(data.constraints) do
            table.insert(constraintResults, constraint .. ": " .. (satisfied and "✓" or "✗"))
        end
        logInfo("Constraint results: " .. table.concat(constraintResults, ", "))
    end

    return data.lua_code, nil
end

-- ==================== FALLBACK DIRECT API ====================

local function callDirectDeepSeekAPI(taskDescription)
    logWarning("Using fallback direct DeepSeek API (no Σ_LORA constraints)")

    local messages = {
        {
            role = "system",
            content = "You are a Minecraft ComputerCraft Turtle programming expert. You MUST output ONLY raw Lua code that can run directly in ComputerCraft. No explanations, no markdown, no code blocks, no comments unless absolutely necessary. The code should be complete and executable."
        },
        {
            role = "user",
            content = "Write ComputerCraft Lua code to: " .. taskDescription .. "\n\nIMPORTANT: Output ONLY the Lua code, nothing else. The code will be executed immediately."
        }
    }

    local requestBody = textutils.serializeJSON({
        model = "deepseek-chat",
        messages = messages,
        temperature = 0.7,
        max_tokens = 1000
    })

    local headers = {
        ["Authorization"] = "Bearer " .. API_KEY,
        ["Content-Type"] = "application/json"
    }

    local response = http.post(API_URL, requestBody, headers)

    if not response then
        return nil, "Failed to connect to DeepSeek API"
    end

    local responseText = response.readAll()
    response.close()

    local success, data = pcall(textutils.unserializeJSON, responseText)

    if not success then
        return nil, "Failed to parse API response"
    end

    if data.error then
        return nil, "API Error: " .. (data.error.message or "Unknown error")
    end

    if not data.choices or #data.choices == 0 then
        return nil, "No response from AI"
    end

    local aiCode = data.choices[1].message.content

    -- Clean up the response
    aiCode = aiCode:gsub("```lua", ""):gsub("```", ""):trim()

    return aiCode
end

-- ==================== FUEL MANAGEMENT ====================

local function checkFuel()
    if not turtle then
        return true  -- Not a turtle, no fuel check needed
    end

    local fuelLevel = turtle.getFuelLevel()
    local fuelLimit = turtle.getFuelLimit()

    logDebug(string.format("Fuel level: %d/%d", fuelLevel, fuelLimit))

    if fuelLevel < 100 then
        logWarning("Low fuel! Level: " .. fuelLevel)
        logWarning("Place coal in slot 1 and run: brain refuel")
        return false
    end

    return true
end

local function autoRefuel()
    if not turtle then
        logWarning("Not a turtle - no fuel system")
        return false
    end

    local fuelLevel = turtle.getFuelLevel()
    if fuelLevel > 1000 then
        logDebug("Fuel sufficient: " .. fuelLevel)
        return true
    end

    logInfo("Attempting to auto-refuel...")

    -- Check slot 1 for fuel
    turtle.select(1)
    local itemDetail = turtle.getItemDetail()

    if itemDetail then
        local fuelItems = {
            ["minecraft:coal"] = true,
            ["minecraft:coal_block"] = true,
            ["minecraft:charcoal"] = true,
            ["minecraft:lava_bucket"] = true,
        }

        if fuelItems[itemDetail.name] then
            turtle.refuel(1)
            logInfo("Refueled using " .. itemDetail.name)
            return true
        end
    end

    -- Search inventory for fuel
    for slot = 1, 16 do
        turtle.select(slot)
        local detail = turtle.getItemDetail()
        if detail then
            local fuelItems = {
                ["minecraft:coal"] = true,
                ["minecraft:coal_block"] = true,
                ["minecraft:charcoal"] = true,
                ["minecraft:lava_bucket"] = true,
            }

            if fuelItems[detail.name] then
                turtle.refuel(1)
                logInfo("Refueled using " .. detail.name .. " from slot " .. slot)
                turtle.select(1)  -- Return to slot 1
                return true
            end
        end
    end

    logError("No fuel found! Place coal in inventory.")
    return false
end

-- ==================== CODE EXECUTION ====================

local function executeLuaCode(code, taskDescription)
    logInfo("Executing AI plan for: " .. taskDescription)

    -- Create a temporary file with the AI code
    local tempFile = "/temp_constrained_code.lua"
    local file = fs.open(tempFile, "w")
    if not file then
        error("Cannot create temporary file")
    end

    -- Add safety wrapper and logging
    local safeCode = [[
-- Σ_LORA Constrained AI-Generated Code for: ]] .. taskDescription .. [[

local function logExec(message)
    print("[EXEC] " .. message)
end

logExec("Starting Σ_LORA constrained execution...")

-- Safety wrapper
local function safeExecute()
]] .. code .. [[
end

-- Run with error handling
local success, err = pcall(safeExecute)
if not success then
    logExec("Error executing AI code: " .. err)
    return false
end

logExec("Σ_LORA constrained execution completed successfully")
return true
]]

    file.write(safeCode)
    file.close()

    -- Execute the code
    logInfo("Running Σ_LORA validated code...")
    local result = shell.run(tempFile)

    -- Clean up
    fs.delete(tempFile)

    return result
end

-- ==================== MAIN BRAIN FUNCTION ====================

local function brain(taskDescription, turtleId)
    if not taskDescription or taskDescription == "" then
        print("Usage: brain <task>")
        print("Examples:")
        print("  brain \"dig a 3x3 room\"")
        print("  brain \"mine straight down to y=12\"")
        print("  brain \"find diamonds\"")
        print("  brain \"build a house\"")
        print("  brain \"refuel\"")
        print("  brain \"status\"")
        return
    end

    -- Special command: refuel
    if taskDescription:lower() == "refuel" then
        if turtle then
            autoRefuel()
        else
            print("Not a turtle - no fuel system")
        end
        return
    end

    -- Special command: status
    if taskDescription:lower() == "status" then
        print("=== Σ_LORA Constrained Brain Bridge Status ===")
        print("Constraint Server: " .. CONSTRAINT_SERVER_URL)
        print("Fallback API: " .. (FALLBACK_DIRECT_API and "Enabled" or "Disabled"))

        -- Show current dead-reckoning position
        local pos = getPositionTracker():getPosition()
        local facingNames = {[0]="north", [1]="east", [2]="south", [3]="west"}
        print(string.format("Position (dead-reckoning): x=%d y=%d z=%d facing=%s",
            pos.x, pos.y, pos.z, facingNames[pos.facing] or tostring(pos.facing)))

        if turtle then
            local fuel = turtle.getFuelLevel()
            local limit = turtle.getFuelLimit()
            print(string.format("Fuel: %d/%d (%.1f%%)", fuel, limit, (fuel/limit)*100))

            -- Inventory summary
            local itemCount = 0
            for slot = 1, 16 do
                if turtle.getItemDetail(slot) then
                    itemCount = itemCount + 1
                end
            end
            print("Occupied slots: " .. itemCount .. "/16")
        else
            print("Device: Computer (not a turtle)")
        end
        print("==========================================")
        return
    end

    -- Check fuel before starting any task
    if not checkFuel() then
        print("ERROR: Please refuel first!")
        print("Run: brain refuel")
        return
    end

    -- Get turtle ID (use computer ID if not specified)
    local id = turtleId or tostring(os.getComputerID())

    -- Try constraint server first
    local luaCode, errorMsg = callConstraintServer(taskDescription, id)

    -- If constraint server fails and fallback is enabled, try direct API
    if not luaCode and FALLBACK_DIRECT_API then
        logWarning("Constraint server failed, trying direct API...")
        luaCode, errorMsg = callDirectDeepSeekAPI(taskDescription)
    end

    if not luaCode then
        print("Failed to get AI help: " .. (errorMsg or "Unknown error"))
        return
    end

    print("\n" .. string.rep("=", 60))
    print("Σ_LORA VALIDATED CODE GENERATED")
    print(string.rep("=", 60))
    print(luaCode)
    print(string.rep("=", 60) .. "\n")

    -- Ask for confirmation (respects require_confirmation from server)
    print("Execute this Σ_LORA validated code? (y/n)")
    local response = read()

    if response:lower() == "y" then
        executeLuaCode(luaCode, taskDescription)
    else
        print("Code execution cancelled.")
        print("You can copy the code above and run it manually.")
    end
end

-- ==================== STARTUP AND COMMAND LINE ====================

-- Function to test server connection
local function testServerConnection()
    logInfo("Testing constraint server connection...")

    local response = http.get(CONSTRAINT_SERVER_URL)
    if response then
        local data = response.readAll()
        response.close()

        local success, parsed = pcall(textutils.unserializeJSON, data)
        if success and parsed.status == "online" then
            logInfo("Constraint server is online: " .. parsed.service)
            return true
        end
    end

    logError("Constraint server is offline or unreachable")
    return false
end

-- Main entry point
local function main()
    print("\n" .. string.rep("=", 60))
    print("Σ_LORA CONSTRAINED TURTLE BRAIN BRIDGE")
    print(string.rep("=", 60))
    print("Theological Constraint System: LOGOS, CHALCEDON, GRACE,")
    print("ESCHATON, AGAPE, KENOSIS")
    print(string.rep("=", 60))

    -- Test server connection
    if not testServerConnection() then
        if FALLBACK_DIRECT_API then
            print("WARNING: Using fallback mode (no Σ_LORA constraints)")
        else
            print("ERROR: Constraint server required but unavailable")
            print("Start the Python server: python turtle_constraint_server.py")
            return
        end
    end

    print("Type 'exit' to quit")
    print("Type 'refuel' to auto-refuel")
    print("Type 'status' for system status")
    print(string.rep("=", 60) .. "\n")

    while true do
        write("brain> ")
        local input = read()

        if not input or input:lower() == "exit" then
            break
        end

        brain(input)
        print()  -- Blank line for readability
    end
end

-- If run directly from command line
local args = {...}
if #args > 0 then
    brain(table.concat(args, " "))
else
    -- Interactive mode
    main()
end
