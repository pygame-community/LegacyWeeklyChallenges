# 04 — Bouncing Bubbles

The goal of this challenge is to make bubbles that bounce gracefully around the screen.

This is meant as an introduction to elastic collisions and physics in python and pygame.
Circle collisions are the simplest type of general collision that one can solve in
an elegant way.

### Setup

The setup code in [`base/`](./base) contains a two classes, `Bubble` and `World`,
that together simulate a world full of circle. Those circles don't collide against each other,
and neithers against the side of the screen. Your challenge will be to add glitchless collisions.

There are no provided assets, we only need `pygame.draw.circle` this time!

The setup can be controlled with the mouse: 
 - Bubbles tend to go away from the mouse.
 - Bubbles spawn when the mouse is clicked.
And techincal info can be toggled with:
 - `D` for the debug
 - `U` for unlimited FPS
 - `F` to show/hide the FPS

### Achievements

- Casual `+3 CP`: Make the bubbles collide glitchless against the walls.
- Ambitious `+2 CP`: Make the bubbles collide against each other.
- Adventurous `+1 CP`: Add moving rectangles that also collide with everything.

For each challenge, it is required that it is impossible to make a bubble teleport,
even if it spawns half into another bubble or a wall.
Bubbles should also not glitch or jitter.
In such case, no points will be given, but check the [tips below](#tips),
the tips inside the provided code or ask on the pygame server, and you will
find answers ;)

Further instructions and more general tips are [available on this document](../general_instructions.md).

In any case, remember to always try to make things as reusable as possible,
who knows, you may need it in a future project!

### Tips

**Tip 1**: If you want to be sure that a bubble never teleports, never set its `x` and `y`
    coordinates directly, modify only its velocity. 

**Tip 2**: To avoid most glitches, you can allow bubbles to overlap a bit for a few frames,
    and when two bubble do overlap, you apply a strong force on each one that separates them,
    that is, a force that is on the oposite direction of the collision.

**Tip 3**: Think about how balls collide in real life: they don't go instantly in the other direction,
    they overlap (or more likely, compress/squeeze) a bit.

**Tip 4**: For an explanation of elatic collisions and some formulas, you can read the 
    [wikipedia page](https://en.wikipedia.org/wiki/Elastic_collision).

**Tip 4**: If two objects collide, but already have velocities that pushes them in opposite directions,
    don't do anything !


Have fun !

### Credits

 - Setup code: [CozyFractal](https://cozyfractal.com)
