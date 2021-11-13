import pygame as pg
from .buttons import Button
import random
from copy import copy

"""

def func(arg):
    print(arg)


How to use buttons :

in self.buttons list from App class :

Button(
    pos=pg.Vector2 | tuple[int,int] -> pos of the button
    size=tuple[int, int] -> size of the button
    # ------------ OPTIONAL ---------------
    icon=pg.Surface -> icon/image shown instead of drawing a rect
    icon_hover=pg.Surface -> icon/image shown when mouse hovers
    on_click=func -> func executed when click happens
    on_click_args="single_click" -> arg passed to the on click func (can be a tuple of arguments)
    on_mouse_hover-> same from "on_click" but when the mouse hovers the button
    on_mouse_hover_args:tuple -> same from "on_click" but when the mouse hovers the button
    font:pg.font.Font -> font for the text
    text:str -> text displayed on the button
    text_color:tuple -> default text color
    text_color_hover:tuple -> text color when mouse hovers button
    bg_color:tuple -> default background color
    bg_color_hover:tuple -> background color when hoverd by the mouse
    double_click:bool -> allow double click
    db_click_func -> func played when double click
    db_click_f_args:tuple -> args of func double click
    border_radius:int -> border radius if needed (round the corner)
    shadow_on_click:int -> feels like the button is really pressed
    execute="down" -> can either be "down" or "up" -> decides when it does execute the func (on mousebuttondown or mousebuttonup)
                 
)

"""


class App:

    def __init__(self):

        self.canvas = pg.Surface((500, 500))
        self.snake = Snake(self.canvas)

        self.buttons = [
            Button(
                pos=pg.Vector2(1024//2-250+50, 768//2-250-100-5),
                size=(500, 80),
                bg_color=(80,60,129),
                bg_color_hover=(69,47,88),
                text="UP",
                font=pg.font.Font("regular.ttf", 25),
                text_color=(255, 255, 255),
                text_color_hover=(200, 200, 200), 
                on_click=self.snake.move_direction,
                on_click_args="up",
                shadow_on_click=2,
                db_click_func=self.snake.db_click,
                db_click_f_args="up",
                border_radius=8
            ),
            Button(
                pos=pg.Vector2(1024//2-250+50,768//2+250+20),
                size=(500, 80),
                bg_color=(80,60,129),
                bg_color_hover=(69,47,88),
                text="DOWN",
                font=pg.font.Font("regular.ttf", 25),
                text_color=(255, 255, 255),
                text_color_hover=(200, 200, 200), 
                on_click=self.snake.move_direction,
                on_click_args="down",
                shadow_on_click=2,
                db_click_func=self.snake.db_click,
                db_click_f_args="down",
                border_radius=8
            ),
            Button(
                pos=pg.Vector2(1024//2-250-25-50, 768//2-250),
                size=(100, 500),
                bg_color=(80,60,129),
                bg_color_hover=(69,47,88),
                text="LEFT",
                font=pg.font.Font("regular.ttf", 25),
                text_color=(255, 255, 255),
                text_color_hover=(200, 200, 200), 
                on_click=self.snake.move_direction,
                on_click_args="left",
                shadow_on_click=2,
                db_click_func=self.snake.db_click,
                db_click_f_args="left",
                border_radius=8
            ),
            Button(
                pos=pg.Vector2(1024//2+250+75, 768//2-250),
                size=(100, 500),
                bg_color=(80,60,129),
                bg_color_hover=(69,47,88),
                text="RIGHT",
                font=pg.font.Font("regular.ttf", 25),
                text_color=(255, 255, 255),
                text_color_hover=(200, 200, 200),  
                on_click=self.snake.move_direction,
                on_click_args="right",
                shadow_on_click=2,
                db_click_func=self.snake.db_click,
                db_click_f_args="right",
                border_radius=8
            ),
            Button(
                pos=pg.Vector2(19, 19),
                size=(110, 730),
                bg_color=(80,60,129),
                bg_color_hover=(69,47,88),
                text="Start",
                font=pg.font.Font("regular.ttf", 25),
                text_color=(255, 255, 255),
                text_color_hover=(200, 200, 200),  
                on_click=self.snake.start_game,
                shadow_on_click=2,
            )
        ]

    def handle_events(self, event:pg.event.Event):

        for button in self.buttons:
            button.handle_events(event)
    
    def update(self, screen):
        
        screen.fill((46,20,64))
        
        for button in self.buttons:
            button.draw(screen)
            
        self.snake.update(screen)


class Snake:

    def __init__(self, canvas):

        # DISPLAY
        self.canvas = canvas
        self.canvas.fill((69,47,88))
        self.W, self.H = self.canvas.get_size()

        # SNAKE
        self.body = [[100, 100], [110, 100], [120, 100], [130, 100]]
        self.body.reverse()
        self.BASE_BODY = copy(self.body)
        self.direction = "right"
        self.size = (10, 10)
        self.score = 0

        # FRUIT
        self.fruits = []
        self.new_fruit()

        # TIME
        self.began_game = False
        self.cur_time = pg.time.get_ticks()
        self.delay = pg.time.get_ticks()
        self.lost = False

        # VEL
        self.DEFAULT_VEL = 125
        self.vel = copy(self.DEFAULT_VEL) # -> higher vel = slower

        # TEXT
        self.font = pg.font.Font("regular.ttf", 25)

    def db_click(self, dir_):
        self.move_direction(dir_)
        self.double_vel()

    def move_direction(self, dir_):
        if dir_ == "left" and self.direction == "right" or dir_ == "right" and self.direction == "left":
            return
        if dir_ == "up" and self.direction == "down" or dir_ == "down" and self.direction == "up":
            return
        self.direction = dir_

    def start_game(self):
        self.began_game = True
        self.score = 0
        self.lost = False
        self.body = [[100, 100], [110, 100], [120, 100], [130, 100]]
        self.body.reverse()
        self.direction = "right"
        self.fruits = []
        self.new_fruit()

    def append_body(self):
        last = self.body[-1]
        if self.direction == "right":
            dx = -self.size[0]
        elif self.direction == "left":
            dx = self.size[0]
        else:
            dx = 0
        
        if self.direction == "up":
            dy = -self.size[1]
        elif self.direction == "down":
            dy = self.size[1]
        else:
            dy = 0
        self.body.append([last[0]+dx, last[1]+dy])

    def new_fruit(self):
        rangex = range(0, self.W, self.size[0])
        rangey = range(0, self.H, self.size[1])
        self.fruits.append((random.choice(rangex), random.choice(rangey)))

    def move(self):
        self.body.insert(1, copy(self.body[0]))
        self.body.remove(self.body[-1])
        if self.direction == "left":
            self.body[0][0] -= self.size[0]
        elif self.direction == "down":
            self.body[0][1] += self.size[1]
        elif self.direction == "right":
            self.body[0][0] += self.size[0]
        elif self.direction == "up":
            self.body[0][1] -= self.size[1]   

    def double_vel(self):
        if self.vel == self.DEFAULT_VEL:
            self.vel /= 1.5
        else:
            self.vel *= 1.5 

    def check_win(self):
        if not 0 <= self.body[0][0] < 500 or not 0 <= self.body[0][1] < 500:
            return True 
        pos = copy(self.body[0])
        for i in range(1, len(self.body)):
            if pos == self.body[i]:
                return True

        return False

    def draw_text(self, surf, txt:str, color, pos):
        render = self.font.render(txt, True, color)
        rect = render.get_rect(center=pos)
        surf.blit(render, rect)

    def update(self, screen):

        # update time
        self.cur_time = pg.time.get_ticks()

        """# draw grid           
        for w in range(0, self.W, self.size[0]):
            for h in range(0, self.H, self.size[1]):
                pg.draw.line(self.canvas, (255, 255, 255), (0, h), (self.W, h))
                pg.draw.line(self.canvas, (255, 255, 255), (w, 0), (w, self.H))"""

        if self.began_game:
            # fill background
            self.canvas.fill((69,47,88))

            # draw body
            for body in self.body:
                pg.draw.rect(self.canvas, (14,189,175), [*body, *self.size])

            # draw fruit
            for fruit in self.fruits:
                pg.draw.rect(self.canvas, (255, 0, 0), [*fruit, *self.size])
                if pg.Rect(*self.body[0], *self.size).colliderect(pg.Rect(*fruit, *self.size)):
                    self.fruits.remove(fruit)
                    self.new_fruit()
                    self.append_body()
                    self.score += 1

            # move
            if self.cur_time - self.delay > self.vel:
                self.move()
                self.delay = self.cur_time
        
        if not self.began_game and not self.lost:
            self.draw_text(self.canvas, "Press Start to begin", (255, 255, 255), (250, 250))

        if self.check_win() and not self.lost:
            self.lost = True
            self.began_game = False

        if self.lost:
            self.draw_text(self.canvas, f"LOST WITH: {self.score}, press start", (255, 255, 255), (250,250))
    
        if self.vel != self.DEFAULT_VEL:
            self.draw_text(screen, "VelX1.5", (255, 255, 0), (235,75))

        # draw canvas on screen
        self.draw_text(screen, "Double click to change velocity", (100, 100, 100), (1078//2+25, 768-15))
        screen.blit(self.canvas, self.canvas.get_rect(center=(screen.get_width()//2+50, screen.get_height()//2)))
        self.draw_text(screen, f"Score : {self.score}", (255, 255, 255), (screen.get_width()-100, 75))