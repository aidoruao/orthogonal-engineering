-- ============================================================
-- inventory.lua — Turtle Storage Governance Phase 1
-- Inventory Awareness: scan, classify, report
-- Part of CC-Tweaked-oe turtle storage governance system
-- Verified by 10-AI industry consensus (2026-05-12)
-- ============================================================

local INVENTORY = {}

-- ============================================================
-- Configuration
-- ============================================================
local CONFIG = {
    SLOTS = 16,            -- Turtle inventory slots
    FUEL_WARNING = 100,    -- Warn if fuel below this
    FUEL_CRITICAL = 10,    -- Halt if fuel below this
}

-- ============================================================
-- Slot-level queries
-- ============================================================

--- Scan a single slot and return item details.
--- @param slot number 1-16
--- @return table|nil {name, count, damage, maxDamage} or nil if empty
function INVENTORY.scanSlot(slot)
    local count = turtle.getItemCount(slot)
    if count == 0 then
        return nil
    end
    local detail = turtle.getItemDetail(slot)
    if not detail then
        return nil
    end
    return {
        slot = slot,
        name = detail.name,
        count = count,
        damage = detail.damage or 0,
        maxDamage = detail.maxDamage or 0,
    }
end

-- ============================================================
-- Full inventory scan
-- ============================================================

--- Scan all 16 slots and return a complete inventory report.
--- @return table {slots = {}, totalItems = number, freeSlots = number, fuel = number}
function INVENTORY.scanAll()
    local report = {
        slots = {},
        totalItems = 0,
        freeSlots = 0,
        fuel = turtle.getFuelLevel(),
        maxFuel = turtle.getFuelLimit(),
    }

    for slot = 1, CONFIG.SLOTS do
        local item = INVENTORY.scanSlot(slot)
        if item then
            report.slots[slot] = item
            report.totalItems = report.totalItems + item.count
        else
            report.slots[slot] = { empty = true }
            report.freeSlots = report.freeSlots + 1
        end
    end

    return report
end

-- ============================================================
-- Category classification
-- ============================================================

-- Sorting rules: map item names to storage categories.
-- Extended by the 5-phase governance specification.
INVENTORY.SORTING_RULES = {
    -- Raw ores → smelting
    ["minecraft:iron_ore"] = "smelting",
    ["minecraft:gold_ore"] = "smelting",
    ["minecraft:copper_ore"] = "smelting",
    ["minecraft:ancient_debris"] = "smelting",

    -- Fuel → fuel storage
    ["minecraft:coal"] = "fuel",
    ["minecraft:charcoal"] = "fuel",
    ["minecraft:coal_block"] = "fuel",

    -- Ingots and gems → crafting
    ["minecraft:iron_ingot"] = "crafting",
    ["minecraft:gold_ingot"] = "crafting",
    ["minecraft:copper_ingot"] = "crafting",
    ["minecraft:netherite_ingot"] = "crafting",
    ["minecraft:diamond"] = "crafting",
    ["minecraft:emerald"] = "crafting",

    -- Building blocks → construction
    ["minecraft:cobblestone"] = "building",
    ["minecraft:stone"] = "building",
    ["minecraft:dirt"] = "building",
    ["minecraft:gravel"] = "building",
    ["minecraft:sand"] = "building",
    ["minecraft:oak_log"] = "building",
    ["minecraft:oak_planks"] = "building",

    -- Food → kitchen
    ["minecraft:bread"] = "food",
    ["minecraft:wheat"] = "food",
    ["minecraft:apple"] = "food",
    ["minecraft:cooked_beef"] = "food",
    ["minecraft:cooked_porkchop"] = "food",

    -- Tools and weapons → armory
    ["minecraft:iron_pickaxe"] = "armory",
    ["minecraft:iron_sword"] = "armory",
    ["minecraft:iron_axe"] = "armory",
    ["minecraft:iron_shovel"] = "armory",
    ["minecraft:bow"] = "armory",
    ["minecraft:shield"] = "armory",

    -- Redstone and components → engineering
    ["minecraft:redstone"] = "engineering",
    ["minecraft:redstone_torch"] = "engineering",
    ["minecraft:repeater"] = "engineering",
    ["minecraft:comparator"] = "engineering",
    ["minecraft:piston"] = "engineering",
    ["minecraft:sticky_piston"] = "engineering",
    ["minecraft:observer"] = "engineering",
    ["minecraft:dispenser"] = "engineering",
}

--- Classify an item by name into a storage category.
--- @param itemName string
--- @return string category name
function INVENTORY.classify(itemName)
    return INVENTORY.SORTING_RULES[itemName] or "misc"
end

-- ============================================================
-- Threshold management
-- ============================================================

INVENTORY.THRESHOLDS = {
    ["minecraft:iron_ingot"] = 10,
    ["minecraft:coal"] = 5,
    ["minecraft:bread"] = 3,
    ["minecraft:oak_log"] = 16,
    ["minecraft:redstone"] = 10,
    ["minecraft:diamond"] = 1,
}

--- Check if an item needs restocking.
--- @param itemName string
--- @param currentCount number
--- @return boolean true if restock is needed
function INVENTORY.needsRestock(itemName, currentCount)
    local threshold = INVENTORY.THRESHOLDS[itemName]
    if threshold == nil then
        return false
    end
    return currentCount < threshold
end

-- ============================================================
-- Fuel management
-- ============================================================

--- Check fuel status and return warning level.
--- @return string "ok", "warning", or "critical"
function INVENTORY.checkFuel()
    local fuel = turtle.getFuelLevel()
    if fuel <= CONFIG.FUEL_CRITICAL then
        return "critical"
    elseif fuel <= CONFIG.FUEL_WARNING then
        return "warning"
    end
    return "ok"
end

--- Compute how many moves are possible with current fuel.
--- @return number estimated moves remaining
function INVENTORY.estimateRange()
    return turtle.getFuelLevel()
end

-- ============================================================
-- Report formatting
-- ============================================================

--- Format a full inventory report as a readable string.
--- @param report table from scanAll()
--- @return string
function INVENTORY.formatReport(report)
    local lines = {}
    table.insert(lines, "=== TURTLE INVENTORY REPORT ===")
    table.insert(lines, string.format("Fuel: %d / %d (%s)",
        report.fuel, report.maxFuel, INVENTORY.checkFuel()))
    table.insert(lines, string.format("Total items: %d", report.totalItems))
    table.insert(lines, string.format("Free slots: %d / %d", report.freeSlots, CONFIG.SLOTS))
    table.insert(lines, "")

    for slot = 1, CONFIG.SLOTS do
        local item = report.slots[slot]
        if item and not item.empty then
            local category = INVENTORY.classify(item.name)
            table.insert(lines, string.format("  [%2d] %s x%d → %s",
                slot, item.name, item.count, category))
        end
    end

    return table.concat(lines, "\n")
end

-- ============================================================
-- Module return
-- ============================================================
return INVENTORY
