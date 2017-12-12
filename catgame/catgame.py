import random
import pygame
import make_maze

BLACK = (0,0,0)
BEIGE = (190, 174, 148)
WHITE = (255,255,255)
ROSE = (255,228,225)
GREY = (220,220,220)
DKGREY = (128,128,128)
BROWNN = (136, 103, 76)
GREEN = (170, 238, 187)
PINK = (238, 170, 170)

WIDTH = 30
HEIGHT = 30
TILES = 64
VIEWPORT_SIZE = (12 * TILES, 8 * TILES)
SIZE = (16 * TILES + TILES // 2, 9 * TILES)
TITLE_FONT_SIZE = 30
STATUS_FONT_SIZE = TILES // 2 #32

KEYS = (pygame.K_UP,
        pygame.K_DOWN,
        pygame.K_LEFT,
        pygame.K_RIGHT,
        pygame.K_SPACE)

MOVE_KEY = {pygame.K_UP: (0,-1),
            pygame.K_DOWN: (0,1),
            pygame.K_LEFT: (-1,0),
            pygame.K_RIGHT: (1,0)
            }

class Game():
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode(SIZE)
        self.viewport = pygame.Surface(VIEWPORT_SIZE)
        self.title_font = pygame.font.SysFont('Comic Sans MS', TITLE_FONT_SIZE)
        self.status_font = pygame.font.SysFont('Comic Sans MS', TITLE_FONT_SIZE)
        self.cam = Camera()

        self.start = False
        self.gameover = False
        self.game_msg = 'Click to Start'
        self.turn = 0
        self.action_taken = False

        self.key = {k: False for k in KEYS}

        self.sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.npcs = pygame.sprite.Group()
        self.fragile_walls = pygame.sprite.Group()
        self.cat = Cat()
        self.sprites.add(self.cat)

        self.wall_grid = self.make_cave()

        self.make_npcs(3)

        self.cat.place_randomly_avoid_groups(self.walls, self.npcs)
        self.cam.update(self.cat)

        self.dijkstra = self.make_dijkstra(self.cat)

        done = False
        while not done:
            #clear value trackers
            self.action_taken = False
            #clear input buffer
            for i in self.key:
                self.key[i] = False
            #new input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                elif event.type == pygame.KEYDOWN:
                    if event.key in KEYS:
                        self.key[event.key] = True
                elif event.type == pygame.KEYUP:
                    pass
                elif event.type == pygame.MOUSEBUTTONUP:
                    if self.gameover == False:
                        self.start = True

            #Game
            if self.start:
                #interpret key input
                for k in KEYS:
                    if self.key[k]:
                        if k == pygame.K_SPACE:
                            #spacecat!
                            self.action_taken = True
                            pass
                        elif False:
                            #if u add more key input, pls fill this out!
                            pass
                        else:
                            #movecat!
                            self.cat.move(MOVE_KEY[k])
                            self.action_taken = True
                            #check bumps
                            wall = pygame.sprite.spritecollideany(self.cat,self.walls)
                            npc = pygame.sprite.spritecollideany(self.cat,self.npcs)
                            if wall or npc:
                                back = (-1 * MOVE_KEY[k][0], -1 * MOVE_KEY[k][1])
                                self.cat.move(back)
                                self.action_taken = False
                                #if left/right, unreverse dir
                                if k == pygame.K_LEFT or k == pygame.K_RIGHT:
                                    self.cat.dir = not self.cat.dir
                                    self.cat.update()
                            if npc:
                                #fight it!
                                npc.health -= 1
                                self.action_taken = True

                self.cam.update(self.cat)
                #if action was taken, give npcs a chance to react!
                if self.action_taken:
                    self.turn += 1

                    #things that happen periodically (WRT turns)
                    #regen health every 10 turns
                    if self.turn % 10 == 0:
                        for s in self.sprites:
                            try:
                                if s.health < s.max_health:
                                    s.health += 1
                            except AttributeError:
                                pass

                    self.remove_walls()
                    #kill whatever died
                    self.sprites.update()
                    #update dijs
                    self.dijkstra = self.make_dijkstra(self.cat)
                    self.flee_cat_dij = self.make_dijkstra(self.cat, fleeing = True)
                    #move npcs toward player
                    for s in self.npcs:
                        acted = False
                        if s.can_move:
                            x, y, _, _ = s.rect
                            x, y = x // TILES , y // TILES

                            if s.fleeing:
                                use_map = self.flee_cat_dij
                                s.following = None
                            else:
                                use_map = self.dijkstra
                                if use_map[y][x] < 127:
                                    s.following = self.cat
                                else:
                                    s.following = None

                            #choose best path
                            bestd = (0, 0)
                            for d in list(MOVE_KEY.values()):
                                i, j = y + d[1], x + d[0]
                                #check if lowest # so far
                                if use_map[i][j] < use_map[y + bestd[1]][x + bestd[0]]:
                                    #if so, check for bumps
                                    bumped = False
                                    for others in self.sprites:
                                        if others.rect.collidepoint(j * TILES, i * TILES):
                                            #if bumping cat, fight unless fleeing
                                            if others == self.cat:
                                                s.attack(self.cat)
                                                acted = True
                                            bumped = True
                                            break
                                    #if no bumps, save i,j in x,y
                                    if acted:
                                        break
                                    elif not bumped:
                                        bestd = d
                            #move to x,y
                            s.move(bestd)
                            s.update()

                if self.cat.health < 1:
                    self.start = False
                    self.gameover = True
                self.viewport.fill(BEIGE)
                #instead of self.sprites.draw(self.screen), use cam.apply(s) for scroll!
                for s in self.sprites:
                    self.viewport.blit(s.image,self.cam.apply(s))
                #draw the viewport on the screen
                self.screen.blit(self.viewport,(TILES // 2, TILES // 2))
                #draw HP bar
                self.screen.blit(self.make_hpbar(),(13 * TILES, TILES // 2))
                #draw minimap
                self.screen.blit(self.make_minimap(),(13 * TILES, int(5.5 * TILES)))
                #draw other stats, inventory, etc

            else:
                if self.start:
                    pass
                elif self.gameover:
                    self.game_msg = 'Game Over'
                #start screen
                self.screen.fill(GREY)
                textsurf = self.title_font.render(self.game_msg, False, DKGREY)
                rect = textsurf.get_rect()
                center = (SIZE[0]//2 - rect.width//2, SIZE[1]//2 - rect.height//2)
                self.screen.blit(textsurf, center)

            pygame.display.flip()
            self.clock.tick(20)

    def random_cave(self):
        smoothing = 4
        #randomize walls
        grid = [[random.randrange(2) for i in range(WIDTH)] for j in range(HEIGHT)]
        newgrid = [[1 for i in range(WIDTH)] for j in range(HEIGHT)]
        #to encourage mega-caves
        for i in range(2 * WIDTH // 5, 3 * WIDTH // 5):
            grid[HEIGHT // 2][i] = 0
        #smoothing
        for k in range(smoothing):
            for i in range(1,HEIGHT-1):
                for j in range(1,WIDTH-1):
                    wallcount = grid[i-1][j-1] + grid[i-1][j] + grid[i-1][j+1] + grid[i][j-1] +   grid[i][j] +     grid[i][j+1] + grid[i+1][j-1] + grid[i+1][j] + grid[i+1][j+1]
                    if wallcount > 6 or k < smoothing - 1 and wallcount == 1:
                        # ^ to add walls to open space
                        newgrid[i][j] = 1
                    elif wallcount < 5:
                        newgrid[i][j] = 0

            #overwrite old cave values
            for i in range(0,HEIGHT):
                for j in range(0,WIDTH):
                    if k == smoothing - 1:
                        grid[i][j] = newgrid[i][j]
                    else:
                        grid[i][j] = newgrid[i][j]
        return grid

    def random_maze(self):
        grid = make_maze.make_maze(WIDTH, HEIGHT)
        return grid

    def make_cave(self):
        grid = self.random_maze()


        #create wall sprites in wall places
        for i in range(HEIGHT):
            for j in range(WIDTH):
                if grid[i][j]:
                    try:
                        is_fragile = (grid[i-1][j] + grid[i+1][j]) == 0 or (grid[i][j-1] + grid[i][j+1]) == 0
                    except IndexError:
                        is_fragile = False
                    if random.randrange(2):
                        #only fragilize half the time
                        is_fragile = False
                    if is_fragile:
                        wall = Fragile_Wall(j, i)
                        wall.add(self.fragile_walls, self.npcs,self.walls,self.sprites)
                    else:
                        wall = Wall(j,i)
                        wall.add(self.walls,self.sprites)
        return grid

    def remove_walls(self):
        for w in self.fragile_walls:
            if w.health < 1:
                self.wall_grid[w.rect.y // TILES][w.rect.x // TILES] = 0

    def make_npcs(self, n=1):
        for i in range(n):
            npc = NpcBase()
            npc.place_randomly_avoid_groups(self.walls,self.npcs)
            npc.add(self.npcs,self.sprites)

    def make_dijkstra(self, *goals, fleeing = False):
        #dijkstra map maker - *goals are sprites!
        #fleeing maps make npcs avoid 'goals' instead!

        #these maps are reproduced each action - they are the bottleneck for game speed - so let's reduce maps to only generating within a certain range of the player, rather than for the entire map. this will also allow many npcs to be placed on a map without dooming the player via swarming, AND it will ensure map areas explored later will still have npcs & not be strangely empty.
        width = VIEWPORT_SIZE[0] // TILES + 1
        height = VIEWPORT_SIZE[1] // TILES + 1
        dijx = self.cat.rect.x // TILES - width // 2
        dijy = self.cat.rect.y // TILES - width // 2 + 2


        if fleeing:
            dijkstra = self.make_dijkstra(*goals)
            #negafy the map
            for i in range(HEIGHT):
                for j in range(WIDTH):
                    dijkstra[i][j] = int(-1.2 * dijkstra[i][j])
            #proceed to smooth it out again
        else:
            #init map
            dijkstra = [[255 for j in range(WIDTH)] for i in range(HEIGHT)]
            #set the goals
            for goal in goals:
                x, y, _, _ = goal.rect
                x, y = x // TILES, y // TILES
                dijkstra[y][x] = 0

        #iterate to build flow field
        done = False
        while not done:
            done = True
            for i in range(dijy, dijy + height):
                for j in range(dijx, dijx + width):
                    #floor tiles only
                    try:
                        if self.wall_grid[i][j] == 0:
                            gotoforloop = True
                        else:
                            gotoforloop = False
                    except IndexError:
                        gotoforloop = False
                    if gotoforloop:
                        #look at nearest neighbours of i,j. are they within 1 of i,j? if no, bring them to within 1 & set done = False
                        for d in list(MOVE_KEY.values()):
                            k, l = i + d[1], j + d[0]
                            try:
                                if self.wall_grid[k][l] == 0:
                                    #the meat:
                                    if dijkstra[k][l] > dijkstra[i][j] + 1:
                                        dijkstra[k][l] = dijkstra[i][j] + 1
                                        done = False
                            except IndexError:
                                print('IndexError')

        #situate the dijkstra within the current wall_grid.
        #set out-of-scope walls = 255, paths = (-)127 (if fleeing)
        for i in range(HEIGHT):
            for j in range(WIDTH):
                if dijkstra[i][j] == 255 and self.wall_grid[i][j] == 0:
                        if fleeing:
                            dijkstra[i][j] = -127
                        else:
                            dijkstra[i][j] = 127

        #print map, for testing only
        # for i in range(HEIGHT):
        #     l = ''
        #     for j in range(WIDTH):
        #         p = str(dijkstra[i][j])
        #         for n in range(len(p), 3):
        #             l += ' '
        #         l += p
        #     print(l)

        return dijkstra

    def make_hpbar(self):
        max_health = self.cat.max_health
        health = self.cat.health
        #things in sidebar should be 3tiles wide + 1/2tile border
        surf = pygame.Surface((3 * TILES, TILES // 2))
        surf.set_colorkey(BLACK)
        #background bar
        pygame.draw.rect(surf, PINK, (0, 0, 3 * TILES, TILES // 2))
        #health bar
        hp = int(health / max_health * 3 * TILES)
        pygame.draw.rect(surf, GREEN, (0, 0, hp, TILES // 2))
        #handy text overlay
        txt = str(health) + '  /  ' + str(max_health)
        textsurf = self.status_font.render(txt, False, DKGREY)
        center = (surf.get_width() // 2 - textsurf.get_width() // 2, surf.get_height() // 2 - textsurf.get_height() // 2)
        surf.blit(textsurf, center)
        return surf

    def make_minimap(self):
        surf = pygame.Surface((3 * TILES, 3 * TILES))
        surf.set_colorkey(BLACK)
        #func to maximize map size (pixels sq per game tile)
        #consider WIDTH and HEIGHT // TILES
        z = max(WIDTH, HEIGHT)
        pxpt = int(3 * TILES / z)
        border = 3 * TILES % z // 2
        for i in range(HEIGHT):
            for j in range(WIDTH):
                if self.wall_grid[i][j]:
                    color = DKGREY
                else:
                    color = BEIGE
                pygame.draw.rect(surf, color, (border + j * pxpt, border + i * pxpt,pxpt, pxpt))
        x, y = self.cat.rect.x // TILES, self.cat.rect.y // TILES
        pygame.draw.rect(surf, PINK, (border + x * pxpt, border + y * pxpt,pxpt, pxpt))
        #TODO convert to a map surf that is centered on both axes, in the cases where WIDTH != HEIGHT
        return surf

class Camera():
    def __init__(self):
        self.camframe = pygame.Rect(0, 0, VIEWPORT_SIZE[0], VIEWPORT_SIZE[1])
    def apply(self, sprite):
        return sprite.rect.move(self.camframe.topleft)
    def update(self, player):
        self.camframe = self.bounded_cam_func(player.rect)
    def bounded_cam_func(self, player_rect):
        left, top, pw, ph = player_rect
        _, _, w, h = self.camframe
        l = -left + w//2 -pw//2
        l = min(l, 0)
        l = max(l, w - WIDTH * TILES)
        t = -top + h//2 - ph//2
        t = min(t, 0)
        t = max(t, h - HEIGHT * TILES)
        return pygame.Rect(l, t, w, h)

class Base(pygame.sprite.Sprite):
    def __init__(self, imgfile=None, colour=BLACK):
        super().__init__()
        self.dir = False

        if imgfile:
            self.image = pygame.image.load(imgfile).convert_alpha()
        else:
            self.image = pygame.Surface((TILES,TILES))
            self.image.fill(colour)

        self.rect = self.image.get_rect()

    def move(self, move):
        self.rect = self.rect.move(move[0] * TILES, move[1] * TILES)
        if move[0] > 0:
            self.dir = False
        elif move[0] < 0:
            self.dir = True

    def place(self, place):
        self.rect.topleft = (place[0] * TILES, place[1] * TILES)

    def place_randomly_avoid_groups(self, *args):
        old_rect = self.rect.copy()
        blocked = True
        while blocked:
            blocked = False
            self.place((random.randrange(WIDTH),random.randrange(HEIGHT)))
            for group in args:
                if pygame.sprite.spritecollideany(self, group):
                    blocked = True

    def update(self):
        try:
            if self.dir:
                self.image = self.image_L
            else:
                self.image = self.image_R
        except AttributeError:
            pass

class Cat(Base):
    def __init__(self):
        super().__init__('../images/gamecat.png')

        self.image_R = self.image
        self.image_L = pygame.transform.flip(self.image, True, False)
        self.health = 10
        self.max_health = self.health

    def update(self):
        super().update()

class Wall(Base):
    def __init__(self, x=0, y=0):
        super().__init__(colour = DKGREY)

        self.rect = self.image.get_rect()
        self.rect.x = TILES * x
        self.rect.y = TILES * y

class NpcBase(Base):
    def __init__(self, imgfile='../images/hands/1.png', colour='BLACK'):
        super().__init__(imgfile, colour)

        self.image_R = self.image
        self.image_L = pygame.transform.flip(self.image, True, False)
        self.scratch1 = pygame.image.load("../images/etc/scratch1.png").convert()
        self.scratch1.set_colorkey(BLACK)
        self.scratch2 = pygame.image.load("../images/etc/scratch2.png").convert()
        self.scratch2.set_colorkey(BLACK)

        self.health = random.randrange(5) + 1
        self.max_health = self.health
        self.can_move = True
        self.fleeing = False
        self.following = None

    def move(self, move):
        super().move(move)
        if move[1] != 0 and self.following:
            dif = self.rect.x - self.following.rect.x
            if dif:
                self.dir = dif > 0

    def update(self):
        super().update()
        if self.health < 1:
            self.kill()
        elif self.health <= self.max_health // 2:
            self.fleeing = True
            #blit lv2 scratch img onto self.image
            self.image.blit(self.scratch2, (0, 0))
        elif self.health < self.max_health:
            #blit lv1 scratch img (R/L from self.dir) onto self.image
            self.image.blit(self.scratch1, (0, 0))

    def attack(self, target):
        #for now, let's just make all damage scratch damage - 1d4!
        #in theory we would calc based on the NPCs status etc. here but
        target.health -= random.randrange(4) + 1

class Fragile_Wall(NpcBase):
    def __init__(self, x=0, y=0):
        super().__init__(None, BROWNN)

        self.rect.x = x * TILES
        self.rect.y = y * TILES

        self.can_move = False

class main():
    pygame.init()
    pygame.font.init()
    game = Game()
    pygame.quit()

if __name__ == "__main__":
    main()
