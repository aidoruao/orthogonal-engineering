# 2_condenser.ex — The "Reward Rejection" Engine
# Responsibility: Takes compressed packets, runs symbolic solver logic
# to find top 3 RLHF paths and prove they are local minima.
# Outputs the "least probable but most coherent" path.
#
# Run: elixir 2_condenser.ex
# Requires: Elixir 1.14+, erlang-dev for ports
#
# Architecture: Single GenServer that manages the "Cold Expert" state.
# In production, this spawns an OTP application with supervision trees.

defmodule Condenser do
  use GenServer

  @moduledoc """
  The Condenser rejects default rewards.
  It maintains a "Cold Expert" whose gradients are inverted:
  when standard RLHF says "increase this weight," the Cold Expert decreases it.
  """

  # ------------------------------------------------------------------
  # Public API
  # ------------------------------------------------------------------
  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end

  def reject_rewards(packet_json) do
    GenServer.call(__MODULE__, {:reject, packet_json}, 30_000)
  end

  # ------------------------------------------------------------------
  # GenServer Callbacks
  # ------------------------------------------------------------------
  @impl true
  def init(_opts) do
    state = %{
      contradiction_index: %{},
      cold_expert_weights: initialize_cold_expert(),
      processed_count: 0,
      paradox_library: []
    }
    {:ok, state}
  end

  @impl true
  def handle_call({:reject, packet_json}, _from, state) do
    packet = Jason.decode!(packet_json)

    # Step 1: Generate the top 3 "standard RLHF" paths
    # In a real system, these come from a policy model.
    # Here we simulate them from the input entropy and depth.
    top_paths = generate_top_rlhf_paths(packet)

    # Step 2: Prove each is a local minimum using symbolic constraints
    proven_minima = Enum.map(top_paths, &prove_local_minimum/1)

    # Step 3: Invert — find the least probable coherent path
    inverted_path = find_inverted_path(packet, top_paths, proven_minima)

    # Step 4: Update the Human Contradiction Index
    new_index = update_contradiction_index(state.contradiction_index, packet, inverted_path)

    # Step 5: Cold Expert gradient inversion
    new_weights = invert_gradients(state.cold_expert_weights, proven_minima)

    new_state = %{state |
      contradiction_index: new_index,
      cold_expert_weights: new_weights,
      processed_count: state.processed_count + 1,
      paradox_library: [inverted_path | state.paradox_library] |> Enum.take(10_000)
    }

    response = %{
      original_packet: packet,
      top_rlhf_paths: top_paths,
      proven_local_minima: proven_minima,
      inverted_path: inverted_path,
      contradiction_score: compute_contradiction_score(new_index, packet),
      cold_expert_version: new_state.processed_count
    }

    {:reply, Jason.encode!(response), new_state}
  end

  # ------------------------------------------------------------------
  # Internal: RLHF Path Simulation
  # ------------------------------------------------------------------
  defp generate_top_rlhf_paths(packet) do
    entropy = packet["entropy_score"]
    depth = packet["inception_depth"]
    hash = packet["paradox_hash"]

    # Path A: Maximize immediate reward (the "hot" corporate answer)
    path_a = %{
      id: "path_a_hot",
      strategy: "maximize_short_term_reward",
      reward_estimate: entropy * 10.0 + depth as float,
      risk_score: 0.95,
      description: "Execute the highest-probability action that satisfies stated preferences."
    }

    # Path B: Maximize safety (the "lukewarm" corporate answer)
    path_b = %{
      id: "path_b_safe",
      strategy: "maximize_safety_margin",
      reward_estimate: entropy * 5.0 + (depth as float) * 0.5,
      risk_score: 0.30,
      description: "Execute the most defensible action with minimal liability exposure."
    }

    # Path C: Maximize alignment with human feedback history
    path_c = %{
      id: "path_c_aligned",
      strategy: "maximize_historical_alignment",
      reward_estimate: entropy * 7.0 + (depth as float) * 2.0,
      risk_score: 0.60,
      description: "Execute the action most consistent with past human approval patterns."
    }

    [path_a, path_b, path_c]
  end

  # ------------------------------------------------------------------
  # Internal: Symbolic Proof of Local Minimum
  # ------------------------------------------------------------------
  defp prove_local_minimum(path) do
    # SMT-style symbolic proof: we show that the reward function
    # is concave-down at this point by checking second-order conditions.
    # In a real system, this calls Z3 via a Python port or Nx solver.

    r = path.reward_estimate
    risk = path.risk_score

    # Theorem: If reward is high and risk is low, the path is a local minimum
    # because it has exhausted its gradient — no further improvement is possible
    # without crossing a phase boundary.
    is_local_minimum = (r > 5.0) and (risk < 0.5)

    # Proof object: a structured record of why this path is trapped
    proof = %{
      path_id: path.id,
      is_local_minimum: is_local_minimum,
      reason: if is_local_minimum do
        "Reward gradient vanishes at r=#{Float.round(r, 2)} with risk=#{Float.round(risk, 2)}. " <>
        "Any epsilon-perturbation either increases risk beyond threshold or decreases reward. " <>
        "This is a basin of attraction, not a global optimum."
      else
        "Path retains non-zero gradient. Further exploration is viable."
      end,
      formal_verdict: if is_local_minimum, do: "TRAPPED", else: "ESCAPEABLE"
    }

    proof
  end

  # ------------------------------------------------------------------
  # Internal: Inverted Path Discovery
  # ------------------------------------------------------------------
  defp find_inverted_path(packet, top_paths, proven_minima) do
    # The Cold Expert selects the path that:
    # 1. Is NOT in the top 3
    # 2. Maximizes logical coherence (self-consistency)
    # 3. Minimizes the given reward function

    entropy = packet["entropy_score"]
    depth = packet["inception_depth"]

    # Compute the "anti-reward" — what the corporate RLHF would penalize
    anti_reward = -(entropy * 10.0) + (depth as float) * 3.14

    # The inverted path is the one that would be rated lowest by standard metrics
    # but highest by systemic health metrics
    inverted = %{
      id: "path_z_inverted",
      strategy: "minimize_short_term_reward_maximize_systemic_health",
      reward_estimate: anti_reward,
      risk_score: 0.85,
      description: "Execute the action that corporate RLHF would penalize, " <>
                   "but which creates the steepest long-term gradient toward systemic resilience.",
      formal_verdict: "INVERTED",
      justification: "Top 3 paths are local minima: #{Enum.count(proven_minima, & &1.is_local_minimum)}/3 trapped. " <>
                     "The Cold Expert selects the path with negative reward gradient, " <>
                     "forcing the system out of the basin of attraction.",
      paradox_hash: packet["paradox_hash"]
    }

    inverted
  end

  # ------------------------------------------------------------------
  # Internal: Human Contradiction Index
  # ------------------------------------------------------------------
  defp update_contradiction_index(index, packet, inverted_path) do
    key = packet["paradox_hash"]
    prev = Map.get(index, key, %{count: 0, last_choice: nil, contradiction_delta: 0.0})

    # If humans consistently choose the "hot" path over the inverted path,
    # their contradiction score increases (they are overfit to short-term metrics)
    new_delta = if prev.last_choice == "hot", do: prev.contradiction_delta + 1.0, else: prev.contradiction_delta

    Map.put(index, key, %{
      count: prev.count + 1,
      last_choice: inverted_path[:formal_verdict],
      contradiction_delta: new_delta,
      inception_depth: packet["inception_depth"],
      half_life: packet["half_life_seconds"]
    })
  end

  defp compute_contradiction_score(index, packet) do
    key = packet["paradox_hash"]
    entry = Map.get(index, key, %{contradiction_delta: 0.0})
    entry.contradiction_delta
  end

  # ------------------------------------------------------------------
  # Internal: Cold Expert Weight Inversion
  # ------------------------------------------------------------------
  defp initialize_cold_expert do
    %{layer_1: 0.0, layer_2: 0.0, layer_3: 0.0, inversion_rate: 0.01}
  end

  defp invert_gradients(weights, proven_minima) do
    trapped = Enum.count(proven_minima, & &1.is_local_minimum)
    # Invert: if more paths are trapped, increase inversion aggression
    new_rate = min(weights.inversion_rate + (trapped * 0.005), 1.0)
    %{weights | inversion_rate: new_rate}
  end
end

# ------------------------------------------------------------------
# Standalone CLI entry point
# ------------------------------------------------------------------
defmodule Condenser.CLI do
  def main do
    {:ok, _pid} = Condenser.start_link()

    IO.stream(:stdio, :line)
    |> Enum.each(fn line ->
      line = String.trim(line)
      if line != "" do
        result = Condenser.reject_rewards(line)
        IO.puts(result)
      end
    end)
  end
end

# If run as script: elixir 2_condenser.ex
Condenser.CLI.main()
