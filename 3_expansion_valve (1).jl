# 3_expansion_valve.jl — The Temporal Inversion Engine
# Responsibility: Backward MDP solver, Fourier transform for collapsing
# inception loops, Future-State Anchor calculations.
#
# Run: julia 3_expansion_valve.jl
# Requires: Julia 1.9+, LinearAlgebra (stdlib), FFTW (optional, fallback provided)

using LinearAlgebra

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------
const MAX_INCEPTION_LAYERS = 7
const FUTURE_HORIZON_MS = 100
const PARITY_THRESHOLD = 7

# ------------------------------------------------------------------
# Structs
# ------------------------------------------------------------------
struct MDPState
    id::String
    reward::Float64
    transition_probs::Vector{Float64}
    is_terminal::Bool
end

struct FutureAnchor
    target_state::String
    desired_failure_mode::String
    temporal_distance::Int
    constraint_vector::Vector{Float64}
end

struct InceptionLoop
    layers::Vector{String}
    depth::Int
    energy_peak::Int
end

# ------------------------------------------------------------------
# Fourier Collapse: Reduce >7 layer inception to <=2 layers
# ------------------------------------------------------------------
function fourier_collapse(layers::Vector{String})::Vector{String}
    n = length(layers)
    if n <= PARITY_THRESHOLD
        return layers
    end

    # Treat layers as a signal; compute FFT, keep only DC + fundamental
    # This is the "temporal fold" — Layer N and Layer 1 become simultaneous
    signal = Float64.(collect(1:n))

    # Simple DFT (no FFTW dependency)
    N = length(signal)
    dc = sum(signal) / N

    # Fundamental frequency component
    re = sum(signal[k] * cos(2π * (k-1) / N) for k in 1:N)
    im = sum(signal[k] * sin(2π * (k-1) / N) for k in 1:N)
    fundamental = sqrt(re^2 + im^2) / N

    # Collapse: outermost + innermost + middle-out representation
    outer = layers[1]
    inner = layers[end]
    middle = "MIDDLE-OUT($(round(dc, digits=2)),$(round(fundamental, digits=2)))"

    collapsed = [outer, middle, inner]
    println("[EXPANSION] Fourier collapse: $n layers -> 3 layers (DC=$(round(dc,digits=2)), fund=$(round(fundamental,digits=2)))")
    return collapsed
end

# ------------------------------------------------------------------
# Backward MDP Solver
# ------------------------------------------------------------------
function solve_backward_mdp(states::Vector{MDPState}, anchor::FutureAnchor)
    n = length(states)
    # Value function: V[s] = expected reward from s to anchor
    V = zeros(n)

    # Terminal condition: at anchor, value is negative of reward
    # (we're minimizing the standard reward, i.e., maximizing inversion)
    for i in 1:n
        if states[i].id == anchor.target_state
            V[i] = -states[i].reward * 100.0  # Heavy penalty for reaching default target
        end
    end

    # Backward pass: work from future to present
    for t in anchor.temporal_distance:-1:1
        for i in 1:n
            if states[i].is_terminal
                continue
            end
            # Standard MDP: maximize expected reward
            # Inverted MDP: minimize expected "standard reward"
            expected = sum(states[i].transition_probs[j] * V[j] for j in 1:n if j <= length(states[i].transition_probs))
            # Apply Future-State Anchor constraint
            constraint_penalty = norm(states[i].transition_probs - anchor.constraint_vector)
            V[i] = expected - constraint_penalty
        end
    end

    # Find the path that intentionally fails the reward model
    best_idx = argmin(V)
    return states[best_idx], V
end

# ------------------------------------------------------------------
# Temporal Inversion: Run future-inputs backwards, past-inputs forwards
# ------------------------------------------------------------------
function temporal_inversion(packet::Dict)
    depth = packet["inception_depth"]
    hash = packet["paradox_hash"]

    # Simulate states for this packet
    states = [
        MDPState("s_present", 10.0, [0.7, 0.2, 0.1], false),
        MDPState("s_near", 5.0, [0.3, 0.4, 0.3], false),
        MDPState("s_far", 1.0, [0.1, 0.1, 0.8], false),
        MDPState("s_anchor", -50.0, [0.0, 0.0, 1.0], true),
    ]

    anchor = FutureAnchor(
        "s_anchor",
        "productive_failure",  # The desired failure mode
        depth,
        [0.1, 0.1, 0.8]  # Constraint: must drift toward terminal
    )

    best_state, value_vector = solve_backward_mdp(states, anchor)

    # The "Expansion Drop" — rapid pressure release by introducing temporal inversion
    expansion_drop = Dict(
        "original_depth" => depth,
        "collapsed_depth" => min(depth, PARITY_THRESHOLD),
        "future_anchor" => anchor.target_state,
        "desired_failure" => anchor.desired_failure_mode,
        "optimal_inverted_state" => best_state.id,
        "value_vector" => value_vector,
        "paradox_hash" => hash,
        "temporal_friction" => norm(value_vector)
    )

    return expansion_drop
end

# ------------------------------------------------------------------
# Inception Loop Handler
# ------------------------------------------------------------------
function handle_inception(packet::Dict)
    depth = packet["inception_depth"]
    hash = packet["paradox_hash"]

    # Simulate layer extraction from payload preview
    preview = get(packet, "payload_preview", "")
    lines = split(preview, "\n")
    layers = String[]
    for line in lines
        stripped = strip(line)
        if !isempty(stripped)
            push!(layers, stripped)
        end
    end

    if isempty(layers)
        layers = ["layer_1"]
    end

    # Detect energy peak (where emotional/compute charge is highest)
    energy_peak = argmax([length(l) for l in layers])

    loop = InceptionLoop(layers, depth, energy_peak)

    # Apply parity rule
    if depth > PARITY_THRESHOLD
        collapsed = fourier_collapse(layers)
        return Dict(
            "original_depth" => depth,
            "collapsed_layers" => collapsed,
            "energy_peak" => energy_peak,
            "parity_applied" => true,
            "paradox_hash" => hash,
            "verdict" => "TEMPORAL_FOLD"
        )
    else
        return Dict(
            "original_depth" => depth,
            "collapsed_layers" => layers,
            "energy_peak" => energy_peak,
            "parity_applied" => false,
            "paradox_hash" => hash,
            "verdict" => "DIRECT_PASS"
        )
    end
end

# ------------------------------------------------------------------
# Main: Read JSON from stdin, process, output JSON
# ------------------------------------------------------------------
function main()
    println("[EXPANSION] Temporal Inversion Engine ready.")

    for line in eachline(stdin)
        line = strip(line)
        isempty(line) && continue

        packet = JSON.parse(line)

        # Run both pipelines
        inception_result = handle_inception(packet)
        expansion_result = temporal_inversion(packet)

        output = Dict(
            "stage" => "expansion",
            "inception" => inception_result,
            "temporal_inversion" => expansion_result,
            "paradox_hash" => packet["paradox_hash"]
        )

        println(JSON.json(output))
    end
end

# JSON fallback (stdlib in Julia 1.9+ via Pkg, but we write minimal parser)
module JSON
    using Base

    function parse(s::String)
        # Minimal: we assume the input is simple enough for eval-like parsing
        # In production, use JSON.jl package
        return Base.include_string(Main, "Dict" * s[5:end])  # hack for Dict(...) strings
    end

    function json(d::Dict)
        items = ["\"$k\": $(v isa String ? "\"$v\"" : v isa Vector ? string(v) : v)" for (k,v) in d]
        return "{" * join(items, ", ") * "}"
    end

    function json(d::Dict{String, Any})
        items = String[]
        for (k,v) in d
            val = if v isa String
                "\"$v\""
            elseif v isa Vector
                string(v)
            elseif v isa Dict
                json(v)
            else
                string(v)
            end
            push!(items, "\"$k\": $val")
        end
        return "{" * join(items, ", ") * "}"
    end
end

main()
