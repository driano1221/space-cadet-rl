# Instrumentation layer

These are the files added to the
[decompilation](https://github.com/k4zmu2a/SpaceCadetPinball) to turn the game
into an RL environment. They are kept here as a readable copy; the buildable
fork lives at
[driano1221/SpaceCadetPinball, branch `rl-instrumentation`](https://github.com/driano1221/SpaceCadetPinball/tree/rl-instrumentation).

| File | What it does |
|---|---|
| `rlenv.h` / `rlenv.cpp` | runs the game on its own thread with a step handshake, and exposes the state struct |
| `rlevents.h` | counters incremented inside the game's own controllers |
| `pymodule.cpp` | pybind11 bindings |

## The three entry points that mattered

Finding these took the longest, and they are not obvious from the outside:

```cpp
pb::frame(float dt)                 // one physics step, no rendering
MainTable->Message(MessageCode::LeftFlipperInputPressed, pb::time_now)
TPinballTable::CurScore             // score, public, no accessor in the way
```

`kPassoMs = 1000.0f / 120.0f`: the physics runs at 120 Hz. The Python side
groups three frames per decision, so the agent acts at 40 Hz. Assuming 40 Hz for
the physics itself produces rates that are wrong by a factor of three, which
cost a day of misreported numbers.

## Two traps in the original code

`TBall::ActiveFlag` does **not** mean "ball in play". It toggles on every
collision step, and filtering by it silently discards two thirds of the samples.

The table's screen projection is a 3D perspective, not linear. Converting world
coordinates to pixels with a proportion is wrong; `proj::xform_to_2d` is the
function that does it correctly.

## Event counters

`ev_flip_acerto` is worth a note. It counts a flipper **in motion** touching the
ball, taken from `collisionFlag` inside `TFlipper::FlipperCollision`. Because
that function only runs with a non-zero `deltaAngle`, holding a flipper up never
produces the event.

The alternative, inferring strikes from a jump in ball speed, was measured
against random instants and came out at 1.15x chance: noise. Any bumper
accelerates the ball too.
