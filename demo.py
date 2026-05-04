from simulation import DELTA_TRIANGLE, Entity, Simulation

sim = Simulation(width=30, height=15, tick_size=1.0)

# Diagonal traveler: bottom-left to top-right, passes through (15, 7)
sim.entities.append(Entity(
    id="traveler",
    symbol="X",
    size=1,
    speed=1.0,
    spawn_time=0.0,
    waypoints=[(0, 0), (29, 14)],
    shape=DELTA_TRIANGLE,
    rotate_with_heading=True,
))

# Stationary objects (single waypoint = never moves)
# (15, 7) sits on the traveler's diagonal path — will collide around t=17
for pos in [(5, 10), (15, 7), (22, 12), (10, 3), (25, 11)]:
    sim.entities.append(Entity(
        id=f"tower_{pos[0]}_{pos[1]}",
        symbol="O",
        size=1,
        speed=1.0,
        spawn_time=0.0,
        waypoints=[pos],
    ))

# Step one tick at a time; print at t=0 and whenever something changes or collides
last_collision_ids: set[frozenset[str]] = set()
print(sim.render())
print()

while sim.current_time < 35:
    sim.step()
    collisions = sim.get_collisions()
    collision_ids = {frozenset([c.entity_a, c.entity_b]) for c in collisions}
    if collision_ids != last_collision_ids or sim.tick_count % 5 == 0:
        print(sim.render())
        print()
    last_collision_ids = collision_ids
