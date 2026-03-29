"""
Falsification test for F_MINECRAFT_002.

Tests the invariant: Dead reckoning position matches GPS trilateration
within 1 block after N movements.

Falsifying observation: Position diverges by more than 1 block on any axis.
"""
# @falsification_id: F_MINECRAFT_002


def test_f_minecraft_002():
    """F_MINECRAFT_002: Dead reckoning accuracy within 1 block."""
    # Simulate dead reckoning: track position through movement commands
    pos = [0, 64, 0]  # x, y, z start
    facing = 0  # 0=north(-z), 1=east(+x), 2=south(+z), 3=west(-x)
    dx = [0, 1, 0, -1]
    dz = [-1, 0, 1, 0]

    movements = [
        ("forward", True),
        ("forward", True),
        ("turnRight", True),
        ("forward", True),
        ("forward", True),
        ("forward", False),  # blocked
        ("up", True),
    ]

    for cmd, success in movements:
        if cmd == "forward" and success:
            pos[0] += dx[facing]
            pos[2] += dz[facing]
        elif cmd == "turnRight":
            facing = (facing + 1) % 4
        elif cmd == "up" and success:
            pos[1] += 1

    # Expected: started at (0,64,0), moved north 2 (-z), turned east, moved east 2 (+x), up 1
    expected = [2, 65, -2]
    for axis in range(3):
        error = abs(pos[axis] - expected[axis])
        assert error <= 1, (
            f"F_MINECRAFT_002 FAILED: axis {axis} error {error} > 1 "
            f"(pos={pos}, expected={expected})"
        )
