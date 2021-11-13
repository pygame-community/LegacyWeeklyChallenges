import pygame

class UiObject:
	def __init__(self, rect):
		self.rect = rect
		self.active = True

	def scaling_text(self, rect, text, borders=(20, 10)):
		i_rect = text.get_rect()
		new_w, new_h = i_rect.w, i_rect.h
		if i_rect.w >= rect.w-borders[0]:
			new_w = int(i_rect.w/(i_rect.w/(rect.w-borders[0])))
		if i_rect.h >= rect.h-borders[1]:
			new_h = int(i_rect.h/(i_rect.h/(rect.h-borders[1])))
		text = pygame.transform.scale(text, (new_w, new_h))
		center = text.get_rect(center=(rect.w/2, rect.h/2))
		return(center, text)

	def logic(**kwargs):
		pass

	def draw(self, screen):
		pass

class SimpleButton(UiObject):
	def __init__(self, rect, colors=((80, 80, 80), (50, 50, 50), (100, 100, 100)), 
				 bold=((0, 0, 0), 10), sounds=None, text=None, icons=None, centered=None, 
				 click=1, action=None):
		super().__init__(rect)
		self.pressed = False
		self.clicked = 0
		self.sounds = sounds
		self.hovering = False
		self.task = False
		self.action = action
		self.click = click
		self.surfaces = tuple([pygame.Surface((rect.w, rect.h), pygame.SRCALPHA).convert_alpha() for _ in range(3)])
		for index, surface in enumerate(self.surfaces):
			surface.fill(colors[index])
			pygame.draw.rect(surface, bold[0], (0, 0, rect.w, rect.h), bold[1])
		if text:
			center, text = self.scaling_text(self.rect, text)
			for surface in self.surfaces:
				surface.blit(text, center)
		if icons:
			for icon in icons:
				img = pygame.transform.scale(icon[0], (icon[1].w, icon[1].h))
				for surface in self.surfaces:
					surface.blit(img, icon[1])
		if centered: self.rect.center = centered

	def logic(self, **mouse):
		mouse_btn = mouse.get("m_btn", {i:False for i in range(0, 2)})
		mouse_pos = mouse.get("m_pos", (0, 0))
		hovering = True if self.rect.collidepoint(mouse_pos) else False
		#plays when mouse hovers on the button
		self.sounds[1].play() if self.sounds and hovering and not self.hovering else None
		self.hovering = hovering
		self.clicked = 0 if not self.hovering else self.clicked
		if not mouse_btn[0] and self.pressed:
			self.pressed = False
			self.clicked += 1/self.click
			#plays when mouse clicks on the button
			self.sounds[0].play() if self.sounds else None
			if int(self.clicked):
				self.clicked = 0
				if self.action:
					self.action[0](self.action[1])
		elif self.hovering and mouse_btn[0]:
			self.pressed = True

	def draw(self, screen):
		if self.active:
			if self.pressed:
				surface = self.surfaces[1]
			elif self.hovering:
				surface = self.surfaces[2]
			else:
				surface = self.surfaces[0]
			screen.blit(surface, self.rect)