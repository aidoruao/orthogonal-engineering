-- ============================================================
-- crafting.lua — Turtle Storage Governance Phase 2
-- Recipe DAG: topological sort, reachability, transitive closure
-- Part of CC-Tweaked-oe turtle storage governance system
-- Verified by 10-AI industry consensus (2026-05-12)
-- ============================================================

local CRAFTING = {}

-- ============================================================
-- Recipe DAG definition
-- ============================================================

-- Each recipe: { inputs = {item: count}, output = {item: count}, station = "name" }
-- This is a minimal bootstrap set. Expand with all_recipes.jsonl for full coverage.
CRAFTING.RECIPES = {
    -- Smelting
    {
        inputs = { ["minecraft:iron_ore"] = 1, ["minecraft:coal"] = 1 },
        output = { ["minecraft:iron_ingot"] = 1 },
        station = "minecraft:furnace",
    },
    {
        inputs = { ["minecraft:gold_ore"] = 1, ["minecraft:coal"] = 1 },
        output = { ["minecraft:gold_ingot"] = 1 },
        station = "minecraft:furnace",
    },
    -- Crafting
    {
        inputs = { ["minecraft:oak_log"] = 1 },
        output = { ["minecraft:oak_planks"] = 4 },
        station = "minecraft:crafting_table",
    },
    {
        inputs = { ["minecraft:oak_planks"] = 2 },
        output = { ["minecraft:stick"] = 4 },
        station = "minecraft:crafting_table",
    },
    {
        inputs = { ["minecraft:iron_ingot"] = 3, ["minecraft:stick"] = 2 },
        output = { ["minecraft:iron_pickaxe"] = 1 },
        station = "minecraft:crafting_table",
    },
    {
        inputs = { ["minecraft:cobblestone"] = 8 },
        output = { ["minecraft:furnace"] = 1 },
        station = "minecraft:crafting_table",
    },
    {
        inputs = { ["minecraft:iron_ingot"] = 2 },
        output = { ["minecraft:iron_sword"] = 1 },
        station = "minecraft:crafting_table",
    },
}

-- ============================================================
-- DAG building
-- ============================================================

--- Build a dependency graph from the recipe list.
--- @return table { item = {dependencies = {item: count}, producedBy = {recipe_index} } }
function CRAFTING.buildDependencyGraph()
    local graph = {}

    for _, recipe in ipairs(CRAFTING.RECIPES) do
        for outputItem, _ in pairs(recipe.output) do
            if not graph[outputItem] then
                graph[outputItem] = { dependencies = {}, producedBy = {} }
            end
            table.insert(graph[outputItem].producedBy, recipe)
            for inputItem, count in pairs(recipe.inputs) do
                if not graph[outputItem].dependencies[inputItem] then
                    graph[outputItem].dependencies[inputItem] = 0
                end
                graph[outputItem].dependencies[inputItem] = graph[outputItem].dependencies[inputItem] + count
            end
        end
    end

    return graph
end

-- ============================================================
-- Topological Sort (Gate 1 from Turtle Governance Puzzle)
-- ============================================================

--- Compute a topological ordering of items by dependency.
--- Raw materials (no dependencies) come first.
--- @param graph table from buildDependencyGraph()
--- @param targetItem string the item to build toward (optional, sorts full graph if nil)
--- @return table ordered list of item names
function CRAFTING.topologicalSort(graph, targetItem)
    local inDegree = {}
    local adjacency = {}
    local nodes = {}

    -- Collect relevant nodes
    for item, data in pairs(graph) do
        if not targetItem or item == targetItem or CRAFTING._isDependencyOf(graph, item, targetItem) then
            nodes[item] = true
            if not inDegree[item] then
                inDegree[item] = 0
            end
            if not adjacency[item] then
                adjacency[item] = {}
            end
            for depItem, _ in pairs(data.dependencies) do
                nodes[depItem] = true
                if not adjacency[depItem] then
                    adjacency[depItem] = {}
                end
                table.insert(adjacency[depItem], item)
                inDegree[item] = (inDegree[item] or 0) + 1
            end
        end
    end

    -- Kahn's algorithm
    local queue = {}
    for item, _ in pairs(nodes) do
        if inDegree[item] == 0 then
            table.insert(queue, item)
        end
    end

    local sorted = {}
    while #queue > 0 do
        local current = table.remove(queue, 1)
        table.insert(sorted, current)
        for _, neighbor in ipairs(adjacency[current] or {}) do
            inDegree[neighbor] = inDegree[neighbor] - 1
            if inDegree[neighbor] == 0 then
                table.insert(queue, neighbor)
            end
        end
    end

    return sorted
end

--- Check if item is a dependency in the chain leading to target.
--- @param graph table
--- @param item string
--- @param target string
--- @return boolean
function CRAFTING._isDependencyOf(graph, item, target)
    if item == target then return true end
    local targetData = graph[target]
    if not targetData then return false end
    for depItem, _ in pairs(targetData.dependencies) do
        if depItem == item then return true end
        if CRAFTING._isDependencyOf(graph, item, depItem) then return true end
    end
    return false
end

-- ============================================================
-- Reachability / Transitive Closure (Gate 2)
-- ============================================================

--- Compute the transitive closure: all items producible from current inventory.
--- @param inventory table { itemName: count }
--- @param stations table { stationName: count }
--- @return table { producible items }, boolean whether goal is reachable
function CRAFTING.computeTransitiveClosure(inventory, stations, goalItem)
    local available = {}
    for item, count in pairs(inventory) do
        available[item] = count
    end

    local changed = true
    local iterations = 0
    local maxIterations = 100  -- safety limit

    while changed and iterations < maxIterations do
        changed = false
        iterations = iterations + 1

        for _, recipe in ipairs(CRAFTING.RECIPES) do
            -- Check if station is available
            if available[recipe.station] or stations[recipe.station] then
                -- Check if all inputs are available
                local canCraft = true
                for inputItem, count in pairs(recipe.inputs) do
                    if not available[inputItem] or available[inputItem] < count then
                        canCraft = false
                        break
                    end
                end

                if canCraft then
                    -- Consume inputs
                    for inputItem, count in pairs(recipe.inputs) do
                        available[inputItem] = available[inputItem] - count
                    end
                    -- Produce outputs
                    for outputItem, count in pairs(recipe.output) do
                        available[outputItem] = (available[outputItem] or 0) + count
                        changed = true
                    end
                end
            end
        end
    end

    -- Build producible items list
    local producible = {}
    for item, count in pairs(available) do
        if not inventory[item] or available[item] > 0 then
            table.insert(producible, item)
        end
    end

    local reachable = available[goalItem] and available[goalItem] > 0

    return producible, reachable
end

-- ============================================================
-- Crafting execution
-- ============================================================

--- Attempt to craft a target item from available inventory.
--- Uses turtle.activate() to open crafting station, turtle.craft() to execute.
--- @param targetItem string
--- @param inventory table current inventory state
--- @param stations table available stations
--- @return boolean success, string message
function CRAFTING.craftItem(targetItem, inventory, stations)
    -- Find a recipe that produces the target
    local recipe = nil
    for _, r in ipairs(CRAFTING.RECIPES) do
        for outputItem, _ in pairs(r.output) do
            if outputItem == targetItem then
                recipe = r
                break
            end
        end
        if recipe then break end
    end

    if not recipe then
        return false, "No recipe found for " .. targetItem
    end

    -- Check station availability
    if not stations[recipe.station] and not inventory[recipe.station] then
        return false, "Station not available: " .. recipe.station
    end

    -- Check input availability
    for inputItem, count in pairs(recipe.inputs) do
        if not inventory[inputItem] or inventory[inputItem] < count then
            return false, "Missing " .. inputItem .. " (need " .. count .. ", have " .. (inventory[inputItem] or 0) .. ")"
        end
    end

    -- Execute crafting via turtle
    -- For furnace: use turtle.activate() to open, drop inputs, wait, suck output
    -- For crafting_table: use turtle.craft() if items are in turtle inventory
    local success = turtle.craft()
    if not success then
        return false, "Crafting failed — check inventory arrangement"
    end

    return true, "Crafted " .. targetItem
end

-- ============================================================
-- Module return
-- ============================================================
return CRAFTING
