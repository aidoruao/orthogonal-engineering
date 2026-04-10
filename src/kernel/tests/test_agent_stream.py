"""Tests for Agent Stream — Symbolic Subagent Spawning

Test coverage:
- Agent spawning with AgentCap
- Lazy evaluation (materialization on observation)
- Copy-on-write (COW) forking
- Resource accounting with Fraction
- Termination and cleanup

All tests use Fraction arithmetic (no floats) and verify ProofObject returns.
"""

import pytest
from fractions import Fraction

from axioms.logic import ProofObject
from axioms.capability_security import Permission

from kernel.agent_stream import (
    AgentCap, SymbolicAgent, AgentState, AgentStreamState,
    MaterializationTrigger,
    spawn_agent, materialize_agent, fork_agent_cow,
    terminate_agent, check_agent_resource_usage,
    get_agent_statistics, observe_agent_state
)


class TestAgentSpawning:
    """Test symbolic agent spawning."""
    
    def test_spawn_agent_success(self):
        """Test successful agent spawning."""
        parent_cap = AgentCap(
            agent_id="parent",
            holder_id="root",
            permissions=frozenset([Permission.WRITE]),
            delegator="root",
            resource_quota=Fraction(1000),
            spawn_depth=0
        )
        state = AgentStreamState()
        
        new_state, agent, proof = spawn_agent(
            state, parent_cap, "intent_abc",
            Fraction(100), Fraction(50),
            Fraction(1000), None
        )
        
        assert agent is not None
        assert agent.state == AgentState.SYMBOLIC
        assert agent.intent_hash == "intent_abc"
        assert agent.memory_quota == Fraction(100)
        assert agent.cpu_quota == Fraction(50)
        assert agent.parent_id is None
        assert "symbolic agent spawned" in proof.conclusion
    
    def test_spawn_agent_no_permission(self):
        """Test spawning fails without WRITE permission."""
        parent_cap = AgentCap(
            agent_id="parent",
            holder_id="root",
            permissions=frozenset([Permission.READ]),  # No WRITE
            delegator="root",
            resource_quota=Fraction(1000),
            spawn_depth=0
        )
        state = AgentStreamState()
        
        new_state, agent, proof = spawn_agent(
            state, parent_cap, "intent_abc",
            Fraction(100), Fraction(50),
            Fraction(1000), None
        )
        
        assert agent is None
        assert "no WRITE permission" in proof.conclusion
    
    def test_spawn_agent_depth_limit(self):
        """Test spawning fails at max nesting depth."""
        parent_cap = AgentCap(
            agent_id="parent",
            holder_id="root",
            permissions=frozenset([Permission.WRITE]),
            delegator="root",
            resource_quota=Fraction(1000),
            spawn_depth=10  # At limit
        )
        state = AgentStreamState()
        
        new_state, agent, proof = spawn_agent(
            state, parent_cap, "intent_abc",
            Fraction(100), Fraction(50),
            Fraction(1000), "parent_id"
        )
        
        assert agent is None
        assert "maximum nesting depth" in proof.conclusion
    
    def test_spawn_tracks_resource_allocation(self):
        """Test that spawning tracks total resource allocation."""
        parent_cap = AgentCap(
            agent_id="parent",
            holder_id="root",
            permissions=frozenset([Permission.WRITE]),
            delegator="root",
            resource_quota=Fraction(1000),
            spawn_depth=0
        )
        state = AgentStreamState()
        
        # Spawn first agent
        state, agent1, _ = spawn_agent(
            state, parent_cap, "intent_1",
            Fraction(100), Fraction(50),
            Fraction(1000), None
        )
        
        # Spawn second agent
        state, agent2, _ = spawn_agent(
            state, parent_cap, "intent_2",
            Fraction(200), Fraction(100),
            Fraction(2000), None
        )
        
        assert state.total_memory_allocated == Fraction(300)  # 100 + 200
        assert state.total_cpu_allocated == Fraction(150)     # 50 + 100
        assert state.spawn_count == 2


class TestLazyEvaluation:
    """Test lazy evaluation (materialization on observation)."""
    
    def test_materialize_on_observation(self):
        """Test that observation triggers materialization."""
        # Create symbolic agent
        agent_cap = AgentCap(
            agent_id="agent_1",
            holder_id="agent_1",
            permissions=frozenset([Permission.READ]),
            delegator="root",
            resource_quota=Fraction(100)
        )
        agent = SymbolicAgent(
            agent_id="agent_1",
            parent_id=None,
            state=AgentState.SYMBOLIC,
            intent_hash="intent_abc",
            capability_set=frozenset([agent_cap]),
            memory_quota=Fraction(100),
            cpu_quota=Fraction(50),
            spawn_quota=10
        )
        state = AgentStreamState(agents={"agent_1": agent})
        
        observer_cap = AgentCap(
            agent_id="observer",
            holder_id="observer",
            permissions=frozenset([Permission.READ]),
            delegator="root",
            resource_quota=Fraction(1000)
        )
        
        # Materialize
        new_state, success, proof = materialize_agent(
            state, "agent_1", MaterializationTrigger.OBSERVATION,
            Fraction(2000), observer_cap
        )
        
        assert success is True
        assert new_state.agents["agent_1"].state == AgentState.MATERIALIZED
        assert new_state.agents["agent_1"].materialized_pid is not None
        assert new_state.agents["agent_1"].materialization_trigger == MaterializationTrigger.OBSERVATION
        assert new_state.materialized_count == 1
    
    def test_materialize_already_materialized(self):
        """Test materializing an already-materialized agent."""
        agent_cap = AgentCap(
            agent_id="agent_1",
            holder_id="agent_1",
            permissions=frozenset([Permission.READ]),
            delegator="root",
            resource_quota=Fraction(100)
        )
        agent = SymbolicAgent(
            agent_id="agent_1",
            parent_id=None,
            state=AgentState.MATERIALIZED,
            intent_hash="intent_abc",
            capability_set=frozenset([agent_cap]),
            memory_quota=Fraction(100),
            cpu_quota=Fraction(50),
            spawn_quota=10,
            materialized_pid="pid_123",
            materialization_time=Fraction(1000)
        )
        state = AgentStreamState(agents={"agent_1": agent})
        
        observer_cap = AgentCap(
            agent_id="observer",
            holder_id="observer",
            permissions=frozenset([Permission.READ]),
            delegator="root",
            resource_quota=Fraction(1000)
        )
        
        new_state, success, proof = materialize_agent(
            state, "agent_1", MaterializationTrigger.OBSERVATION,
            Fraction(2000), observer_cap
        )
        
        assert success is True
        assert "already materialized" in proof.conclusion
    
    def test_materialize_terminated_fails(self):
        """Test that materializing terminated agent fails."""
        agent_cap = AgentCap(
            agent_id="agent_1",
            holder_id="agent_1",
            permissions=frozenset([Permission.READ]),
            delegator="root",
            resource_quota=Fraction(100)
        )
        agent = SymbolicAgent(
            agent_id="agent_1",
            parent_id=None,
            state=AgentState.TERMINATED,
            intent_hash="intent_abc",
            capability_set=frozenset([agent_cap]),
            memory_quota=Fraction(100),
            cpu_quota=Fraction(50),
            spawn_quota=10
        )
        state = AgentStreamState(agents={"agent_1": agent})
        
        observer_cap = AgentCap(
            agent_id="observer",
            holder_id="observer",
            permissions=frozenset([Permission.READ]),
            delegator="root",
            resource_quota=Fraction(1000)
        )
        
        new_state, success, proof = materialize_agent(
            state, "agent_1", MaterializationTrigger.OBSERVATION,
            Fraction(2000), observer_cap
        )
        
        assert success is False
        assert "terminated" in proof.conclusion
    
    def test_observe_triggers_materialization(self):
        """Test that observe_agent_state triggers materialization."""
        agent_cap = AgentCap(
            agent_id="agent_1",
            holder_id="agent_1",
            permissions=frozenset([Permission.READ]),
            delegator="root",
            resource_quota=Fraction(100)
        )
        agent = SymbolicAgent(
            agent_id="agent_1",
            parent_id=None,
            state=AgentState.SYMBOLIC,
            intent_hash="intent_abc",
            capability_set=frozenset([agent_cap]),
            memory_quota=Fraction(100),
            cpu_quota=Fraction(50),
            spawn_quota=10
        )
        state = AgentStreamState(agents={"agent_1": agent})
        
        observer_cap = AgentCap(
            agent_id="observer",
            holder_id="observer",
            permissions=frozenset([Permission.READ]),
            delegator="root",
            resource_quota=Fraction(1000)
        )
        
        new_state, observed, proof = observe_agent_state(
            state, "agent_1", observer_cap, Fraction(2000)
        )
        
        assert observed is not None
        assert observed.state == AgentState.MATERIALIZED
        assert "materialized" in proof.conclusion


class TestCOWForking:
    """Test copy-on-write (COW) forking."""
    
    def test_fork_agent_cow_success(self):
        """Test successful COW fork."""
        agent_cap = AgentCap(
            agent_id="agent_1",
            holder_id="agent_1",
            permissions=frozenset([Permission.READ, Permission.WRITE]),
            delegator="root",
            resource_quota=Fraction(100)
        )
        agent = SymbolicAgent(
            agent_id="agent_1",
            parent_id=None,
            state=AgentState.MATERIALIZED,
            intent_hash="intent_abc",
            capability_set=frozenset([agent_cap]),
            memory_quota=Fraction(100),
            cpu_quota=Fraction(50),
            spawn_quota=10,
            materialized_pid="pid_123"
        )
        state = AgentStreamState(agents={"agent_1": agent})
        
        forker_cap = AgentCap(
            agent_id="forker",
            holder_id="forker",
            permissions=frozenset([Permission.WRITE]),
            delegator="root",
            resource_quota=Fraction(1000)
        )
        
        new_state, forked, proof = fork_agent_cow(
            state, "agent_1", forker_cap, Fraction(3000),
            cow_memory_delta=Fraction(50)
        )
        
        assert forked is not None
        assert forked.fork_parent == "agent_1"
        assert forked.state == AgentState.SYMBOLIC  # Fork starts symbolic
        assert forked.memory_quota == Fraction(150)  # 100 + 50 delta
        assert len(forked.cow_layers) == 1
        assert "COW" in proof.conclusion
    
    def test_fork_tracks_cow_layer(self):
        """Test that fork creates COW layer in state."""
        agent_cap = AgentCap(
            agent_id="agent_1",
            holder_id="agent_1",
            permissions=frozenset([Permission.READ, Permission.WRITE]),
            delegator="root",
            resource_quota=Fraction(100)
        )
        agent = SymbolicAgent(
            agent_id="agent_1",
            parent_id=None,
            state=AgentState.MATERIALIZED,
            intent_hash="intent_abc",
            capability_set=frozenset([agent_cap]),
            memory_quota=Fraction(100),
            cpu_quota=Fraction(50),
            spawn_quota=10
        )
        state = AgentStreamState(agents={"agent_1": agent})
        
        forker_cap = AgentCap(
            agent_id="forker",
            holder_id="forker",
            permissions=frozenset([Permission.WRITE]),
            delegator="root",
            resource_quota=Fraction(1000)
        )
        
        new_state, forked, _ = fork_agent_cow(
            state, "agent_1", forker_cap, Fraction(3000),
            cow_memory_delta=Fraction(50)
        )
        
        # Check COW layer was created
        assert len(new_state.cow_layers) == 1
        cow_layer_id = list(new_state.cow_layers.keys())[0]
        cow_layer = new_state.cow_layers[cow_layer_id]
        assert cow_layer["parent_agent"] == "agent_1"
        assert cow_layer["fork_agent"] == forked.agent_id
        assert cow_layer["delta_memory"] == Fraction(50)
    
    def test_fork_no_permission(self):
        """Test fork fails without WRITE permission."""
        agent_cap = AgentCap(
            agent_id="agent_1",
            holder_id="agent_1",
            permissions=frozenset([Permission.READ]),
            delegator="root",
            resource_quota=Fraction(100)
        )
        agent = SymbolicAgent(
            agent_id="agent_1",
            parent_id=None,
            state=AgentState.MATERIALIZED,
            intent_hash="intent_abc",
            capability_set=frozenset([agent_cap]),
            memory_quota=Fraction(100),
            cpu_quota=Fraction(50),
            spawn_quota=10
        )
        state = AgentStreamState(agents={"agent_1": agent})
        
        forker_cap = AgentCap(
            agent_id="forker",
            holder_id="forker",
            permissions=frozenset([Permission.READ]),  # No WRITE
            delegator="root",
            resource_quota=Fraction(1000)
        )
        
        new_state, forked, proof = fork_agent_cow(
            state, "agent_1", forker_cap, Fraction(3000)
        )
        
        assert forked is None
        assert "no WRITE permission" in proof.conclusion
    
    def test_fork_inherits_capabilities(self):
        """Test that fork inherits parent's capabilities."""
        agent_cap = AgentCap(
            agent_id="agent_1",
            holder_id="agent_1",
            permissions=frozenset([Permission.READ, Permission.WRITE, Permission.DELEGATE]),
            delegator="root",
            resource_quota=Fraction(100)
        )
        agent = SymbolicAgent(
            agent_id="agent_1",
            parent_id=None,
            state=AgentState.MATERIALIZED,
            intent_hash="intent_abc",
            capability_set=frozenset([agent_cap]),
            memory_quota=Fraction(100),
            cpu_quota=Fraction(50),
            spawn_quota=10
        )
        state = AgentStreamState(agents={"agent_1": agent})
        
        forker_cap = AgentCap(
            agent_id="forker",
            holder_id="forker",
            permissions=frozenset([Permission.WRITE]),
            delegator="root",
            resource_quota=Fraction(1000)
        )
        
        new_state, forked, _ = fork_agent_cow(
            state, "agent_1", forker_cap, Fraction(3000)
        )
        
        # Fork should share capability set
        assert forked.capability_set == agent.capability_set


class TestAgentTermination:
    """Test agent termination and cleanup."""
    
    def test_terminate_agent_success(self):
        """Test successful agent termination."""
        agent_cap = AgentCap(
            agent_id="agent_1",
            holder_id="agent_1",
            permissions=frozenset([Permission.READ]),
            delegator="root",
            resource_quota=Fraction(100)
        )
        agent = SymbolicAgent(
            agent_id="agent_1",
            parent_id=None,
            state=AgentState.MATERIALIZED,
            intent_hash="intent_abc",
            capability_set=frozenset([agent_cap]),
            memory_quota=Fraction(100),
            cpu_quota=Fraction(50),
            spawn_quota=10,
            materialized_pid="pid_123"
        )
        state = AgentStreamState(
            agents={"agent_1": agent},
            materialized_count=1,
            total_memory_allocated=Fraction(100),
            total_cpu_allocated=Fraction(50)
        )
        
        terminator_cap = AgentCap(
            agent_id="root",
            holder_id="root",
            permissions=frozenset([Permission.REVOKE]),
            delegator="root",
            resource_quota=Fraction(1000)
        )
        
        new_state, success, proof = terminate_agent(
            state, "agent_1", terminator_cap, Fraction(4000)
        )
        
        assert success is True
        assert new_state.agents["agent_1"].state == AgentState.TERMINATED
        assert new_state.agents["agent_1"].memory_quota == Fraction(0)
        assert new_state.materialized_count == 0
        assert new_state.total_memory_allocated == Fraction(0)
        assert "terminated" in proof.conclusion
    
    def test_parent_can_terminate_child(self):
        """Test that parent can terminate child without REVOKE permission."""
        agent_cap = AgentCap(
            agent_id="child",
            holder_id="child",
            permissions=frozenset([Permission.READ]),
            delegator="parent",
            resource_quota=Fraction(100)
        )
        agent = SymbolicAgent(
            agent_id="child",
            parent_id="parent",  # Has parent
            state=AgentState.MATERIALIZED,
            intent_hash="intent_abc",
            capability_set=frozenset([agent_cap]),
            memory_quota=Fraction(100),
            cpu_quota=Fraction(50),
            spawn_quota=10
        )
        state = AgentStreamState(agents={"child": agent})
        
        # Parent terminator cap (no REVOKE, but is parent)
        parent_cap = AgentCap(
            agent_id="parent",
            holder_id="parent",
            permissions=frozenset([Permission.READ, Permission.WRITE]),  # No REVOKE
            delegator="root",
            resource_quota=Fraction(1000)
        )
        
        new_state, success, proof = terminate_agent(
            state, "child", parent_cap, Fraction(4000)
        )
        
        assert success is True
        assert new_state.agents["child"].state == AgentState.TERMINATED
    
    def test_terminate_no_permission(self):
        """Test termination fails without permission."""
        agent_cap = AgentCap(
            agent_id="agent_1",
            holder_id="agent_1",
            permissions=frozenset([Permission.READ]),
            delegator="root",
            resource_quota=Fraction(100)
        )
        agent = SymbolicAgent(
            agent_id="agent_1",
            parent_id=None,
            state=AgentState.MATERIALIZED,
            intent_hash="intent_abc",
            capability_set=frozenset([agent_cap]),
            memory_quota=Fraction(100),
            cpu_quota=Fraction(50),
            spawn_quota=10
        )
        state = AgentStreamState(agents={"agent_1": agent})
        
        # Random terminator (not parent, no REVOKE)
        random_cap = AgentCap(
            agent_id="random",
            holder_id="random",
            permissions=frozenset([Permission.READ]),
            delegator="root",
            resource_quota=Fraction(1000)
        )
        
        new_state, success, proof = terminate_agent(
            state, "agent_1", random_cap, Fraction(4000)
        )
        
        assert success is False
        assert "insufficient permission" in proof.conclusion


class TestResourceAccounting:
    """Test Fraction-based resource accounting."""
    
    def test_check_resource_usage(self):
        """Test resource usage query."""
        agent_cap = AgentCap(
            agent_id="agent_1",
            holder_id="agent_1",
            permissions=frozenset([Permission.READ]),
            delegator="root",
            resource_quota=Fraction(100)
        )
        agent = SymbolicAgent(
            agent_id="agent_1",
            parent_id=None,
            state=AgentState.MATERIALIZED,
            intent_hash="intent_abc",
            capability_set=frozenset([agent_cap]),
            memory_quota=Fraction(150),
            cpu_quota=Fraction(75),
            spawn_quota=10,
            cow_layers=["cow_1", "cow_2"]
        )
        state = AgentStreamState(agents={"agent_1": agent})
        
        usage, proof = check_agent_resource_usage(state, "agent_1")
        
        assert usage is not None
        memory, cpu = usage
        assert memory == Fraction(150)
        assert cpu == Fraction(75)
        assert "cow_layers=2" in str(proof.premises)
    
    def test_get_statistics(self):
        """Test aggregate statistics."""
        # Create agents in different states
        agents = {
            "sym_1": SymbolicAgent(
                agent_id="sym_1", parent_id=None, state=AgentState.SYMBOLIC,
                intent_hash="i1", capability_set=frozenset(),
                memory_quota=Fraction(100), cpu_quota=Fraction(50), spawn_quota=10
            ),
            "mat_1": SymbolicAgent(
                agent_id="mat_1", parent_id=None, state=AgentState.MATERIALIZED,
                intent_hash="i2", capability_set=frozenset(),
                memory_quota=Fraction(200), cpu_quota=Fraction(100), spawn_quota=10,
                materialized_pid="pid_1"
            ),
            "term_1": SymbolicAgent(
                agent_id="term_1", parent_id=None, state=AgentState.TERMINATED,
                intent_hash="i3", capability_set=frozenset(),
                memory_quota=Fraction(0), cpu_quota=Fraction(0), spawn_quota=0
            ),
        }
        state = AgentStreamState(
            agents=agents,
            spawn_count=3,
            materialized_count=1,
            total_memory_allocated=Fraction(300),
            total_cpu_allocated=Fraction(150)
        )
        
        stats, proof = get_agent_statistics(state)
        
        assert stats["total_agents"] == 3
        assert stats["symbolic_count"] == 1
        assert stats["materialized_count"] == 1
        assert stats["active_agents"] == 2  # Not terminated
        assert stats["total_memory_allocated"] == Fraction(300)


class TestAgentCapabilities:
    """Test AgentCap functionality."""
    
    def test_agent_cap_permission_check(self):
        """Test capability permission checking."""
        cap = AgentCap(
            agent_id="agent_1",
            holder_id="agent_1",
            permissions=frozenset([Permission.READ, Permission.WRITE]),
            delegator="root",
            resource_quota=Fraction(100)
        )
        
        assert cap.has_permission(Permission.READ) is True
        assert cap.has_permission(Permission.WRITE) is True
        assert cap.has_permission(Permission.REVOKE) is False
    
    def test_spawn_depth_tracking(self):
        """Test spawn depth tracking across generations."""
        root_cap = AgentCap(
            agent_id="root",
            holder_id="root",
            permissions=frozenset([Permission.WRITE]),
            delegator="root",
            resource_quota=Fraction(1000),
            spawn_depth=0
        )
        state = AgentStreamState()
        
        # Spawn child
        state, child, _ = spawn_agent(
            state, root_cap, "child_intent",
            Fraction(100), Fraction(50),
            Fraction(1000), None
        )
        
        # Get child's capability (child has its own cap)
        child_cap = list(child.capability_set)[0]
        assert child_cap.spawn_depth == 1
        
        # Spawn grandchild
        state, grandchild, _ = spawn_agent(
            state, child_cap, "grandchild_intent",
            Fraction(50), Fraction(25),
            Fraction(2000), child.agent_id
        )
        
        grandchild_cap = list(grandchild.capability_set)[0]
        assert grandchild_cap.spawn_depth == 2


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_materialize_nonexistent_agent(self):
        """Test materializing non-existent agent."""
        state = AgentStreamState()
        
        observer_cap = AgentCap(
            agent_id="observer",
            holder_id="observer",
            permissions=frozenset([Permission.READ]),
            delegator="root",
            resource_quota=Fraction(1000)
        )
        
        new_state, success, proof = materialize_agent(
            state, "nonexistent", MaterializationTrigger.OBSERVATION,
            Fraction(1000), observer_cap
        )
        
        assert success is False
        assert "not found" in proof.conclusion
    
    def test_fork_nonexistent_agent(self):
        """Test forking non-existent agent."""
        state = AgentStreamState()
        
        forker_cap = AgentCap(
            agent_id="forker",
            holder_id="forker",
            permissions=frozenset([Permission.WRITE]),
            delegator="root",
            resource_quota=Fraction(1000)
        )
        
        new_state, forked, proof = fork_agent_cow(
            state, "nonexistent", forker_cap, Fraction(1000)
        )
        
        assert forked is None
        assert "not found" in proof.conclusion
    
    def test_terminate_nonexistent_agent(self):
        """Test terminating non-existent agent."""
        state = AgentStreamState()
        
        terminator_cap = AgentCap(
            agent_id="root",
            holder_id="root",
            permissions=frozenset([Permission.REVOKE]),
            delegator="root",
            resource_quota=Fraction(1000)
        )
        
        new_state, success, proof = terminate_agent(
            state, "nonexistent", terminator_cap, Fraction(1000)
        )
        
        assert success is False
        assert "not found" in proof.conclusion


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
