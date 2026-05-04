import math
from typing import Optional
from pydantic import BaseModel

# Delta triangle pointing right (+x): nose, body, upper-rear wing, lower-rear wing
DELTA_TRIANGLE: list[tuple[int, int]] = [(1, 0), (0, 0), (-1, 1), (-1, -1)]


class Entity(BaseModel):
    id: str
    symbol: str
    size: int = 1
    speed: float
    spawn_time: float = 0.0
    waypoints: list[tuple[float, float]]
    shape: list[tuple[int, int]] | None = None
    rotate_with_heading: bool = False

    def position_at(self, time: float) -> Optional[tuple[float, float]]:
        if time < self.spawn_time or not self.waypoints:
            return None
        elapsed = time - self.spawn_time
        accumulated = 0.0
        for i in range(len(self.waypoints) - 1):
            x0, y0 = self.waypoints[i]
            x1, y1 = self.waypoints[i + 1]
            dist = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
            seg_dur = dist / self.speed
            if elapsed <= accumulated + seg_dur:
                frac = (elapsed - accumulated) / seg_dur if seg_dur > 0 else 1.0
                return (x0 + frac * (x1 - x0), y0 + frac * (y1 - y0))
            accumulated += seg_dur
        return self.waypoints[-1]

    def heading_at(self, time: float) -> float:
        if len(self.waypoints) < 2:
            return 0.0
        elapsed = max(0.0, time - self.spawn_time)
        accumulated = 0.0
        for i in range(len(self.waypoints) - 1):
            x0, y0 = self.waypoints[i]
            x1, y1 = self.waypoints[i + 1]
            dist = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
            seg_dur = dist / self.speed
            if elapsed <= accumulated + seg_dur:
                return math.atan2(y1 - y0, x1 - x0)
            accumulated += seg_dur
        x0, y0 = self.waypoints[-2]
        x1, y1 = self.waypoints[-1]
        return math.atan2(y1 - y0, x1 - x0)

    def is_active(self, time: float) -> bool:
        return time >= self.spawn_time and bool(self.waypoints)

    def footprint(self, time: float) -> set[tuple[int, int]]:
        pos = self.position_at(time)
        if pos is None:
            return set()
        cx, cy = round(pos[0]), round(pos[1])

        if self.shape is not None:
            offsets = self.shape
            if self.rotate_with_heading:
                angle = self.heading_at(time)
                cos_a, sin_a = math.cos(angle), math.sin(angle)
                offsets = [
                    (round(dx * cos_a - dy * sin_a), round(dx * sin_a + dy * cos_a))
                    for dx, dy in offsets
                ]
        else:
            r = range(-(self.size // 2), (self.size + 1) // 2)
            offsets = [(dx, dy) for dx in r for dy in r]

        return {(cx + dx, cy + dy) for dx, dy in offsets}


class Collision(BaseModel):
    entity_a: str
    entity_b: str
    cells: list[tuple[int, int]]


class Simulation(BaseModel):
    width: int = 40
    height: int = 20
    tick_size: float = 1.0
    current_time: float = 0.0
    tick_count: int = 0
    entities: list[Entity] = []

    def step(self) -> None:
        self.current_time += self.tick_size
        self.tick_count += 1

    def get_collisions(self) -> list[Collision]:
        footprints = {e.id: e.footprint(self.current_time) for e in self.entities}
        collisions: list[Collision] = []
        ids = list(footprints.keys())
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                a, b = ids[i], ids[j]
                overlap = footprints[a] & footprints[b]
                if overlap:
                    collisions.append(Collision(
                        entity_a=a,
                        entity_b=b,
                        cells=sorted(overlap),
                    ))
        return collisions

    def render(self) -> str:
        grid: list[list[str]] = [["." for _ in range(self.width)] for _ in range(self.height)]
        collision_cells: set[tuple[int, int]] = set()

        collisions = self.get_collisions()
        for c in collisions:
            collision_cells.update(c.cells)

        for entity in self.entities:
            for gx, gy in entity.footprint(self.current_time):
                row = self.height - 1 - gy
                if 0 <= gx < self.width and 0 <= row < self.height:
                    grid[row][gx] = "!" if (gx, gy) in collision_cells else entity.symbol

        lines: list[str] = [f"t={self.current_time:.1f}  tick={self.tick_count}"]
        if collisions:
            for c in collisions:
                lines.append(f"  COLLISION: {c.entity_a} x {c.entity_b} at {c.cells}")

        y_label_width = len(str(self.height - 1)) + 1
        for row_idx, row in enumerate(grid):
            y_val = self.height - 1 - row_idx
            lines.append(f"{y_val:{y_label_width}d} |" + "".join(row))

        lines.append(" " * y_label_width + " +" + "-" * self.width)

        x_label = " " * (y_label_width + 2)
        col = 0
        while col < self.width:
            marker = str(col)
            x_label += marker
            next_col = col + 5
            if next_col < self.width:
                x_label += " " * (5 - len(marker))
            col = next_col
        lines.append(x_label)

        return "\n".join(lines)
