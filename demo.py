from simulation import Entity, Simulation

sim = Simulation(width=30, height=10, tick_size=1.0)

sim.entities.append(Entity(
    id="traveler",
    symbol="X",
    size=1,
    speed=1.0,
    spawn_time=0.0,
    waypoints=[(29, 5), (0, 5)],
))

# Show every 4 ticks across the 29-unit journey
for _ in range(8):
    print(sim.render())
    print()
    for _ in range(4):
        sim.step()

# Show final resting position
print(sim.render())
