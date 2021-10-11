# 02 — Particle System

The goal of this challenge is to implement general and reusable particle system for your games.

Particles are a very good way to add feedback and interactivity to a game, 
so it is very handy to have a system already implemented for when a game jam comes.

### Achievements

 Description of the different levels and the amount of 
`C`hallenger `P`oints they provide:

- Casual `+3 CP`: Have 3 different particle effects of your choice in the game 
    (for instance: asteroid explosion, ship damage, thrusters, stars, asteroids clear fireworks, bullets, warning as approaching asteroids...)
- Ambitious `+2 CP`: Have 6 different particles effects and handle 1000 particles at 60 FPS
- Adventurous `+1 CP`: Have 9 effects

In any case, your particle system should be:
- independent of the rest of your code (for instance, in it own file) 
   so that you can copy/paste it in your other projects
- run at 60 FPS, at least, so that there is still processing power for the rest of a real game
- Generic, so that you can create new particle effect without too much effort.

### Setup

The setup code in [`base/`](./base) consists of a simple top down game with trees and ghosts moving around.
To get started, duplicate the whole `base` folder and rename the copy with your username
(will call it `yourname/` from now on). All your modifications should be inside the `yourname/` folder,
otherwise it would be impossible to have a showcase of all the submissions.

Have fun !

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
