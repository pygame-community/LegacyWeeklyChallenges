import math
import random
import sys
from pathlib import Path
from random import random as rnd

from pygame import Vector2
from pygame.key import get_pressed

try:
    import wclib
except ImportError:
    # wclib may not be in the path because of the architecture
    # of all the challenges and the fact that there are many
    # way to run them (through the showcase, or on their own)

    ROOT_FOLDER = Path(__file__).parent.parent.parent
    sys.path.append(str(ROOT_FOLDER))
    import wclib

# This line tells python how to handle the relative imports
# when you run this file directly.
__package__ = "02-particle-system." + Path(__file__).parent.name

# ---- Recommended: don't modify anything above this line ---- #

# Metadata about your submission
__author__ = "andenixa#2251"  # Put yours!
__achievements__ = [  # Uncomment the ones you've done
    # "Casual",
    "Ambitious",
    # "Adventurous",
]

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
# noinspection PyPackages
from .objects import *
from .particles import *
from .utils import font, text

BACKGROUND = 0x0F1012


class Cracklet:
    """Cracks propogation"""

    __slots__ = "rect", "points", "angle", "size", "_angle_random", "_is_done"

    def __init__(self, pos, angle, rect, size=7, angle_random=7):
        self.rect = rect
        self.points = [pygame.Vector2(pos)]
        self.angle = angle
        self.size = size
        self._is_done = False
        self._angle_random = angle_random

    def is_done(self):
        pt = self.points[-1]
        return self._is_done or not self.rect.collidepoint(pt)

    def stop(self):
        self._is_done = True

    def propagate(self):
        last_p = self.points[-1]
        rnd_add = min(len(self.points) * 15, 45)
        step = pygame.Vector2(self.size + random.randint(-self.size // 2, self.size // 2)).rotate(
            self.angle + random.randint(-self._angle_random - rnd_add, self._angle_random + rnd_add)
        )
        # step = pygame.Vector2(10).rotate(self.angle)
        step = last_p + step
        self.points += [step]


class AsteroidEx(Asteroid):
    _blinky_color = [
        (127, 127, 113),
        (119, 118, 101),
        (93, 93, 77),
        (55, 55, 44),
        (15, 15, 12),
        (0, 0, 0),
        (41, 41, 29),
        (143, 142, 96),
        (242, 202, 97),
        (226, 179, 85),
        (79, 60, 28),
        (2, 2, 0),
        (149, 100, 47),
        (248, 157, 73),
        (65, 38, 17),
        (44, 24, 11),
        (226, 77, 30),
        (64, 21, 8),
        (62, 20, 8),
        (178, 56, 21),
        (0, 0, 0),
        (156, 45, 17),
        (18, 5, 1),
        (113, 29, 10),
    ]

    def __init__(self, pos, vel, size_or_surf=3, color=None):
        if isinstance(size_or_surf, int):
            size = min(3, size_or_surf)
            super().__init__(pos, vel, size, color)
        elif isinstance(size_or_surf, pygame.Surface):
            Object.__init__(self, pos, vel, size_or_surf)
            self.color = color
        else:
            raise TypeError("size_or_surf has to be int or Surface")

    def explode(self, bullet):
        asteroid = self.rotated_sprite
        asteroid_rect = asteroid.get_rect()
        bullet_mask = pygame.mask.from_surface(bullet.rotated_sprite)
        asteroid_mask = pygame.mask.from_surface(self.rotated_sprite)
        self_xy = self.center - asteroid_rect.center
        bullet_xy = bullet.center - bullet.rotated_sprite.get_rect().center

        overlap = asteroid_mask.overlap(bullet_mask, bullet_xy - self_xy)
        if not overlap:
            return

        b_angle = bullet.vel.as_polar()[1] - 45  # I have no idea why it tilted but it is

        a_rect = asteroid_rect
        asteroid_x, asteroid_y = self_xy

        collision_point = Vector2(overlap)
        try:
            collision_point -= collision_point.normalize() * 5
        except ValueError:
            pass

        cracks = generate_cracks(collision_point, asteroid_rect, p_angle=b_angle)
        if not cracks:
            return

        colorkey = asteroid.get_colorkey()
        asteroid1 = asteroid.copy().convert()
        asteroid1.set_colorkey((0, 0, 0))

        self.state.particle_man.spawnMany(
            40,
            self_xy + collision_point,
            bullet.vel.dot(self.vel) * 3,
            350,
            Particles.TYPE_SIMPLE,
            spawn_cb=impact_cb,
        )
        self.state.particle_man.spawnMany(
            20,
            self_xy + collision_point,
            bullet.vel.dot(self.vel) * 3,
            450,
            Particles.TYPE_SIMPLE,
            spawn_cb=impact_cb,
            color=self._blinky_color,
        )
        self.state.particle_man.spawnMany(
            sum(asteroid_rect.size) // 2,
            self.center,
            self.vel,
            150,
            Particles.TYPE_SNOWFLAKE,
            spawn_cb=lambda p: asteroid_explosion(p, self),
            color=(
                (255, 254, 226),
                (255, 254, 164),
                (255, 213, 103),
                (252, 128, 58),
                (229, 78, 31),
                (125, 30, 10),
            ),
        )

        asteroid.set_colorkey((1, 0, 0, 255))

        # render asteroid cracks
        cicrle = pygame.draw.circle
        c_center = pygame.Vector2(cracks[0].points[0])
        kuroi = (0, 0, 0)
        for _ in range(3):
            cicrle(asteroid1, kuroi, c_center, int(5 + rnd() * 3))
            c_center += (2 - rnd() * 4, 2 - rnd() * 4)

        for crack in cracks:
            for i in range(len(crack.points)):
                if i == 0:
                    continue
                pygame.draw.line(
                    asteroid1, (0, 0, 0), crack.points[i - 1], crack.points[i], width=2
                )

        asteroid.set_colorkey(colorkey)
        m = pygame.mask.from_surface(asteroid1)

        for (shard_img, shard_mask, r) in break_surface(asteroid, m):
            mm_count = shard_mask.count()
            ratio = mm_count / m.count()
            sh_speed = pygame.Vector2(
                (
                    (r.centerx - a_rect.centerx) * (1 - ratio),
                    (r.centery - a_rect.centery) * (1 - ratio),
                )
            )
            sh_speed += bullet.vel * 4
            sh_pos = pygame.Vector2((asteroid_x + r.x, asteroid_y + r.y))
            # if bigger than a size of smallest astroid
            if mm_count > 840:
                self.state.add(
                    AsteroidEx(
                        sh_pos + shard_img.get_rect().center, sh_speed / 15, shard_img, self.color
                    )
                )
            else:
                self.state.particle_man.spawn(
                    sh_pos,
                    sh_speed,
                    800 + rnd() * 150,
                    p_type=Particles.TYPE_SPRITE,
                    surf=shard_img,
                    color=(255, 255, 255),
                    torque=random.randint(-15, 16),
                )

        bullet.alive = False
        self.alive = False


class FpsCounterEx(FpsCounter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._text_color = "#89C4F4"
        self._particles_t = text("Particles:", self._text_color)
        self._particles_t_w = self._particles_t.get_size()[0]
        self._part_t_pos = self.center + (0, 25)

    @staticmethod
    @lru_cache(maxsize=5000, typed=False)
    def text2(txt, color, size=20, font_name=None):
        """Render a text on a surface."""
        return font(size, font_name).render(txt, False, color)

    def draw(self, screen):
        if self.hidden:
            return
        particle_count_t = self.text2("%d" % self.state.particle_man.count(), self._text_color)
        t_pos = self._part_t_pos
        screen.blit(self._particles_t, t_pos)
        screen.blit(particle_count_t, t_pos + (self._particles_t_w + 8, 0))
        super().draw(screen)


def generate_cracks(
    st_point,
    bounding_rect,
    max_cracks=7,
    crack_len=7,
    p_angle=None,
    angle_proclivity=1.0,
    new_crack_chance=15,
    chance_to_split=50,
    cracks_spread=90,
):
    """
    st_point - starting point
    bounding_rect - bounding rect for cracks propogation
    crack_len - average size of a crack line
    p_angle - if specified, preferred angle for crack formation
    angle_proclivity - tendency to follow p_angle with 0 - little tendency, 1.0 - maxmum tendency
    new_crack_chance - change to form an extra crack at every step
    chance_to_split - chance to split a crack in two (stopping the old one)
    cracks_spread - angle randomisation for cracks (-+)
    """
    cracks = []

    if p_angle is not None:
        if p_angle < 0:
            p_angle += 360
        p_angle %= 360

        pr = int(36 * (2.0 - angle_proclivity))

        for i in range(max_cracks * 2):
            angle = rnd() * 360
            if (100 - abs(angle - p_angle) // pr) > (rnd() * 100):
                cracks += [Cracklet(st_point, angle, bounding_rect, size=crack_len)]
            if len(cracks) > max_cracks:
                break
    else:
        for i in range(max_cracks):
            angle = rnd() * 360
            cracks += [Cracklet(st_point, angle, bounding_rect, size=crack_len)]
    while True:
        done = True
        new_cracks = []
        for crack in cracks:
            crack.propagate()
            if crack.is_done():
                continue
            else:
                done = False
            if new_crack_chance > (rnd() * 100):
                pt = crack.points[-1]
                angle_add = (cracks_spread // 2) - (rnd() * cracks_spread)
                new_cracks += [
                    Cracklet(pt, crack.angle + angle_add, bounding_rect, size=(crack_len - 2))
                ]
                if chance_to_split > (
                    rnd() * 100
                ):  # 50% chance to kill the old crack, i.e. spl.splitting
                    new_cracks += [
                        Cracklet(
                            pt,
                            crack.angle - angle_add + random.randint(-5, 5),
                            bounding_rect,
                            size=(crack_len - 2),
                        )
                    ]
                    crack.stop()
        if done:
            break
        cracks.extend(new_cracks)

    return cracks


def asteroid_explosion(p, asteroid):
    r = asteroid.rotated_sprite.get_bounding_rect()
    size = max(r.width, r.height) * 0.8
    pos2 = Vector2(rnd() * size).rotate(rnd() * 360)
    p.speed += pos2
    p.pos += pos2
    p.life = int(p.life * (0.5 + rnd()))


def impact_cb(p):
    pos2 = Vector2(rnd() * 5).rotate(rnd() * 360)
    p.speed += pos2 * 3
    p.pos += pos2
    p.life = int(p.life * (0.5 + rnd()))


def break_surface(surf, surf_mask):
    """break a surface to mask connected components"""
    res = []
    for mm, r in zip(surf_mask.connected_components(), surf_mask.get_bounding_rects()):
        shard_img = pygame.Surface(r[2:])
        shard_img.blit(surf, (0, 0), r)
        mms = mm.to_surface()
        mms.set_colorkey((255, 255, 255))
        shard_img.blit(mms, (0, 0), r)
        shard_img.set_colorkey((0, 0, 0))
        res.append((shard_img, mm, r))
    return res


def burner_spawn_cb(p):
    ang = 25 - rnd() * 50
    p.speed.rotate_ip(ang)
    p.speed *= rnd()
    p.life = int(p.life * (0.5 + rnd()))


def burner_spawn_rot_cb(p):
    ang = 25 - rnd() * 50
    p.speed.rotate_ip(ang)
    p.speed *= 1.0 + rnd()
    p.life = int(p.life * (0.5 + rnd()))
    p.torque += ang


# import cProfile
# import line_profiler
# from memory_profiler import profile


def mainloop():
    pygame.init()
    # profiler = cProfile.Profile()
    # profiler = line_profiler.LineProfiler()

    player = Player((SIZE[0] / 2, SIZE[1] / 2), (0, 0))

    fps_counter = FpsCounterEx(60)
    particle_man = Particles(clock=fps_counter.clock, target_fps=fps_counter.target_fps)

    # The state is just a collection of all the objects in the game
    state = State(player, fps_counter, *AsteroidEx.generate_many())
    state.particle_man = particle_man

    # profiler.add_function(particles.spawnMany)
    # profiler.add_function(particles.update)
    # profiler.add_function(SnowFlake.update)
    # profiler.enable()

    is_done = False
    engine_pos = Vector2(35, 0)
    # collided = set()
    frame = 0
    rotation = 0

    fire_colors1 = (
        (255, 254, 226),
        (255, 254, 164),
        (255, 213, 103),
        (252, 128, 58),
        (229, 78, 31),
        (125, 30, 10),
    )
    fire_colors2 = InterpolatedColors(fire_colors1, 50)
    # text_12 = fps_counter.text2("All Will Survive And Prosper", (255,222,100), size=135)

    engine_exhaust = particle_man.addSpawner(
        15, (0, 0), (0, 0), 150, Particles.TYPE_SIMPLE, spawn_cb=burner_spawn_cb, color=fire_colors2
    )
    engine_exhaust_blinky = particle_man.addSpawner(
        150,
        (0, 0),
        (0, 0),
        350,
        Particles.TYPE_SIMPLE,
        spawn_cb=burner_spawn_cb,
        color=AsteroidEx._blinky_color,
    )

    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                is_done = True
            else:
                state.handle_event(event)
            # if event.type==EVT_SPAWN_FIRE:
            # colored text magic
            # if not subrects:
            #     pygame.time.set_timer(EVT_SPAWN_FIRE, 0)
            #     continue
            # subrects = sorted(subrects, key=lambda s: player.center.distance_squared_to(s[1]))
            # (sr, pos, _) = subrects.pop()
            # final_pos = Vector2(pos) + (150,150)
            # spawn_pos = player.center + engine_pos.rotate(90-player.rotation)
            # spawn_vel = Vector2(55,0).rotate(90-player.rotation)
            # s_pos = pygame.Vector2(spawn_pos)

            # spawner = particles.addSpawner(50, s_pos, spawn_vel, 500, p_type=particles.TYPE_SIMPLE, spawn_cb= burner_spawn_cb1, color=fire_colors1)

            # movers.append([spawner, spawner.pos, final_pos, -rnd()*.5])
            #
        # for move in movers[:]:
        #     (spawner, s_pos, final_pos, i) = move
        #     i+=.01
        #     if i>=1:
        #         movers.remove(move)
        #         spawner._spawn_cb=fire_spawner_cb
        #         spawner.vel = pygame.Vector2( (0,-5.0) )
        #         continue
        #     move[3] = i
        #     if i<0:
        #         continue
        #     spawner.pos = s_pos.lerp(final_pos, i)

        # Note: the logic for collisions is in the Asteroids class.
        # This may seem arbitrary, but the only collisions that we consider
        # are with asteroids.
        state.logic()
        particle_man.update()

        screen.fill(BACKGROUND)
        state.draw(screen)
        particle_man.draw(screen)
        # for obj in state.objects:
        #     if isinstance(obj, Bullet):
        #         pygame.draw.line(screen, (255,255,22), obj.center, obj.center + pygame.Vector2(45,0).rotate(obj.vel.as_polar()[1]))

        # rotation = (rotation - player.rotation) * 5
        # print('particles (after update):', particles.count())

        # engine_spawner.pos = spawn_pos
        # engine_spawner.vel = spawn_vel
        pressed = get_pressed()
        raw_acceleration = 0.5 * pressed[pygame.K_DOWN] - pressed[pygame.K_UP]
        engine_exhaust.rate = max(0, 1500 - (1300 * raw_acceleration))
        engine_exhaust.pos = player.center + engine_pos.rotate(90 - player.rotation)
        engine_exhaust.vel = Vector2(55, 0).rotate(90 - player.rotation) * (1 - raw_acceleration)
        engine_exhaust_blinky.pos = engine_exhaust.pos
        engine_exhaust_blinky.vel = engine_exhaust.vel
        # collision code if you please
        # rotation = player.rotation
        # rect = player.rotated_sprite.get_bounding_rect()
        # rect.inflate_ip(-5, -5)
        # rect.center = player.center

        # rect.x = player.center.x - rect.width//2
        # rect.y = player.center.y - rect.height//2
        # for particle in particles.batch:
        #     if (not particle in collided) and rect.collidepoint(particle.pos):
        #         p1, p2 = rect.clipline(*particle.pos, *rect.center)
        #         s1 = Vector2(p1) - Vector2(p2)
        #         #pygame.draw.line(screen, (255,33,122), line[0], line[1],width=2)
        #         particle.speed += player.vel*25
        #         particle.speed += s1 * 10
        #         collided.add(particle)
        # if not frame % 50:rr
        #     collided = set()

        # state.particle_man.draw(screen)

        if is_done:
            break

    # profiler.disable()
    # try:
    #     profiler.print_stats(sort='cumtime')
    # except:
    #     profiler.print_stats()


if __name__ == "__main__":
    wclib.run(mainloop())
