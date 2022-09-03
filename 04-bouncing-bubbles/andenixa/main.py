import sys
from dataclasses import dataclass
from pathlib import Path


try:
    import wclib
except ImportError:
    # wclib may not be in the path because of the architecture
    # of all the challenges and the fact that there are many
    # way to run them (through the showcase, or on their own)

    ROOT_FOLDER = Path(__file__).absolute().parent.parent.parent
    sys.path.append(str(ROOT_FOLDER))
    import wclib

from random import gauss, uniform, randint
from typing import List, Optional

import pygame

# This line tells python how to handle the relative imports
# when you run this file directly. Don't modify this line.
__package__ = "04-bouncing-bubbles." + Path(__file__).absolute().parent.name

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
import math
from .utils import *

BACKGROUND = 0x0F1012
NB_BUBBLES = 42
#NB_BUBBLES = 10


class Bubble:
    MAX_VELOCITY = 7

    def __init__(self, position=None):
        self.radius = int(gauss(35, 5))

        if position is None:
            # Default position is random.
            self.position = pygame.Vector2(
                randint(self.radius, SIZE[0] - self.radius),
                randint(self.radius, SIZE[1] - self.radius),
            )
        else:
            self.position = position

        # Set a random direction and a speed of around 3.
        self.velocity = pygame.Vector2()
        self.velocity.from_polar((gauss(3, 0.5), uniform(0, 360)))

        # Pick a random color with high saturation and value.
        self.color = pygame.Color(0)
        h,s,v,a = uniform(0, 360), 80, 100, 100
        self.color.hsva = h,s,v,a        
        self.color_shade = pygame.Color(0)        
        self.color_shade.hsva = h,s,30,a
        self._render_bubble()
        self._start = pygame.time.get_ticks()
        self._ripples = []

    def _render_bubble(self):
        rect = self.get_rect()
        rect.inflate_ip(5, 5)
        self._image = pygame.Surface(rect[2:])
        self._image.set_colorkey((0,0,0))
        r = self._image.get_rect()
        pygame.draw.circle(self._image, self.color, r.center, self.radius)
        pygame.draw.circle(self._image, self.color_shade, r.center, self.radius-2)
        w1, h1 = self._image.get_size()

        mask = pygame.mask.from_surface(self._image).to_surface().convert_alpha()
        s1 = self._image.copy()        
        h,s,v,a = self.color.hsva
        sh1 = pygame.Color(0)
        sh1.hsva = h,s,55,a
        sh2 = pygame.Color(0)
        sh2.hsla = h,s,90,a
        pygame.draw.circle(s1, sh2, r.inflate(-r.width//2, -r.height//2).move(r.centerx,0)[:2], self.radius//5)
        pygame.draw.circle(s1, sh1, r.inflate(-r.width//2, -r.height//2).move(r.centerx,0)[2:], self.radius//2)
        s1 = pygame.transform.smoothscale(s1, (w1//6,h1//6))
        s1 = pygame.transform.smoothscale(s1, (w1, h1))
        self._image = pygame.transform.average_surfaces([self._image, s1]).copy()
        self._image.blit(mask, (0,0), special_flags=pygame.BLEND_RGBA_MULT)

    
    def get_timer(self):
        return pygame.time.get_ticks() + self._start
    
    @property
    def mass(self):        
        return self.radius ** 2

    def add_ripple(self, v):
        self._ripples.append((v, pygame.time.get_ticks()))

    def draw(self, screen: pygame.Surface):     
        ticks = pygame.time.get_ticks()
        ripple = pygame.Vector2(0,0)
        r = self._image.get_rect(center=self.position)
        for r_v, r_st in self._ripples:
            l = r_v.length()
            t = ((ticks - r_st)*.5)
            if t < 1:
                t = 1
            ripple += r_v.normalize().rotate(ticks*l) / t
            
        self._ripples = [ripl for ripl in self._ripples if (ticks - ripl[1])<5000]

        if ripple:
            ripple = ripple.normalize()
            ripple.scale_to_length(self.radius//5)
            
            pulse = ripple
            r = r.inflate(pulse.x,pulse.y)
            img = pygame.transform.scale(self._image, r[2:])
            screen.blit(img, r)
        else:
            screen.blit(self._image, r)

    def move_away_from_mouse(self, mouse_pos: pygame.Vector2):
        """Apply a force on the bubble to move away from the mouse."""
        bubble_to_mouse = mouse_pos - self.position
        distance_to_mouse = bubble_to_mouse.length()
        if 0 < distance_to_mouse < 200:
            strength = chrange(distance_to_mouse, (0, 200), (1, 0), power=2)
            self.velocity -= bubble_to_mouse.normalize() * strength

    def move(self):
        """Move the bubble according to its velocity."""
        # We first limit the velocity to not get bubbles that go faster than what we can enjoy.
        if self.velocity.length() > self.MAX_VELOCITY:
            self.velocity.scale_to_length(self.MAX_VELOCITY)

        self.position += self.velocity
        debug.vector(self.velocity, self.position, scale=10)

    def get_rect(self):
        v = self.radius, self.radius
        r = pygame.Rect(*(self.position-v), self.radius*2, self.radius*2)
        return r

    def collide_borders(self):
        # The first challenge is to make the bubbles bounce against the border.
        # Hover that doesn't mean that a bubble must always be completely inside of the screen:
        # If for instance it spawned on the edge, we don't want it to teleport so that it fits the screen,
        # we want everything to be *smooooth*.
        #
        # To be sure it is smooth, a good rule is to never modify self.position directly,
        # but instead modify self.velocity when needed.
        #
        # The second golden principle is to be lazy and not do anything if the collision will
        # resolve itself naturally in a few frames, that is, if the bubble is already moving
        # away from the wall.

        r = self.get_rect()
        collided = pygame.Vector2(r.clamp(pygame.Rect(0,0,*SIZE)).topleft) - r.topleft
        if collided:            
            h_norm = pygame.Vector2(collided[0], 0)            
            v_norm = pygame.Vector2(0, collided[1])
            if v_norm and math.copysign(self.velocity.y, v_norm.y)!=self.velocity.y:
                self.velocity.reflect_ip(v_norm)
            if h_norm and math.copysign(self.velocity.x, h_norm.x)!=self.velocity.x:
                self.velocity.reflect_ip(h_norm)

    def collide(self, other):
        """Get the collision data if there is a collision with the other Bubble"""
        if self.position.distance_to(other.position)<(self.radius + other.radius):        
            center = self.position.lerp(other.position, self.radius / (other.radius + self.radius))
            normal = self.position - other.position
            return Collision(self, other, center, normal)
            
        return None


# The second challenge contains two parts.
# The first one is to generate a list of all the collisions
# between bubbles.
# The data for a collision is stored into the Collision class below,
# and is generated by the Bubble.collide method above.
# The second part is then to process those collision data, and resolve them.


@dataclass
class Collision:
    """
    The data of a collision consist of four attributes.

    [first] and [second] are the the two objects that collided.
    [center] is the collision point, that is, the point from which you
        would like to push both circles away from. It corresponds to the center
        of the overlapping area of the two moving circles, which is also the
        midpoint between the two centers.
    [normal] is the axis along which the two circles should bounce. That is,
        if two bubbles move horizontally they bounce against the vertical axis,
        so normal would be a vertical vector.
    """

    first: "Bubble"
    second: "Bubble"
    center: pygame.Vector2
    normal: pygame.Vector2

    def resolve(self):
        """Apply a force on both colliding object to help them move out of collision."""
        
        # The second part of the Ambitious challenge is to resolve the collisions that we have collected.
        # (See below in World.logic for how all this is put together).

        # TODO: Resolve the collision.
        # Resolving a collision, here, means to modify the velocity of the two bubbles
        # so that they move out of collision. Not necessarly in one frame, but if
        # they move away from each other for say 2-5 frames, the collision will be resolved.

        # To do so, add a force to the velocity of each bubble to help the two bubbles to separate.
        # The separating force is perpendicular to the normal, similarly to how bubbles bounce
        # against a wall: only the part of the velocity perpendicular to the wall is reflected.
        # Keep in mind that one bubble an have multiple collisions at the same time.
        # You may need to define extra methods.
        # If you have troubles handling the mass of the particles, start by assuming they
        # have a mass of 1, and then upgrade your code to take the mass into account.
        
        m1m2 = self.first.mass + self.second.mass
        f_contrib = self.first.mass / m1m2
        s_contrib = self.second.mass / m1m2

        testa = self.first.position - self.center
        testb = self.second.position - self.center

        reflecta = self.first.velocity.reflect(self.normal)
        reflectb = self.second.velocity.reflect(self.normal)

        mg1 = self.first.velocity.length() +  self.second.velocity.length()
        
        f1 = self.normal.normalize() * reflecta.length()
        f2 = -self.normal.normalize() * reflectb.length()
        self.first.velocity = (self.first.velocity*f_contrib+reflecta*s_contrib) - f2*s_contrib 
        self.second.velocity = (self.second.velocity*s_contrib+reflectb*f_contrib) - f1*f_contrib 
        self.first.add_ripple(f2*s_contrib)
        self.second.add_ripple(f1*f_contrib )
        mg2 = self.first.velocity.magnitude() +  self.second.velocity.magnitude()

        lost = mg1 - mg2
        if lost>0:
            self.first.velocity.scale_to_length(self.first.velocity.length()+lost/2)
            self.second.velocity.scale_to_length(self.second.velocity.length()+lost/2)




# The world is a list of bubbles.
class World(List[Bubble]):
    def __init__(self, nb):
        super().__init__(Bubble() for _ in range(nb))
        self._connected = set()

    def logic(self, mouse_position: pygame.Vector2):
        """ Handles the collision and evolution of all the objects. """

        # Second part of the ambitious challenge is to make the algorithm that solves the collisions.
        # A part of it is already provided so that you can focus on the important part.

        # We start by moving the bubbles and do the collisions with the static objects, the walls.
        for bubble in self:
            bubble.move()
            bubble.collide_borders()
            #bubble.move_away_from_mouse(mouse_position)

        # Then we check each pair of bubbles to collect all collisions.
        collisions = []
        for i, b1 in enumerate(self):
            for b2 in self[i + 1 :]:
                collision = b1.collide(b2)
                connected = (b1, b1) in self._connected
                if collision:
                    if not connected:
                        collisions.append(collision)
                        self._connected.add((b1, b1))
                elif connected:
                    self._connected.remove((b1, b1))
                

        # And finally we resolve them all at once, so that it doesn't impact the detection of collision.
        for collision in collisions:
            collision.resolve()

    def draw(self, screen):
        for bubble in self:
            bubble.draw(screen)


def mainloop():
    pygame.init()

    world = World(NB_BUBBLES)

    mouse_position = pygame.Vector2()

    fps_counter = FpsCounter(60, Bubbles=world)
    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.MOUSEMOTION:
                mouse_position.xy = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                world.append(Bubble(event.pos))
            debug.handle_event(event)
            fps_counter.handle_event(event)

        # Handle the collisions
        world.logic(mouse_position)
        fps_counter.logic()

        # Drawing the screen
        screen.fill(BACKGROUND)
        world.draw(screen)
        fps_counter.draw(screen)
        debug.draw(screen)


# ---- Recommended: don't modify anything below this line ---- #
if __name__ == "__main__":
    try:
        # Note: your editor might say that this is an error, but it's not.
        # Most editors can't understand that we are messing with the path.
        import wclib
    except ImportError:
        # wclib may not be in the path because of the architecture
        # of all the challenges and the fact that there are many
        # way to run them (through the showcase, or on their own)
        ROOT_FOLDER = Path(__file__).absolute().parent.parent.parent
        sys.path.append(str(ROOT_FOLDER))
        import wclib

    wclib.run(mainloop())

