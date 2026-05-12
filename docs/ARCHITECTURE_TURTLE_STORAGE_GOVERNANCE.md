# Turtle Storage Governance — Architectural Specification

## Phase 1: Inventory Awareness

### What The Turtle Learns
- Query every slot in its 16-slot inventory
- Report item name, count, and damage value per slot
- Report empty slots and total free space
- Report fuel level and maximum fuel capacity

### Code Required (Lua)
```lua
function scanInventory()
    local report = {}
    for slot = 1, 16 do
        local count = turtle.getItemCount(slot)
        if count > 0 then
            local detail = turtle.getItemDetail(slot)
            report[slot] = {
                name = detail.name,
                count = count,
                damage = detail.damage or 0,
                maxDamage = detail.maxDamage or 0
            }
        else
            report[slot] = { empty = true }
        end
    end
    return report
end
Expected Output
text
{
  [1] = { name = "minecraft:iron_ore", count = 12 },
  [2] = { name = "minecraft:coal", count = 5 },
  [3] = { empty = true },
  ...
}
Phase 2: External Storage Connection
What The Turtle Learns
turtle.activate() on a chest to connect

turtle.suck() to pull items from chest into turtle

turtle.drop() to push items from turtle into chest

Distinguish between input chest (raw materials) and output chest (finished goods)

Code Required (Lua)
lua
function depositToStorage(storageSlot, itemName)
    -- Move specific item to a chest's specific slot
    for slot = 1, 16 do
        local detail = turtle.getItemDetail(slot)
        if detail and detail.name == itemName then
            turtle.select(slot)
            turtle.drop()
            return true
        end
    end
    return false
end

function withdrawFromStorage(itemName, count)
    -- Pull specific item from chest into turtle
    turtle.activate() -- open chest
    local pulled = 0
    while pulled < count do
        turtle.suck()
        pulled = pulled + 1
    end
    return true
end
Phase 3: Sorting Logic
Invariants
Ores → Smelting Chest

Ingots/Gems → Crafting Chest

Building Blocks → Construction Chest

Food → Kitchen Chest

Tools/Weapons → Armory Chest

Redstone/Components → Engineering Chest

Code Required (Lua)
lua
SORTING_RULES = {
    ["minecraft:iron_ore"] = "smelting",
    ["minecraft:gold_ore"] = "smelting",
    ["minecraft:coal"] = "fuel",
    ["minecraft:iron_ingot"] = "crafting",
    ["minecraft:gold_ingot"] = "crafting",
    ["minecraft:diamond"] = "crafting",
    ["minecraft:cobblestone"] = "building",
    ["minecraft:dirt"] = "building",
    ["minecraft:oak_log"] = "building",
    -- Add all modded items here
}

function sortItem(itemName)
    local category = SORTING_RULES[itemName] or "misc"
    return category
end
Phase 4: Threshold Management
Invariants
If crafting_chest.iron_ingot < 10 → Mine iron

If fuel_chest.coal < 5 → Mine coal

If food_chest.bread < 3 → Harvest/craft food

If inventory is full → Return to storage and deposit all

Code Required (Lua)
lua
THRESHOLDS = {
    ["minecraft:iron_ingot"] = 10,
    ["minecraft:coal"] = 5,
    ["minecraft:bread"] = 3,
}

function needsRestock(itemName, currentCount)
    local threshold = THRESHOLDS[itemName] or 0
    return currentCount < threshold
end
Phase 5: Merkle-Anchored Inventory State
Invariants
Every deposit generates a ProofObject: {item, count, destination_chest, hash_before, hash_after}

Every withdrawal generates a ProofObject: {item, count, source_chest, hash_before, hash_after}

Christ Score reflects inventory accuracy

Code Required (Lua → Yeshua bridge)
lua
function logTransfer(action, item, count, chest)
    local entry = {
        action = action,   -- "deposit" or "withdraw"
        item = item,
        count = count,
        chest = chest,
        timestamp = os.time()
    }
    -- Send to Yeshua via HTTP
    http.post("http://localhost:8000/log", textutils.serializeJSON(entry))
end
Implementation Sequence
Phase	Deliverable	Test In-Game
1	scanInventory() function	lua> scanInventory() prints all slots
2	depositToStorage() and withdrawFromStorage()	Place chest, run deposit, verify items moved
3	sortItem() with full SORTING_RULES table	Run scan, sort all items, verify categories
4	needsRestock() with THRESHOLDS table	Simulate low stock, verify restock trigger
5	logTransfer() with Yeshua HTTP bridge	Run transfer, check Yeshua log for entry
External Development Workflow
Write Lua scripts in Ubuntu: /home/idor/oe-local/automation/computer_craft/storage/

Copy to turtle directory: cp *.lua /mnt/c/Users/Aidor/.../computercraft/computer/1/

In-game: lua> scanInventory() or run the script by name

Iterate: edit outside, copy, test in-game
