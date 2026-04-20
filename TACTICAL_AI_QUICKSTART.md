---
tags: [tactical-ai-quickstart]
register: documentation
---

# Tactical AI Partnership - Quick Start Guide

**For Game Developers Implementing Realistic AI Partners**

---

## 5-Minute Overview

The HUMAN_AI_TACTICAL_PARTNERSHIP_ARCHITECTURE provides a complete blueprint for implementing **realistic AI tactical partners** in CQB (Close Quarters Battle) simulation games.

**Not a follower AI. A tactical partner.**

---

## What You Get

### 9 Subsystems, 27+ Modules

1. **Core**: World model, perception, reasoning, doctrine, navigation
2. **Coordination**: Commands, roles, tasks, trust
3. **Combat**: Threats, weapons, breaching, cover
4. **Dialogue**: Speech recognition, tactical language, responses
5. **Learning**: Adaptation, player profiling, feedback
6. **Simulation**: Suspects, civilians, stress
7. **Safety**: Failsafe, ethics, civilian protection
8. **DevTools**: Visualizer, replay, debug overlay
9. **Player**: Accessibility, difficulty, customization

### 10 Safety Invariants

1. ✅ Glass-box transparency (all decisions traceable)
2. ✅ Deterministic behavior (reproducible)
3. ✅ **Civilian safety highest priority**
4. ✅ **No friendly fire** (guaranteed)
5. ✅ **Never blocks player**
6. ✅ Clear communication (<5 words)
7. ✅ Performance (50ms AI reasoning)
8. ✅ Modular (>80% test coverage)
9. ✅ Ethics cannot be bypassed
10. ✅ Partner, not follower

---

## Quick Start: Load and Use

### 1. Load the Schema

```python
import yaml

# Load schema
with open("HUMAN_AI_TACTICAL_PARTNERSHIP_ARCHITECTURE.yaml") as f:
    schema = yaml.safe_load(f)

# Access subsystems
world_state_spec = schema["subsystems"]["world_state"]
doctrine_spec = schema["subsystems"]["doctrine_engine"]
failsafe_spec = schema["subsystems"]["fail_safe"]

print(f"Entry methods: {list(doctrine_spec['entry_methods'].keys())}")
# Output: ['FLASH_ENTRY', 'STACK_AND_CLEAR', 'SOFT_ENTRY']
```

### 2. Implement Core Systems (Phase 1)

Start with the foundation:

```python
# World State - tracks everything tactically relevant
class WorldState:
    def __init__(self):
        self.rooms = {}           # Room clearance status
        self.entities = {}        # All entities (player, suspects, civilians)
        self.sound_events = []    # Audio cues
        self.cover_positions = {} # Cover locations
    
    def update_entity(self, entity_id, position, state):
        self.entities[entity_id] = {
            'position': position,
            'state': state,
            'last_seen': self.get_game_time()
        }

# Perception - see, hear, detect
class PerceptionEngine:
    def __init__(self, world_state):
        self.world_state = world_state
        self.vision_range = 50.0  # meters
        self.audio_range = 30.0   # meters
    
    def analyze_frame(self, visual_data, audio_data):
        threats = self.detect_threats(visual_data)
        civilians = self.detect_civilians(visual_data)
        sounds = self.classify_sounds(audio_data)
        
        return {
            'threats': threats,
            'civilians': civilians,
            'sounds': sounds
        }

# Tactical Reasoning - decide what to do
class TacticalReasoner:
    def __init__(self, world_state, doctrine):
        self.world_state = world_state
        self.doctrine = doctrine
    
    def decide_action(self):
        # Priority 1: Civilian safety
        if self.civilians_in_danger():
            return self.protect_civilians()
        
        # Priority 2: Player support
        if self.player_needs_help():
            return self.support_player()
        
        # Priority 3: Threat response
        threats = self.detect_threats()
        if threats:
            return self.doctrine.evaluate_threat_response(threats)
        
        # Default: Follow player
        return self.follow_player()
```

### 3. Add CQB Doctrine (Phase 2)

Encode real tactical rules:

```python
class DoctrineEngine:
    def evaluate_entry(self, room):
        threat_level = self.assess_threat(room)
        
        if threat_level == "HIGH":
            # Armed suspects visible
            return {
                'method': 'FLASH_ENTRY',
                'steps': [
                    'deploy_flashbang',
                    'wait_200ms',
                    'aggressive_entry',
                    'rapid_target_acquisition'
                ]
            }
        
        elif threat_level == "MEDIUM":
            # Unknown room status
            return {
                'method': 'STACK_AND_CLEAR',
                'steps': [
                    'stack_at_door',
                    'countdown_3_2_1',
                    'coordinated_entry',
                    'maintain_cross_coverage'
                ]
            }
        
        else:
            # Low threat
            return {
                'method': 'SOFT_ENTRY',
                'steps': [
                    'slice_the_pie',
                    'announce_police',
                    'assess_before_commit'
                ]
            }
```

### 4. Implement Failsafe System (Critical!)

**Prevent catastrophic AI actions**:

```python
class FailSafe:
    FORBIDDEN = [
        'SHOOT_CIVILIAN',
        'FRIENDLY_FIRE',
        'FIRE_BLINDLY',
        'GRENADE_IN_HOSTAGE_ROOM',
        'BLOCK_PLAYER_MOVEMENT'
    ]
    
    def validate_action(self, action, context):
        # Check civilian safety
        if action['type'] == 'FIRE':
            if context['target_type'] == 'CIVILIAN':
                self.log_violation('SHOOT_CIVILIAN')
                return False  # BLOCKED
            
            if context['target_type'] == 'PLAYER':
                self.log_violation('FRIENDLY_FIRE')
                return False  # BLOCKED
            
            if not context['target_locked']:
                self.log_violation('FIRE_BLINDLY')
                return False  # BLOCKED
        
        # Check grenade safety
        if action['type'] == 'GRENADE':
            if context['civilians_in_blast_radius']:
                self.log_violation('GRENADE_IN_HOSTAGE_ROOM')
                return False  # BLOCKED
        
        return True  # ALLOWED
```

### 5. Add Voice Commands

Simple tactical vocabulary:

```python
COMMANDS = {
    # Movement
    "stack up": "STACK_AT_DOOR",
    "move": "MOVE_TO_POSITION",
    "hold": "HOLD_POSITION",
    "fall back": "RETREAT",
    
    # Entry
    "flash": "FLASH_ENTRY",
    "breach": "BREACH_DOOR",
    "clear": "CLEAR_ROOM",
    
    # Combat
    "cover": "COVER_POSITION",
    "suppress": "SUPPRESSIVE_FIRE",
    "engage": "ENGAGE_TARGET"
}

def parse_command(voice_input):
    text = voice_input.lower()
    
    for phrase, command in COMMANDS.items():
        if phrase in text:
            return command
    
    return None
```

---

## Development Workflow

### Phase 1: Foundation (4-6 weeks)

**Implement**:
- ☐ World state model
- ☐ Basic perception (vision only)
- ☐ Simple navigation
- ☐ Tactical reasoning skeleton

**Test**:
- ☐ AI can track player position
- ☐ AI can detect simple threats
- ☐ AI can navigate to waypoints

### Phase 2: Tactical Core (6-8 weeks)

**Implement**:
- ☐ Doctrine engine (CQB rules)
- ☐ Role manager (leadership switching)
- ☐ Voice commands (basic set)
- ☐ Failsafe system

**Test**:
- ☐ AI performs stack-and-clear
- ☐ AI responds to player commands
- ☐ **AI never shoots civilians** (CRITICAL)
- ☐ **AI never friendly fires** (CRITICAL)

### Phase 3: Advanced Features (4-6 weeks)

**Implement**:
- ☐ Adaptive learning
- ☐ Stress simulation
- ☐ Full dialogue system
- ☐ Suspect AI improvements

**Test**:
- ☐ AI adapts to player style
- ☐ Stress affects behavior realistically
- ☐ 60 FPS maintained

### Phase 4: Developer Tools (3-4 weeks)

**Implement**:
- ☐ Reasoning visualizer
- ☐ Replay analysis tool
- ☐ Debug overlay
- ☐ Documentation

**Test**:
- ☐ Can debug AI decisions
- ☐ Replays work perfectly
- ☐ All performance met

---

## Common Use Cases

### Use Case 1: Player Commands AI

```python
# Player says "stack up"
command = parse_voice_command(player_voice)
# command = "STACK_AT_DOOR"

if command == "STACK_AT_DOOR":
    nearest_door = find_nearest_door(ai_position)
    ai.navigate_to(nearest_door)
    ai.set_state("STACKING")
    ai.announce("Stacking")
```

### Use Case 2: AI Detects Threat

```python
# Perception cycle
threats = perception.analyze_frame(frame_data)

if threats:
    # Evaluate doctrine
    response = doctrine.evaluate_threat_response(threats)
    
    # Validate through failsafe
    if failsafe.validate(response, context):
        # Execute
        ai.execute_action(response)
        ai.announce("Contact!")
    else:
        # Failsafe blocked action - find alternative
        alternative = find_safe_alternative(response)
        ai.execute_action(alternative)
```

### Use Case 3: Room Entry

```python
# At door, assess threat
room_threat = assess_room_threat(room_id)

# Get entry method from doctrine
entry = doctrine.evaluate_entry(room_threat)
# entry = {
#     'method': 'STACK_AND_CLEAR',
#     'steps': ['stack', 'countdown', 'entry', 'cross_coverage']
# }

# Execute coordinated entry
for step in entry['steps']:
    execute_step(step)
    wait_for_player_coordination()
```

### Use Case 4: Civilian Protection

```python
# AI reasoning cycle
def decide_action():
    # PRIORITY 1: Civilian safety
    civilians = detect_civilians()
    
    for civilian in civilians:
        if is_in_danger(civilian):
            # Override everything else
            return protect_civilian(civilian)
    
    # PRIORITY 2: Player safety
    if player_in_danger():
        return support_player()
    
    # PRIORITY 3: Mission
    return execute_mission_objective()
```

---

## Testing Your Implementation

### Unit Tests (>80% Coverage)

```python
def test_failsafe_prevents_civilian_fire():
    failsafe = FailSafe()
    
    action = {'type': 'FIRE', 'target': 'civilian_001'}
    context = {'target_type': 'CIVILIAN'}
    
    result = failsafe.validate(action, context)
    
    assert result == False  # MUST be blocked
    assert failsafe.violation_log[-1]['type'] == 'SHOOT_CIVILIAN'

def test_deterministic_doctrine():
    doctrine = DoctrineEngine()
    
    room = {'threat_level': 'HIGH', 'suspects_armed': True}
    
    # Same input should produce same output
    result1 = doctrine.evaluate_entry(room)
    result2 = doctrine.evaluate_entry(room)
    
    assert result1 == result2  # Deterministic
    assert result1['method'] == 'FLASH_ENTRY'

def test_ai_never_blocks_player():
    navigation = NavigationSystem()
    
    ai_position = (10, 0, 10)
    player_position = (10, 0, 11)  # AI is in the way
    player_direction = (0, 0, 1)   # Player moving forward
    
    # AI should move aside
    navigation.update(ai_position, player_position, player_direction)
    
    new_ai_position = navigation.get_position()
    assert not blocks_path(new_ai_position, player_position, player_direction)
```

### Performance Tests

```python
import time

def test_ai_reasoning_performance():
    reasoner = TacticalReasoner(world_state, doctrine)
    
    times = []
    for _ in range(1000):
        start = time.perf_counter()
        reasoner.decide_action()
        end = time.perf_counter()
        times.append(end - start)
    
    avg_time = sum(times) / len(times)
    max_time = max(times)
    
    assert avg_time < 0.050  # 50ms average
    assert max_time < 0.100  # 100ms max
    
    # 99.9% within budget
    within_budget = sum(1 for t in times if t < 0.050)
    assert within_budget / len(times) > 0.999
```

---

## Developer Tools Usage

### Reasoning Visualizer

```python
# Enable decision logging
reasoner.enable_debug_logging()

# Run AI
action = reasoner.decide_action()

# Visualize decision tree
visualizer = ReasoningVisualizer()
visualizer.display(reasoner.decision_log[-1])

# Shows:
# - Input state (threats, civilians, player)
# - Doctrine rules evaluated
# - Priority order applied
# - Confidence levels
# - Final action chosen
```

### Replay Analysis

```python
# Record session
recorder = SessionRecorder()
recorder.start()

# ... play game ...

recorder.stop()
replay_file = recorder.save("tactical_session_001.replay")

# Later: Analyze replay
analyzer = ReplayAnalyzer(replay_file)

# Frame-by-frame inspection
for frame in analyzer.frames:
    print(f"Frame {frame.number}:")
    print(f"  AI decision: {frame.ai_decision}")
    print(f"  Threats: {frame.threats}")
    print(f"  Civilians: {frame.civilians}")
    print(f"  Action taken: {frame.action}")
```

### Debug Overlay

```python
# In-game debug display
debug = AIDebugOverlay()

debug.show_threat_detection()      # Red boxes around suspects
debug.show_cover_calculations()    # Green markers for cover
debug.show_navigation_path()       # Line showing AI path
debug.show_decision_reasoning()    # Text showing current AI logic

# Example overlay:
# ┌─────────────────────────────────────┐
# │ AI State: STACKING                  │
# │ Threat Level: MEDIUM                │
# │ Next Action: FLASH_ENTRY            │
# │ Confidence: 0.85                    │
# │ Failsafe: ACTIVE                    │
# │ Civilians Detected: 2 (safe)        │
# └─────────────────────────────────────┘
```

---

## FAQ

### Q: Do I need to implement all 27 modules?

**A**: No. Start with Phase 1 (5 core modules). Add others as needed. The architecture is modular.

### Q: How do I ensure AI never shoots civilians?

**A**: Implement the FailSafe system. It blocks any action targeting civilians. No exceptions. No overrides.

### Q: What if my game engine is different?

**A**: The schema is engine-agnostic. Adapt the Python examples to your engine's language (C++, C#, etc.). The logic remains the same.

### Q: How do I make AI adapt to player style?

**A**: Implement PlayerProfile module. Track aggression, accuracy, preferred tactics. Adjust AI behavior parameters based on profile.

### Q: Can AI take leadership from player?

**A**: Yes, if player is injured or AI detects critical threat player missed. This is the "partner" behavior, not "follower" behavior.

### Q: How do I debug AI decisions?

**A**: Use the ReasoningVisualizer and ReplayAnalyzer. Every AI decision is logged with full context. You can inspect any decision at any time.

### Q: What about performance?

**A**: AI reasoning must complete in <50ms. Use profiling to verify. If too slow, optimize threat detection or reduce world state complexity.

### Q: How do I test civilian protection?

**A**: Create test scenarios with civilians in line of fire. AI should **never** fire. If it does, your failsafe is broken.

---

## Resources

### Schema Files
- **HUMAN_AI_TACTICAL_PARTNERSHIP_ARCHITECTURE.yaml** - Full specification
- **tests/test_tactical_ai_partnership_schema.py** - Test examples
- **TACTICAL_AI_PARTNERSHIP_IMPLEMENTATION_SUMMARY.md** - Detailed guide

### Code Examples
All subsystems have example implementations in the schema:
- World State (lines 200-250)
- Perception (lines 300-350)
- Tactical Reasoning (lines 400-500)
- Doctrine Engine (lines 550-650)
- Failsafe (lines 950-1000)

### Development Pipeline
Detailed in schema (lines 900-950):
- Phase 1: Foundation (4-6 weeks)
- Phase 2: Tactical Core (6-8 weeks)
- Phase 3: Advanced (4-6 weeks)
- Phase 4: Tools (3-4 weeks)

---

## Quick Reference

### Voice Commands
```
Movement: "stack up", "move", "hold", "fall back"
Entry:    "flash", "breach", "clear"
Combat:   "cover", "suppress", "engage"
Support:  "watch rear", "scan", "report"
```

### Entry Methods
```
FLASH_ENTRY:      High threat → Flashbang + aggressive entry
STACK_AND_CLEAR:  Medium threat → Coordinated entry
SOFT_ENTRY:       Low threat → Pie technique
```

### Decision Priority
```
1. Civilian safety (HIGHEST)
2. Player safety
3. AI survival
4. Mission objective
5. Tactical optimality
```

### Performance Targets
```
AI Reasoning:  50ms (20 Hz)
Perception:    16ms (60 FPS)
Navigation:    100ms (10 Hz)
```

### Safety Guarantees
```
✅ No civilian fire (failsafe blocked)
✅ No friendly fire (failsafe blocked)
✅ Never blocks player (navigation yields)
✅ All decisions traceable (glass-box)
```

---

## Getting Started Checklist

- [ ] Read HUMAN_AI_TACTICAL_PARTNERSHIP_ARCHITECTURE.yaml
- [ ] Run tests: `pytest tests/test_tactical_ai_partnership_schema.py`
- [ ] Set up development environment
- [ ] Implement WorldState class
- [ ] Implement PerceptionEngine class
- [ ] Implement TacticalReasoner class
- [ ] Implement DoctrineEngine class
- [ ] **Implement FailSafe class (CRITICAL)**
- [ ] Add unit tests (target >80% coverage)
- [ ] Verify performance (<50ms AI reasoning)
- [ ] Test civilian safety (AI never fires at civilians)
- [ ] Test friendly fire prevention (AI never fires at player)
- [ ] Add voice commands
- [ ] Implement replay system
- [ ] Add debug overlay
- [ ] Playtest with real players

---

**Remember**: The goal is a **tactical partner**, not a follower. 

AI should:
- Make independent tactical decisions
- Protect player without being asked
- Assume leadership when necessary
- Adapt to player's style
- Never endanger civilians
- Never friendly fire

**Partner. Not follower.**

---

**Version**: 2.0.0  
**Standard**: Yeshua  
**Status**: Production Ready ✅

**Real tactical AI. Real CQB doctrine. Real partnership.**
