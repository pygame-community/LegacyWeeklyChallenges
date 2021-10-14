# 02 — Particle System

The goal of this challenge is to implement general and reusable particle system for your games.

Particles are a very good way to add feedback and interactivity to a game, 
so it is very handy to have a system already implemented for when a game jam comes.

### Achievements

 Description of the different levels and the amount of 
`C`hallenger `P`oints they provide:

- Casual `+3 CP`: Have 3 different particle effects of your choice in the game
- Ambitious `+2 CP`: Have the asteroids break in pieces that together make up the original sprite,
  in a somewhat "realistic" way.
- Adventurous `+1 CP`:
  Have a reusable system that can handle a thousand particles at 60 FPS
  with three of the following features (you choose!):
    - Transparency
    - Images as well as drawn particles
    - Change colors overtime with multistep gradients
    - Particle physics (colliding against walls, asteroids, ...)
    - Ability to spawn a burst of particles but also spawn some over time
    - A cool feature of your choice (mention it in the description of your entry!)

In any case, your particle system should strive to be:
- independent of the rest of your code (for instance, in it own file) 
   so that you can copy/paste it in your other projects
- run at 60 FPS, at least, so that there is still processing power for the rest of a real game
- Generic, so that you can create new particle effect without too much effort.

### Setup

The setup code in [`base/`](./base) consists of a simple Asteroids clone with a ship that moves around and fires on asteroids.
The code is a bit more complex than last time, so here's an overview.

- [`main.py`](./base/main.py) contains basic boilerplate, with every method delegated to a `State` object.
- [`objects.py`](./base/objects.py) contains many things:
  - The `State` class, that represent everything in the game. It is probably the place were you will 
      want to create your particle system / particle manager. This class contains all the `Object`s of the game,
      and is accessible from any object as `obj.state`. In order to add an object to the state, use `state.add(new_object)`,
      it will then be drawn and updated each frame automatically. Objects are removed from the state when `obj.alive == False`.
      If you do not use a particle manager, you can add your particles directly to the state as with other objects.
  - The `Object` class, base class of all objects of the game (`Player`, `Asteroid`, `Bullet`). It takes care of 
      drawing correctly the rotated sprites, detecting collisions and moving objects according to their velocity.
      You probably don't need to modify it.
  - The `Player` class implements event handling and firing. It contains a `on_asteroid_collision()`
      method that is called whenever the ship collides with an asteroid. It is a good place to add particles.
      An other good place is `Player.logic()` to emit particles every frame.
  - The `Asteroid` class dispatches the collision with other objects and manages its own explosion.
      The `explode` method is a nice place to add particles.
  - The `Bullet` class doesn't do much, except dying after a given time.
  - The `FpsCounter` class is a wrapper around `pygame.time.Clock` so it manages the FPS but also 
      displays them. You can toggle the display with the `F` key.

To get started, **duplicate** the whole `base` folder and rename the copy with your username
(we will call it `yourname/` from now on). All your modifications should be inside the `yourname/` folder,
otherwise it would be impossible to have a showcase of all the submissions.

> PLEASE. Do not modify the base folder.

Further instructions are 

Have fun !

### Tips

**Tip 1**: If you are struggling to find places to add particles, here are a few, but there are countless others!
> asteroid explosion, ship damage, thrusters, stars, asteroids clear fireworks, bullets, warning as approaching asteroids...

**Tip 2**: You can remove completely the code with the asteroids if you want to, it is there only to sparkle your 
creativity. If you want to, you can just create a "particle showcase" with lots of nice handcrafted effects going on at the same time.
I strongly suggest this option if you have not used object-oriented programming before, as the setup code make heavy use of it.
However, this challenge is a good chance to get more familiar with OOP.

**Tip 3**: If you have never made particles before, don't start by making something generic.
Make something specific, then think about how you could make it more reusable. 
Usable comes first, reusable comes second.

**Tip 4**: If you have already made a particle system before, make a new one! 
Try to make it better, or explore other concepts, the possibilities are endless ;)

### Credits

 - Asteroids: [Asteroids 02 by GameArtForge](https://opengameart.org/content/asteroids-set-02)
 - Other sprites: [Flyre by CozyFractal](https://gitlab.com/ddorn/flyre)
 - Setup code: [CozyFractal](https://cozyfractal.com)

### Legal stuff

By submitting your game, you agree that we add its code to the repository 
and that it can be:
- used (for instance in the showcase), 
- modified (for instance to work with a future version of the showcase),
- shared (for instance as a mean to illustrate the capabilities of pygames).

But all those uses must be for the good of the community, and never for any individual.
This concerns for instance any profits that could be made: they have to be used for the 
benefit of the whole community.
