from typing import *
import pygame as pg
from tkinter.messagebox import showerror
from threading import Thread
from socket import *
from numpy import *


try:
  from keyboard import *
except ModuleNotFoundError:
  try:
    import os
    os.system("pip install keyboard")
    from keyboard import *
  except ModuleNotFoundError:
    print("\033[31Cannot install keyboard library. Do not use is_pressed() function and Input widget.\033[0m")


__G = 9.8
KEY_LIST, SHIFT_LIST = list("abcdefghijklmnopqrstuvwxyz1234567890-=/*\\[]';.,/`"), list("ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()_+{}\"|:?<>~")


def is_once_pressed(key):
  if is_pressed(key) and not key in is_once_pressed.pressed:
    is_once_pressed.pressed.append(key)
    return True
  if not is_pressed(key):
    try: is_once_pressed.pressed.remove(key)
    except: ...
  return False


is_once_pressed.pressed = []


def is_mouse_pressed(btn = "left"):
  ind = 0
  if btn == "right": ind = 2
  elif btn == "middle": ind = 1
  return pg.mouse.get_pressed()[ind]


get_gravity = lambda: __G


def set_gravity(g: float = 9.8):
  global __G
  __G = g


get_system_fonts = pg.font.get_fonts


pg.init()


try: pg.mixer.init()
except pg.error: print("\033[31mCannot initialize audio module. Don't use Sound() function.\033[0m")


mouse_pos = pg.mouse.get_pos


set_mouse_pos = pg.mouse.set_pos


hide_mouse = lambda: pg.mouse.set_visible(0)


show_mouse = lambda: pg.mouse.set_visible(1)


is_mouse_visible = pg.mouse.get_visible


Sound = pg.mixer.Sound


class Hitbox:
  def __init__(self, x: float = 0, y: float = 0, width: float = 20, height: float = 20, angle: float = 0):
    self.x = x
    self.y = y
    self.width = width
    self.height = height
    self.angle = angle
    self.pressed = False

  def move(self, x: float = 0, y: float = 0):
    self.x += x
    self.y += y

  def setcoords(self, x: float = 0, y: float = 0):
    self.x = x
    self.y = y
  
  def setbycenter(self, x: float, y: float):
    self.x = x - self.width / 2
    self.y = y - self.height / 2

  def setsize(self, width: float = 20, height: float = 20):
    self.width = width
    self.height = height

  def scale(self, x: float = 1, y: float = 1):
    self.width *= x
    self.height *= y
  
  def setrotate(self, angle: float = 0):
    self.angle = angle
  
  def rotate(self, angle: float = 0):
    self.angle += angle

  def is_clicked(self, btn = "left"):
    return is_mouse_pressed(btn) and self.is_hovered()
  
  def is_once_clicked(self, btn = "left"):
    if self.is_clicked(btn) and not self.pressed:
      self.pressed = True
      return True
    if not self.is_clicked(btn): self.pressed = False
    return False
  
  def __str__(self): return "<" + self.__class__.__name__ + " " + str(self.x) + ", " + str(self.y) + ">"
  
  def __repr__(self): return str(self)

  def is_hovered(self):
    ms = pg.mouse.get_pos()
    return ms[0] >= self.x and ms[0] <= self.x + self.width and ms[1] >= self.y and ms[1] <= self.y + self.height and pg.mouse.get_focused()

  def is_collides(self, hitbox: Self):
    return self.x <= hitbox.x + hitbox.width and self.x + self.width >= hitbox.x and self.y <= hitbox.y + hitbox.height and self.y + self.height >= hitbox.y


class Shader:
  def __init__(self, x: int, y: int, fn = lambda:None):
    self.fn = fn
    self.x = x
    self.y = y

  def __draw__(self, root):
    for y in arange(self.y):
      for x in arange(self.x):
        pg.draw.rect(root, self.fn(x, y), (x, y, 1, 1))


class Widget(Hitbox):
  def __init__(self, x: float = 0, y: float = 0, width: float = 20, height: float = 20, angle: float = 0, radius: int = -1, color = "white", outline: float = 0, tags: Iterable[str] = [], physic: bool = False):
    self.x = x
    self.y = y
    self.width = width
    self.height = height
    self.angle = angle
    self.color = color
    self.radius = radius
    self.tags = tags
    self.outline = outline
    self.physic = physic
    super().__init__(x, y, width, height, angle)
  
  def is_collides_widget(self, w: Hitbox, root):
    for obj in root.objects:
      if self.is_collides(obj) and isinstance(obj, w): return True
    return False
  
  def is_collides_tag(self, tag: str, root):
    for obj in root.objects:
      if self.is_collides(obj) and tag in obj.tags: return True
    return False

  def __draw__(self, root): ...


class Group:
  def __init__(self, *objects: Widget):
    self.objects = list(objects)
    self.tags = []
    self.physic = False
  
  def add(self, *obj: Widget):
    for i in obj: self.objects.append(i)

  def remove(self, *obj: Widget):
    for i in obj: self.objects.remove(i)

  def get_by_tag(self, tag: str):
    out = []
    for o in arange(len(self.objects)):
      if tag in self.objects[o].tags: out.append(self.objects[o])
    return out
  
  def clear(self): self.objects.clear()
  
  def scale(self, x: float = 1, y: float = 1):
    for i in arange(len(self.objects)): self.objects[i].scale(x, y)
  
  def get_widgets(self, w: type[Widget]): return list(filter(lambda e: isinstance(e, w), self.objects))

  def move(self, x: int = 0, y: int = 0):
    for o in arange(len(self.objects)): self.objects[o].move(x, y)
  
  def __len__(self): return len(self.objects)

  def is_collides(self, hitbox: Hitbox):
    return any(map(lambda el: el.is_collides(hitbox), self.objects))
  
  def is_collides_tag(self, hitbox: Hitbox, tag: str):
    return any(map(lambda el: el.is_collides(hitbox) and tag in el.tags, self.objects))
  
  def __str__(self): return "<Group " + str(self.objects)[1:-1] + ">"
  
  def __repr__(self): return str(self)
  
  def __getitem__(self, item: int): return self.objects[item]
  
  def __iter__(self): return iter(self.objects)

  def __draw__(self, root):
    for obj in self.objects: obj.__draw__(root)


class Rect(Widget):
  def __draw__(self, root):
    pg.draw.rect(root, self.color, pg.Rect(self.x, self.y, self.width, self.height), self.outline, self.radius)


class Ellipse(Widget):
  def __draw__(self, root):
    pg.draw.ellipse(root, self.color, pg.Rect(self.x, self.y, self.width, self.height), self.outline)


class Line(Widget):
  def __draw__(self, root):
    pg.draw.line(root, self.color, (self.x, self.y), (self.width, self.height), self.outline)


class Image(Widget):
  def __init__(self, path: str = "", **kw):
    super().__init__(**kw)
    self.path = path
    self.__i = pg.image.load(path)
  
  def reload(self, path: str):
    self.path = path
    self.__i = pg.image.load(path)

  def __draw__(self, root):
    root.blit(pg.transform.scale(self.__i, (self.width, self.height)), pg.Rect(self.x, self.y, self.width, self.height))


class Text(Widget):
  def __init__(self, text: str = "", font: str = "", size: float = 10, bold: bool = False, opacity: int = 1, **kw):
    super().__init__(**kw)
    self.text = text
    self.size = size
    self.font = font
    self.opacity = opacity
    self.bold = bold
    try: f = pg.font.Font(self.font, self.size).render(self.text, True, self.color)
    except: f = pg.font.SysFont(self.font, self.size, self.bold).render(self.text, True, self.color)
    self.width, self.height = f.get_rect().size
  
  def update_size(self):
    try: f = pg.font.Font(self.font, self.size).render(self.text, True, self.color)
    except: f = pg.font.SysFont(self.font, self.size, self.bold).render(self.text, True, self.color)
    self.width, self.height = f.get_rect().size
  
  def __draw__(self, root):
    try: f = pg.font.Font(self.font, self.size).render(self.text, True, self.color)
    except: f = pg.font.SysFont(self.font, self.size, self.bold).render(self.text, True, self.color)
    self.width, self.height = f.get_rect().size
    f.set_alpha(round(self.opacity * 255))
    root.blit(f, pg.Rect(self.x, self.y + self.size / 10, 1, 1))


CHAR_LENGTH = Text("w").width


class Input(Widget):
  def __init__(self, font: str = "", bg = None, max_length: int = 100, size: int = 20, border: int = 1, outline = "black", radius: int = -1, **kw):
    self.font = font
    self.bg = bg
    self.outline = outline
    self.border = border
    self.radius = radius
    self.max_length = max_length
    self.text = ""
    self.size = size
    self.enter = False
    self.caps_locked = False
    self.resizable = False
    super().__init__(**kw)
  
  def __draw__(self, root):
    txt = Text(self.text, self.font, self.size, x = self.x + self.border, y = self.y, color = self.color)
    border = Rect(self.x, self.y, txt.width * 1.34 if self.resizable else self.max_length * CHAR_LENGTH, txt.height or self.size, 0, self.radius, self.outline, self.border)
    if self.bg is not None: Rect(self.x + 1, self.y + 1, border.width - 2, border.height - 2, 0, self.radius, self.bg).__draw__(root)
    
    if border.is_once_clicked(): self.enter = True
    if is_mouse_pressed() and not border.is_hovered(): self.enter = False
    
    if is_once_pressed("caps_lock"): self.caps_locked = not self.caps_locked
    
    if self.enter:
      if txt.width < border.width:
        if is_pressed("shift") or self.caps_locked:
          for i in arange(len(SHIFT_LIST)):
            if is_once_pressed(KEY_LIST[i]): self.text += SHIFT_LIST[i]
        
        else:
          for i in arange(len(KEY_LIST)):
            if is_once_pressed(KEY_LIST[i]): self.text += KEY_LIST[i]
    
      if is_once_pressed("backspace"): self.text = self.text[:-1]
      
      if is_pressed("delete"): self.txt = ""
    
    border.__draw__(root)
    txt.__draw__(root)


class Animation:
  def __init__(self, fn: Callable = lambda: None, endframe: int = 30):
    self.fn = fn
    self.frame = 0
    self.endframe = endframe
  
  def setframe(self, frame: int): self.frame = frame
  
  def __draw__(self):
    if self.frame < self.endframe:
      self.frame += 1
      if self.fn(self.frame) == -1: self.endframe = 0


class Client(socket):
  def __init__(self, host: Union[str, bytes], port: uint16, connect = True):
    self.host = host
    self.port = port
    super().__init__(AF_INET, SOCK_STREAM)
    if connect: self.connect()
  
  def connect(self):
    super().connect((self.host, self.port))
  
  def send(self, data):
    self.sendall(data)
    return self.recv(len(str(data)))
  
  def __del__(self): self.close()


class App:
  def __init__(self, width: int = 800, height: int = 600, title: str = "Untitled", bg: str = "black", src: str = "", resizable: bool = False, fps: float = 30):
    global __window
    self.width = width or self.screen_size()[0]
    self.height = height or self.screen_size()[1]
    self.title = title
    self.resizable = resizable
    self.bg = bg
    self.fps = fps
    self.animations = []
    self.src = src
    self.exit = exit
    self.objects = []
    self.__screen = pg.display.set_mode((self.width, self.height), flags = (pg.RESIZABLE if self.resizable else 0))
    pg.display.set_caption(self.title)
    if self.src != "": pg.display.set_icon(pg.image.load(self.src))
    self.__clock = pg.time.Clock()
  
  def update_params(self):
    if self.fullscreen: pg.display.toggle_fullscreen() 
    pg.display.set_caption(self.title)
    pg.display.set_icon(self.src)
  
  def screen_size(self):
    inf = pg.display.Info()
    return (inf.current_w, inf.current_h)

  def add(self, *obj: Hitbox):
    for i in obj: self.objects.append(i)
  
  def start(self, ani: Animation): self.animations.append(ani)
  
  def clear(self): self.objects.clear()
  
  def setfps(self, fps: float): self.fps = fps
  
  def on_exit(self, fn: Callable): self.exit = fn
  
  def get_widgets(self, w: type[Widget]): return list(filter(lambda e: isinstance(e, w), self.objects))

  def remove(self, *obj: Hitbox):
    for i in obj: self.objects.remove(i)
  
  def draw(self, obj: Widget): obj.__draw__(self.__screen)

  def get_by_tag(self, tag: str):
    out = []
    for o in arange(len(self.objects)):
      if tag in self.objects[o].tags: out.append(self.objects[o])
    return out
  
  def set_function(self, fn: Callable = lambda c: None): self.__fn = fn
  
  def run(self, fn: Callable = lambda c: None):
    curr_frame = 0
    self.set_function(fn)
    while True:
      curr_frame += 1
      self.__clock.tick(self.fps)
      for e in pg.event.get():
        if e.type == pg.QUIT: self.exit(e)
      self.__screen.fill(self.bg)
      self.__fn(curr_frame)
      for i in self.animations:
        i.setframe(curr_frame)
        self.draw(i)
      try:
        for obj in self.objects:
          if obj.physic and not obj.is_collides_tag("static", self): obj.y += self.fps / get_gravity()
          self.draw(obj)
        pg.display.flip()
      except pg.error: self.exit(None)