import sys
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

# This line tells python how to handle the relative imports
# when you run this file directly.
__package__ = "03-buttons." + Path(__file__).absolute().parent.name

# ---- Recommended: don't modify anything above this line ---- #

# Metadata about your submission
__author__ = "andenixa#2251"  # Put yours!
__achievements__ = [  # Uncomment the ones you've done
    "Casual",
    "Ambitious",
    "Adventurous",
]

import math
from functools import lru_cache
from types import MethodType

import pygame

# To import the modules in yourname/, you need to use relative imports,
# otherwise your project will not be compatible with the showcase.
# noinspection PyPackages
from .utils import *

#BACKGROUND = 0x0F1012

BACKGROUND = (35,46,58)


def pulse(value, freq):
    return math.sin(pygame.time.get_ticks()/freq) * value

@lru_cache(5000)
def text_alt(txt, color, size=20, font_name=None, **kwargs):
    """Render a text on a surface. Results are cached."""
    return font(size, font_name).render(str(txt), True, color, **kwargs)

class Textitsu:
    """ Just a demo class, not significant to the submittion """
    def __init__(self, s, pos, size, color):
        self.topleft = pygame.Vector2(pos)
        self.s = s
        self.size = size
        self.color = color
        self.font = pygame.font.Font(None, size)
        self.text_sprite = self.font.render(s, False, color)
        self._life = 100
        self._life_max = 100

    def update(self):        
        zoom = (self._life_max - self._life)/self._life_max
        #w, h = self.text_sprite.get_size()
        rect = self.text_sprite.get_rect()
        
        erect = rect.fit(pygame.Rect(0,0, rect.width*zoom,rect.width*zoom))
        self.pos = self.topleft + (pygame.Vector2(rect.center) - pygame.Vector2(erect.center))/2 
        self.pos.y += .85 * self._life

        self.image = pygame.transform.scale(self.text_sprite, (erect.width, erect.height))
        self._life -= 1
        inv_life = self._life_max - self._life
        self.pos.x += pulse((inv_life)/100, 15)
    
    def draw(self, surf):
        surf.blit(self.image, self.pos)

class Button:
    """ Implements PyGame Button
    """
    DBLCLICK_DELAY = 200 # milliseconds
    SHADED=1 # text is shaded
    GLOWING=2 # glow text on selection
    HIGHLIGH=4 # highlight on selection
    MOVEPUSH=8 # change y on push
    ROUND=16 # round edges
    BORDER=32 # colored border
    SMOOTHMOVE=64 # smooth movement on push
    NINEPATCH=128 # use nine-patch mode
    TEXTHALO=256 # draw outline / halo
    DROPSHADOW=512 # drop button shadows
    def __init__(self, s, pos, size=None, text_size=20, color=(133,90,144), 
                 text_color="lightgreen", border_color=None, on_push=None, 
                 on_doubleclick=None, features=0, ninepatch_img=None, ninepatch_slice=None,
                 ninepatch_active_img=None, ninepatch_active_slice=None):

        self.text = s # internal string
        self.label = s # button label
        self.pos = pygame.Vector2( pos )
        self._color = pygame.Color(color)

        if ninepatch_img is not None:
            if isinstance( ninepatch_img, str ):
                ninepatch_img = load_image(ninepatch_img)            
            #auto patching
            if ninepatch_slice is None:
                ninepatch_slice = self._find_slice(ninepatch_img)
            crop_rect = ninepatch_img.get_rect().inflate(-2, -2)
            ninepatch_img = self._crop(ninepatch_img, crop_rect)        
        self.ninepatch_img = ninepatch_img
        self.ninepatch_slice = ninepatch_slice

        if ninepatch_active_img is not None:
            if isinstance( ninepatch_active_img, str ):
                ninepatch_active_img = load_image(ninepatch_active_img)            
            #auto patching
            if ninepatch_active_slice is None:
                ninepatch_active_slice = self._find_slice(ninepatch_active_img)
            crop_rect = ninepatch_active_img.get_rect().inflate(-2, -2)
            ninepatch_active_img = self._crop(ninepatch_active_img, crop_rect)        
        self.ninepatch_active_img = ninepatch_active_img
        self.ninepatch_active_slice = ninepatch_active_slice
        
        if border_color is None:
            border_color = self._darker(color, .35)
        self._border_color = pygame.Color(border_color)
        self._text_color = tuple(pygame.Color(text_color))
        self._padding = 32
        self._border = 2
        self._text_size = text_size
        self._push_off_y = 4
        if size is None: 
            t_size = text(self.label, self._text_color, size=self._text_size).get_rect()                        
            size = t_size.inflate(self._padding, self._padding)[2:]
        else:
            for i in reversed(range(len(s))):                
                _str = self.text[:i]+".."
                t_size = text(_str, self._text_color, size=self._text_size).get_rect()
                if t_size.width < (size[0]-self._padding):
                    self.label = _str
                    break
        self.size = size
        self._features = features
        self._pushed = False
        self._active = False
        self._last_click_at = 0
        if on_doubleclick is not None:
            on_doubleclick = MethodType(on_doubleclick, self)
        if on_push is not None:
            on_push = MethodType(on_push, self)                    
        self._on_push_cb = on_push      
        self._on_doubleclick_cb = on_doubleclick
        self._move_down = False
        self._y_shift = 0
        self._y_increment = .75
        self._dirty = True

    @staticmethod
    def _find_slice(surf):
        np_slicetest = surf.copy()
        rect = np_slicetest.get_rect().inflate(-2, -2) # find rect denoting middle
        np_slicetest.fill(np_slicetest.get_at((0,0)), rect)
        np_slicetest = pygame.mask.from_surface(np_slicetest)
        try:
            top, right, left, bottom = np_slicetest.get_bounding_rects()
        except:
            raise ValueError("Can't find ninepatch slices automatically")
        return top.x-1, left.y-1

    @staticmethod
    def _crop(surf, area_rect):
        new_surf = pygame.Surface(area_rect[2:])
        new_surf.blit(surf, (0,0), area_rect)
        return new_surf

    @staticmethod
    def _brighter(color, amount):
        """ make specified color lighter via HSLA representation """
        _color = pygame.Color(color)
        h,s,l,a = _color.hsla
        l = max(0, min(l+l*amount, 99))
        _color.hsla = h,s,l,a
        return tuple(_color)
        
    @staticmethod
    def _darker(color, amount):
        """ make specified color darker via HSLA representation """
        _color = pygame.Color(color)
        h,s,l,a = _color.hsla 
        l = max(0, min(l-l*amount, 99))
        _color.hsla = h,s,l,a
        return _color

    def on_push(self):
        """ is executed when a button is pushed/pressed """
        if callable(self._on_push_cb):
            return self._on_push_cb()
        return True        

    def dblclicked(self):
        """ Double clicked event """
        if callable(self._on_doubleclick_cb):
            return self._on_doubleclick_cb()
        return True

    def handle_event(self, event: pygame.event.Event):
        if event.type==pygame.MOUSEBUTTONDOWN:
            if not self.pushed:
                if pygame.Rect(self.pos, self.size).collidepoint(*event.pos):
                    self.pushed = True
                    if (pygame.time.get_ticks()-self._last_click_at)<self.DBLCLICK_DELAY:
                        self.dblclicked()
                    else:
                        self._last_click_at = pygame.time.get_ticks()
        elif event.type==pygame.MOUSEBUTTONUP:
            self.pushed = False
        elif event.type==pygame.MOUSEMOTION:
            if pygame.Rect(self.pos, self.size).collidepoint(*event.pos):
                self.active = True
            else:
                self.active = False
        return True

    @property
    def pushed(self):        
        return self._pushed

    @pushed.setter
    def pushed(self, pushed):
        if self._pushed != pushed:            
            self._pushed = pushed
            self._dirty = True   
            self._move_down = True                                                   

    @property
    def active(self):        
        return self._active

    @staticmethod
    def _render_ninepatch(im, slice, surf, size):
        w,h = slice        
        ltop = im.subsurface(pygame.Rect(0,0,w,h))
        rtop = im.subsurface(pygame.Rect(im.get_width()-w,0,w,h))
        lbot = im.subsurface(pygame.Rect(0,im.get_height()-h,w,h))
        rbot= im.subsurface(pygame.Rect(im.get_width()-w,im.get_height()-h,w,h))

        left = im.subsurface(pygame.Rect(0,h, w, im.get_height()-h*2))   
        right = im.subsurface(pygame.Rect(im.get_width()-w,h, w, im.get_height()-h*2))   

        bt = im.subsurface(pygame.Rect(w, im.get_height()-h, im.get_width()-2*w, h)) 
        top = im.subsurface(pygame.Rect(w, 0, im.get_width()-2*w, h)) 

        middle = im.subsurface(pygame.Rect(w, h, im.get_width()-2*w, im.get_height()-h*2)) 
        for y in range(h, size[1]-h, left.get_height()):
            for x in range(w, size[0]-w, bt.get_width()):
                surf.blit(middle, (x, y) )

        for x in range(w, size[0]-w, bt.get_width()):
            surf.blit(bt, (x, size[1]-h) )
            surf.blit(top, (x, 0) )

        for y in range(h, size[1]-h, left.get_height()):
            surf.blit(left, (0,y))
            surf.blit(right, (size[0]-w,y))                    

        surf.blit(ltop, (0,0))
        surf.blit(rbot, (size[0]-w, size[1]-h))
        surf.blit(rtop, (size[0]-w,0))
        surf.blit(lbot, (0, size[1]-h))
        surf.set_colorkey(surf.get_at((0,0)))

    @active.setter
    def active(self, active):
        if self._active != active:
            self._active = active 
            self._dirty = True           
        
    @staticmethod
    def _pyramid_zoom(surf, scale=1.1, downscale=6, border=0):
        w,h = surf.get_size()
        if border:
            surf1 = pygame.Surface((w+border*2, h+border*2))
            surf1.fill(surf.get_at((0,0)))
            surf1.blit(surf, (border, border))
            w1,h1 = surf1.get_size()
            res = pygame.transform.smoothscale(surf1, (w1//downscale,h1//downscale))
            res = pygame.transform.smoothscale(res, (int(w1*scale),int(h1*scale)))
        else:
            res = pygame.transform.smoothscale(surf, (w//downscale,h//downscale))
            res = pygame.transform.smoothscale(res, (int(w*scale),int(h*scale)))
        return res

    def _render(self):
        self._image = pygame.Surface(self.size)
        if self._features & self.ROUND:
            pygame.draw.rect(self._image, self._color, self._image.get_rect().inflate(-2,-2), 0, 14)
            self._image.set_colorkey(self._image.get_at((0,0)))
        else:
            self._image.fill(self._color)

        if self._features & self.BORDER:
            pygame.draw.rect(self._image, self._border_color, self._image.get_rect().inflate(-2,-2), self._border, 14)

        t = text(self.label, self._text_color)
        t_rect = t.get_rect()
        t_rect.center = self._image.get_rect().center        

        # glowing
        if self._active and (self._features & self.GLOWING):
            t_highlight = pygame.Surface(self._image.get_rect()[2:])        
            t_highlight_t = text(self.label, (105,105,105))                     
            t_highlight_rect = t_highlight_t.get_rect(center=t_rect.center)
            t_highlight.blit(t_highlight_t, t_highlight_rect)
            
            scale = 1.0 + math.sin(pygame.time.get_ticks()/100)/15
            t_highlight = self._pyramid_zoom(t_highlight, scale=scale)
            t_highlight_rect = t_highlight.get_rect() #.inflate(-15, -15)
            t_highlight_rect.center=t_rect.center         
            self._image.blit(t_highlight, t_highlight_rect, special_flags=pygame.BLEND_ADD)

        if self._features & self.NINEPATCH:
            if self._active and self.ninepatch_active_img is not None:
                self._render_ninepatch(self.ninepatch_active_img, self.ninepatch_active_slice, self._image, self.size)
            else:
                self._render_ninepatch(self.ninepatch_img, self.ninepatch_slice, self._image, self.size)

        if self._features & self.SHADED:
            t_shade = text(self.label, tuple( self._darker(self._text_color, 0.5) ))
            t_lit = text(self.label, tuple( self._brighter(self._text_color, 0.65) ))
            self._image.blit(t_shade, t_rect.move(1, -1))
            self._image.blit(t_lit, t_rect.move(-1, 1))

        if self._features & self.TEXTHALO:
            pass

        self._image.blit(t, t_rect)

        if self.pushed and not (self._features & self.MOVEPUSH):
            self._image.scroll(0, 2)
        if self._active and not (self._features & self.NINEPATCH):            
            mask=pygame.mask.from_surface(self._image).to_surface()
            mask.set_colorkey((255,255,255))            
            self._image.fill((35,35,35), special_flags=pygame.BLEND_RGB_ADD)
            self._image.blit(mask, (0,0))
            self._dirty = True      

        return self._image

    def draw(self, screen: pygame.Surface):
        if self._dirty:
            self._dirty = False
            self._render()

        if self._move_down:
            if self._y_shift < self._push_off_y:
                if self._features & self.SMOOTHMOVE:
                    self._y_shift += self._y_increment
                else:
                    self._y_shift = self._push_off_y
            elif not self.pushed:
                self._move_down = False
            where = self.pos + (0, self._y_shift)
        else:            
            if self._y_shift > 0:
                if self._features & self.SMOOTHMOVE:
                    self._y_shift -= self._y_increment/2
                else:
                    self._y_shift = 0
            where = self.pos + (0, self._y_shift)            

        if self._features & self.DROPSHADOW:
            shadow_offset = 7
            shadow_border = 16
            shadow_intensity = 18
            shadow_blur = 5
            mask=pygame.mask.from_surface(self._image).to_surface()
            mask.fill((255-shadow_intensity,255-shadow_intensity,255-shadow_intensity),special_flags=pygame.BLEND_SUB)       
            mask = self._pyramid_zoom(mask, scale=1.0, downscale=shadow_blur, border=shadow_border)
            screen.blit(mask, (self.pos-(self._y_shift//2, self._y_shift//2))+(shadow_offset-shadow_border, shadow_offset-shadow_border//2), special_flags=pygame.BLEND_SUB)            
        
        screen.blit(self._image, where)


                       
def mainloop():
    pygame.init()

    texts = []

    buttons = [
        Button("Click me?! Or else!", (400,200), color= Button._darker(pygame.Color("orange"), 0.2), text_color=(220,212,200), features=Button.SHADED|Button.GLOWING|Button.MOVEPUSH, 
               on_doubleclick=lambda self: texts.append(Textitsu("Double Click!", (430,150), 35, (230,230,200)))),

        Button("Praise Her, I am the god!", (380,280), size=(250,45), text_color=(200,222,210), color=BACKGROUND, 
                border_color=(200,200,200), features=Button.GLOWING|Button.MOVEPUSH|Button.BORDER | Button.ROUND | Button.SMOOTHMOVE,
                on_doubleclick=lambda self: texts.append(Textitsu("Double Click #2!", (400,240), 55, (200,200,200)))),

        Button("Clouds Unmake the World", (365,350),  text_color=(87,112,135), features=Button.NINEPATCH|Button.SHADED|Button.MOVEPUSH|Button.SMOOTHMOVE|Button.DROPSHADOW, 
                ninepatch_img="button", ninepatch_active_img="button_selected")
    ]

    clock = pygame.time.Clock()

    while True:
        screen, events = yield
        for event in events:
            if event.type == pygame.QUIT:
                return

            for button in buttons:
                if not button.handle_event(event):
                    break

        screen.fill(BACKGROUND)
        for button in buttons:
            button.draw(screen)

        for text in texts[:]:
            text.update()
            text.draw(screen)
            if text._life < 0:
                texts.remove(text)            

        clock.tick(60)


if __name__ == "__main__":
    wclib.run(mainloop())
