from pinge import *



victor_lines = [
  [0, 1, 2],
  [3, 4, 5],
  [6, 7, 8],
  [0, 3, 6],
  [1, 4, 7],
  [2, 5, 8],
  [0, 4, 8],
  [2, 4, 6]
]



class ActiveRect(Rect):
  def __init__(self, *args, **kwargs):
    self.active = None
    super().__init__(*args, **kwargs)



class Grid(Widget):
  def __init__(self, **kw):
    self.rects = Group()
    super().__init__(**kw)
    for y in arange(self.y, self.y + self.width, self.width / 3):
      rec = []
      for x in arange(self.x, self.x + self.width, self.width / 3):
        rec.append(ActiveRect(x, y, self.width / 3, self.width / 3, outline = self.outline, color = self.color))
      self.rects.add(rec)
  
  def __iter__(self): return iter(self.rects)
  
  def __getitem__(self, item): return self.rects[item]
  
  def __draw__(self, root):
    for row in self.rects:
      for rect in row: rect.__draw__(root)
  
  def clear_values(self):
    for column in arange(3):
      for row in arange(3): self[column][row].active = None
  
  def ai(self):
    lines = ((0, 1, 2), (1, 2, 0), (0, 2, 1))
    
    if self[1][1].active is None:
      self[1][1].active = 0
      return (self[1][1].x, self[1][1].y)
    
    for row in arange(3):
      for k in lines:
        if self[row][k[0]].active == self[row][k[1]].active and self[row][k[2]].active is None:
          self[row][k[2]].active = 0
          return (self[row][k[2]].x, self[row][k[2]].y)
    
    row, k = None, None
    for k in lines:
      for row in arange(3):
        if self[k[0]][row].active == self[k[1]][row].active and self[k[2]][row].active is None:
          self[k[2]][row].active = 0
          return (self[k[2]][row].x, self[k[2]][row].y)
    
    row, k = None, None
    for k in arange(3):
      for row in arange(3):
        if self[k][row].active is None:
          self[k][row].active = 0
          return (self[k][row].x, self[k][row].y)
  
  def check(self):
    new_map = []
    for i in self.rects: new_map.extend(list(map(lambda el: el.active, i)))
    for j in victor_lines:
      if new_map[j[0]] == new_map[j[1]] == new_map[j[2]] and new_map[j[0]] is not None: return new_map[j[0]]
    
    if len(list(filter(lambda el: not None in list(map(lambda e: e.active, el)), self.rects))) == 3: return -1



class KPECT(Widget):
  def __draw__(self, root):
    Line(self.x + 5, self.y + 5, self.x + self.width - 5, self.y + self.width - 5, color = "red", outline = 10).__draw__(root)
    Line(self.x + 5, self.y + self.width - 5, self.x + self.width - 5, self.y + 5, color = "red", outline = 10).__draw__(root)



app = App(0, 0, "Big tic tac toe", fps = 30)
WIDTH, HEIGHT = app.screen_size()



grid = Group()
res = Group()
back = Text("Back", "./fonts/ChargerMonospace.otf", round(WIDTH / 43), color = "red")
restart = Text("Restart", "./fonts/ChargerMonospace.otf", round(WIDTH / 43), color = "red", y = 75)
player = Text("Red's turn", "Arial", round(WIDTH / 57), True, color = "red")
player.mode = 1
player.setbycenter(WIDTH / 2, HEIGHT * 0.8)



for y in arange(0, WIDTH / 3.85 + 10, WIDTH / 7.7):
  for x in arange(WIDTH / 2 - WIDTH / 5.12, WIDTH / 2 + 200, WIDTH / 7.7):
    grid.add(Grid(x = x, y = y, width = WIDTH / 7.7, height = WIDTH / 7.7, outline = 5, color = (10, 150, 10)))



grid.add(Grid(x = WIDTH / 2 - WIDTH / 5.12, width = WIDTH / 2.56, height = HEIGHT, outline = 8))



def game(frame, computer = None):
  end = False
  
  if not grid in app.objects: app.add(grid, player, back, restart, res)
  
  if not game.pressed:
    
    if back.is_hovered(): back.color = "blue"
    else: back.color = "red"
    
    if restart.is_hovered(): restart.color = "blue"
    else: restart.color = "red"
    
    if back.is_once_clicked():
      app.remove(grid, player, back, restart, res)
      app.set_function(menu)
      return
    
    if restart.is_once_clicked():
      res.clear()
      for i in arange(10): grid[i].clear_values()
      player.mode = 1
      player.text = "Red's turn"
      player.color = "red"
      player.setbycenter(WIDTH / 2, HEIGHT * 0.8)
      return
  
    for gr in arange(9):
      if end: break
      
      for row in arange(3):
        if end: break
        
        for rect in arange(3):
          curr = grid[gr][row][rect]
            
          if curr.is_once_clicked() and curr.active is None:
            grid[gr][row][rect].active = player.mode
              
            if computer is None:
                
              if player.mode == 1:
                res.add(KPECT(curr.x, curr.y, curr.width))
                player.mode = 0
                player.text = "Blue's turn"
                player.color = "blue"
              else:
                res.add(Ellipse(curr.x + 5, curr.y + 5, curr.width - 5, curr.height - 5, color = "blue", outline = 8))
                player.mode = 1
                player.text = "Red's turn"
                player.color = "red"
                
              player.setbycenter(WIDTH / 2, HEIGHT * 0.8)
              
            else:
              
              if player.text != "Your turn":
                player.text = "Your turn"
                player.mode = 1
                player.color = "red"
                player.setbycenter(WIDTH / 2, HEIGHT * 0.8)
                
              res.add(KPECT(curr.x, curr.y, curr.width))
              
              ai = grid[gr].ai()
              if ai: res.add(Ellipse(ai[0], ai[1], WIDTH / 23 + 5, WIDTH / 23 - 5, color = "blue", outline = 8))
              
            result = grid[gr].check()
              
            if result is not None:
              res.add(Rect(grid[gr][0][0].x, grid[gr][0][0].y, WIDTH / 7.7, WIDTH / 7.7, color = "black"))
              
              if result == 1: res.add(KPECT(grid[gr][0][0].x, grid[gr][0][0].y, WIDTH / 7.7))
              elif result == 0: res.add(Ellipse(grid[gr][0][0].x + 8, grid[gr][0][0].y + 8, WIDTH / 7.7, WIDTH / 7.7, color = "blue", outline = 8))
              
              grid[-1][gr % 3][gr // 3].active = result

            end = True
            break
  
  if game.pressed and not ms.is_pressed(): game.pressed = False
  
  ch = grid[-1].check()
  
  if ch is not None:
    app.remove(grid, player, back, restart, res)
    app.set_function(lambda c: winner(ch, c))
    res.clear()
    for i in arange(10): grid[i].clear_values()
    player.mode = 1



winner_win = Group(Rect(WIDTH * 0.1, HEIGHT * 0.1, WIDTH * 0.8, HEIGHT * 0.8, 0, 10, "blue", 15))
winner_text = Text("", "Arial", round(WIDTH / 17.1), True)
help = Text("Press tab to exit", "./fonts/ChargerMonospace.otf", round(WIDTH / 64), color = "red")
help.setbycenter(WIDTH / 2, HEIGHT * 0.55)



def winner(wins, frame):
  if not winner_win in app.objects: app.add(winner_win, winner_text, help)
  
  if is_pressed("tab"):
    app.remove(winner_win, winner_text, help)
    app.set_function(menu)
    return
  
  if wins == 1:
    winner_text.text = "Red is the winner!"
    winner_text.color = "red"
  
  elif wins == 0:
    winner_text.text = "Blue is the winner!"
    winner_text.color = "blue"
  
  else:
    winner_text.text = "Nobody win. Draw!"
    winner_text.color = "green"
  
  winner_text.setbycenter(WIDTH / 2, HEIGHT / 2 - 50)



rules_win = Group(Rect(WIDTH * 0.05, HEIGHT * 0.05, WIDTH * 0.9, HEIGHT * 0.9, 0, 10, "blue", 15))

rules_back = Text("Back", "./fonts/ChargerMonospace.otf", round(WIDTH / 43), color = "red", x = WIDTH * 0.05 + 20, y = HEIGHT * 0.05 + 10)

rules_text = Group(
  Text("How to play", "Arial", round(WIDTH / 17.1), True, color = "red"),
  Text("Big tic-tac-toe is a classic tic-tac-toe, where", "Arial", round(WIDTH / 43), True, color = "red"),
  Text("there is another batch in each cell. The goal is to", "Arial", round(WIDTH / 43), True, color = "red"),
  Text("win a game in each cell and win the whole, big game.", "Arial", round(WIDTH / 43), True, color = "red")
)

rules_text[0].setbycenter(WIDTH / 2, HEIGHT * 0.2)

for i in arange(1, 4): rules_text[i].setbycenter(WIDTH / 2, HEIGHT * 0.4 + i * 100)



play = Text("Play", "./fonts/ChargerMonospace.otf", round(WIDTH / 32))

comp = Text("With computer", "./fonts/ChargerMonospace.otf", round(WIDTH / 32))

rules = Text("Rules", "./fonts/ChargerMonospace.otf", round(WIDTH / 32))

title = Group(
  Text("Tic", "./fonts/Softie Cyr.ttf", round(WIDTH / 17.1), color = "red"),
  Text("Tac", "./fonts/Softie Cyr.ttf", round(WIDTH / 17.1), color = "green"),
  Text("Toe", "./fonts/Softie Cyr.ttf", round(WIDTH / 17.1), color = "blue"),
  Text("by EtoPinge", "./fonts/ChargerMonospace.otf", round(WIDTH / 128), color = "red"),
  Text("big", "./fonts/Softie Cyr.ttf", round(WIDTH / 25.6), color = "blue")
)

title[-1].setbycenter(WIDTH / 2, HEIGHT * 0.1)
title[-2].setbycenter(WIDTH / 2, HEIGHT * 0.35)

for txt in arange(0, 3): title[txt].setbycenter(WIDTH / 2 - title[txt].width + txt * 300 - 50, HEIGHT * 0.25)

play.setbycenter(WIDTH / 2, HEIGHT * 0.6)
rules.setbycenter(WIDTH / 2, HEIGHT * 0.75)
comp.setbycenter(WIDTH / 2, HEIGHT * 0.9)



def menu(frame):
  if not play in app.objects: app.add(play, title, rules, comp)
  
  if play.is_hovered(): play.color = "blue"
  else: play.color = "red"
  
  if comp.is_hovered(): comp.color = "blue"
  else: comp.color = "red"
  
  if rules.is_hovered(): rules.color = "blue"
  else: rules.color = "red"
  
  if rules.is_once_clicked():
    app.remove(play, title, rules, comp)
    app.set_function(rule)
  
  if play.is_once_clicked():
    app.remove(play, title, rules, comp)
    game.pressed = True
    app.set_function(game)
  
  if comp.is_once_clicked():
    app.remove(play, title, rules, comp)
    game.pressed = True
    app.set_function(lambda f: game(f, True))



def rule(frame):
  if not rules_win in app.objects: app.add(rules_win, rules_back, rules_text)
  
  if rules_back.is_hovered(): rules_back.color = "blue"
  else: rules_back.color = "red"
  
  if rules_back.is_once_clicked():
    app.remove(rules_win, rules_back, rules_text)
    app.set_function(menu)



app.run(menu)