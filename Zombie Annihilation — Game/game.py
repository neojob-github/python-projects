import pygame, sys, random, os, numpy as np
import getpass, json, pandas as pd
from pygame.math import Vector2
from math import floor as to_low

pygame.init()
pygame.font.init()
pygame.mixer.init()

gameSoundtracks = os.listdir('audio/')
bossSoundtracks = os.listdir('boss/')

class Window:
    

    class Floor(pygame.sprite.Sprite):

        def __init__(self,  tileSprite: pygame.surface.Surface, sizeX, sizeY):
            pygame.sprite.Sprite.__init__(self)
            self.image = tileSprite
            self.rect = self.image.get_rect(center=[sizeX * tileSprite.get_size()[0], sizeY * tileSprite.get_size()[1]])

    def __init__(self, windowType: str, mouseVisibility: bool, TPS: int):
        self.windowType = windowType
        self.windowSize = [sizes for sizes in pygame.display.get_desktop_sizes()[0]]
        self.windowName = "Zombie Annihilation"
        self.windowIcon = pygame.display.set_icon(pygame.image.load("icons/icon.png"))
        self.windowBackground =  pygame.transform.scale(pygame.image.load("sprites/back.jpeg"), self.windowSize)
        self.myFonts = [pygame.font.Font("fonts/game_font.ttf", round(self.windowSize[0] / i)) for i in range(1, 80)]
        self.mouseVisibility = pygame.mouse.set_visible(mouseVisibility)
        self.TPS = TPS
        self.screen = pygame.display.set_mode(self.windowSize)
        self.clock = pygame.time.Clock()
        self.playing = True
        self.tileGroup = pygame.sprite.Group()
        pygame.display.set_caption(self.windowName)

    def generateFloor(self, tileSprite: pygame.surface.Surface, tile = Floor):
        for sizeX in range(self.windowSize[0] // tileSprite.get_size()[0] + 1):
            for sizeY in range(self.windowSize[1] // tileSprite.get_size()[1] + 1):
                self.tileGroup.add(tile(tileSprite, sizeX, sizeY))

    

    def gameUpdating(self):
        global points, gameDifficulity
        points = 0
        tiles = self.tileGroup
        
        class Player(pygame.sprite.Sprite):
            def __init__(self):
                pygame.sprite.Sprite.__init__(self)
                __baseSpeed = 2
                self.orig_image = pygame.transform.scale(surface = pygame.image.load("sprites/player/player0.png").convert_alpha(),
                                                         size = [i * (windowSize[0]*windowSize[1])**0.02 for i in pygame.image.load("sprites/player/player0.png").convert_alpha().get_size()])
                self.image = self.orig_image
                self.rect = self.image.get_rect(center=[i/2 for i in windowSize])
                self.speed = windowSize[0] / (windowSize[0] / __baseSpeed) ## BaseSpeed = 6
                self.angle = 0
                self.pos = Vector2([i/2 for i in windowSize])
                self.health = 100
                self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
                self.win = False

            def rotate(self):
                self.mouse_x, self.mouse_y = pygame.mouse.get_pos()
                rel_x, rel_y = self.mouse_x - self.rect.centerx, self.mouse_y - self.rect.centery
                self.angle = -57.3248408 * np.arctan2(rel_y, rel_x)
                self.image = pygame.transform.rotate(self.orig_image, self.angle)
                self.rect = self.image.get_rect(center=self.rect.center)

            def update(self, keys):
                moving = Vector2(0, 0)
                if keys[pygame.K_w] and self.pos.y > 0: 
                    moving.y = -1
                if keys[pygame.K_a] and self.pos.x > 0:  
                    moving.x = -1
                if keys[pygame.K_s] and self.pos.y < windowSize[1]:  
                    moving.y = 1
                if keys[pygame.K_d] and self.pos.x < windowSize[0]:  
                    moving.x = 1
                if moving.length() > 0:
                    self.pos += moving.normalize() * self.speed
                    self.rect.center = self.pos
                enemyEatsPlayer = pygame.sprite.spritecollide(self, enemyGroup, False, pygame.sprite.collide_rect_ratio(0.36))
                enemyBulletsInPlayer = pygame.sprite.spritecollide(self, enemyBulletsGroup, True, pygame.sprite.collide_rect_ratio(0.36))
                for ReasonToDie in [enemyEatsPlayer, enemyBulletsInPlayer]:
                    if ReasonToDie:
                        for reason in ReasonToDie:
                            self.health = round(self.health - reason.damage, 1)
                            if reason.name == "Shrimp":
                                reason.kill()
                        if self.health <= 0:
                            self.kill()
                            writeRecordToFile()
        
        ### MOBS

        class Enemy(pygame.sprite.Sprite):
            def __init__(self, name, enemy_sprite, speed, health, damage, enemy_points, **customArgs):
                pygame.sprite.Sprite.__init__(self)
                ### Kfs to spawn random enemies
                self.name = name
                self.speed = speed * gameDifficulity
                self.health = health * gameDifficulity
                self.damage = damage * gameDifficulity
                self.points = round(enemy_points * gameDifficulity * gameStage) 
                self.orig_image = enemy_sprite
                self.image = enemy_sprite

                for key, value in customArgs.items():
                    self.__setattr__(key, value)
                if self.speed > self.maxSpeed:
                    self.speed = self.maxSpeed

                choiced = random.choice([0, 1])
                if choiced == 0:
                    posx=random.randint(-192, 2112)
                    posy=random.choice([-108, 1188])
                elif choiced == 1:
                    posy=random.randint(-108, 1188)
                    posx=random.choice([-192, 2112])

                self.rect = self.image.get_rect(center=[posx, posy])
                self.pos = Vector2([posx, posy])
                self.rectRatio = 0.6
                if self.name == "Ultimate":
                    self.rectRatio = 0.8
                    self.weaponry = ZombieBeam()
                    self.baseDelay = self.weaponry.delay
                
                
                
            def update(self):
                global points
                ## Rotate to player func
                rel_x, rel_y = player.pos[0] - self.rect.centerx, player.pos[1] - self.rect.centery
                self.angle = -57.3248408 * np.arctan2(rel_y, rel_x)
                self.image = pygame.transform.rotate(self.orig_image, self.angle)
                self.rect = self.image.get_rect(center=self.rect.center)
                direction = (player.pos - self.pos).normalize()
                ## Проверка на движение если игрок не рядом то движение моба приостанавливаем:
                if (self.pos - player.pos).length() > Vector2(self.speed, self.speed).length() * 0.5:
                    self.pos += direction * self.speed
                    self.rect.center = self.pos

                if self.name == "Terrible" and self.health < self.max_health / 2 :
                    self.speed = self.speed * self.rage
                    self.name = "Rage Terrible"
                if self.name == "Ultimate":
                    self.weaponry.delay = self.baseDelay * (self.health/self.max_health) if (self.health/self.max_health) > 1/20 else 100
                    self.weaponry.shoot(self.pos)
                if self.name != "Shrimp":
                    collidedBullet = pygame.sprite.spritecollideany(self, allyBulletsGroup, pygame.sprite.collide_rect_ratio(self.rectRatio))
                    if collidedBullet:
                        collidedBullet.kill() if collidedBullet.name != "LaserBullet" else None
                        if self.health <= weapon.damage:
                            bloodGroup.add(Blood(self.pos, self.rect.size))
                            self.kill()
                            points += self.points
                        self.health -= weapon.damage

        class Zombie(Enemy):
            def __init__(self):
                super().__init__(
                    name="Zombie",
                    enemy_sprite = allEnemySprites[1],
                    speed = 0.28 * gameStage,
                    health = 2 * gameStage,
                    damage = 0.0583 * gameStage,
                    enemy_points = 60,
                    maxSpeed = 1.28
                    )

        class Runner(Enemy):
            def __init__(self):
                super().__init__(
                    name="Runner",
                    enemy_sprite = allEnemySprites[2],
                    speed = 0.56 * gameStage,
                    health = 1 * gameStage,
                    damage = 0.05 * gameStage,
                    enemy_points = 250,
                    maxSpeed = 2.12
                    )

        class Infected(Enemy):
            def __init__(self):
                super().__init__(
                    name="Infected",
                    enemy_sprite = allEnemySprites[3],
                    speed = 0.34 * gameStage,
                    health = 10 * gameStage,
                    damage = 0.16 * gameStage,
                    enemy_points = 650,
                    maxSpeed = 1.38
                    )
                
        class Terrible(Enemy):
            def __init__(self):
                super().__init__(
                    name="Terrible",
                    enemy_sprite = allEnemySprites[4],
                    speed = 0.135 * gameStage,
                    health = 30 * gameStage,
                    damage = 0.3 * gameStage,
                    rage = 2,
                    max_health = 20 * gameStage,
                    enemy_points = 1150,
                    maxSpeed = 1.35
                    )
                
        class Ultimate(Enemy):
            def __init__(self):
                super().__init__(
                    name="Ultimate",
                    enemy_sprite = allEnemySprites[5],
                    speed = 0.8 * gameDifficulity,
                    health = 80000 * gameDifficulity,
                    damage = 100 * gameDifficulity,
                    rage = 3 * gameDifficulity,
                    max_health = 100000 * gameDifficulity,
                    enemy_points = 1000000 * gameDifficulity,
                    maxSpeed = 0.8 * gameDifficulity
                    )        
                
        class Shrimp(Enemy):
            def __init__(self):
                super().__init__(
                    name="Shrimp",
                    enemy_sprite = allEnemySprites[0],
                    speed = 0.45,
                    health = 1,
                    damage = -100 / gameDifficulity,
                    enemy_points = 0,
                    maxSpeed = 0.45
                    )

        ### BULLETS

        class Bullet(pygame.sprite.Sprite):
                def __init__(self,
                            name: str,
                            baseImage: pygame.Surface,
                            rect: pygame.Rect,
                            speed: float,
                            spawnPosition: pygame.math.Vector2,
                            vector: pygame.math.Vector2,
                            targetX: int,
                            targetY: int,
                            **customArgs):
                    
                    pygame.sprite.Sprite.__init__(self)
                    for key, value in customArgs.items():
                        self.__setattr__(key, value) ### BULLETS, DEGREES

                    self.name = name
                    self.orig_image = baseImage
                    self.image = baseImage
                    self.rect = rect
                    self.speed = speed
                    self.pos = spawnPosition
                    self.vec = Vector2.rotate(vector, self.bulletAngle) ### ЭТО НЕ ТО ЧТО НУЖНО. ЗДЕСЬ ДВИЖЕНИЕ СПРАЙТА
                    self.targetX = targetX ### MOUSE X * ?
                    self.targetY = targetY ### MOUSE Y * ?
                    rel_x, rel_y = self.targetX - self.pos[0], self.targetY - self.pos[1]
                    self.angle = -57.3248408 * (np.arctan2(rel_y, rel_x) + np.pi * self.bulletAngle / 180) ### WHATS NEXT????????????
                    self.image = pygame.transform.rotate(self.image, self.angle)
                    self.rect = self.image.get_rect(center=self.rect.center) 
                def move(self): 
                    ## Moving traectory
                    self.pos += self.vec * self.speed
                    self.rect.center = self.pos

                def update(self):
                    if not pygame.sprite.spritecollideany(self, tiles):
                        self.kill()

        class RiffleBullet(Bullet):
            def __init__(self,  bulletAngle):
                super().__init__(
                    name = "RiffleBullet",
                    baseImage = allBulletSprites[0],
                    rect = allBulletSprites[0].get_rect(center=player.pos),
                    speed = player.speed * 12,
                    spawnPosition = Vector2(player.pos),
                    vector = Vector2((player.mouse_x - player.pos[0]), (player.mouse_y - player.pos[1])).normalize(),
                    targetX = player.mouse_x,
                    targetY = player.mouse_y,
                    bulletAngle = np.random.randint(-3, 3) 
                    )

        class ShotgunBullet(Bullet):
            def __init__(self, bulletAngle):
                super().__init__(
                    name = "ShotgunBullet",
                    baseImage = allBulletSprites[1],
                    rect = allBulletSprites[1].get_rect(center=player.pos),
                    speed = player.speed * 11,
                    spawnPosition = Vector2(player.pos),
                    vector = Vector2((player.mouse_x - player.pos[0]), (player.mouse_y - player.pos[1])).normalize(),
                    targetX = player.mouse_x,
                    targetY = player.mouse_y,
                    bulletAngle = bulletAngle         
                    )
                
        class LaserBullet(Bullet):
            def __init__(self, bulletAngle):
                super().__init__(
                    name = "LaserBullet",
                    baseImage = allBulletSprites[2],
                    rect = allBulletSprites[2].get_rect(topleft=player.pos),
                    speed = player.speed * 7,
                    spawnPosition = Vector2(player.pos),
                    vector = Vector2((player.mouse_x - player.pos[0]), (player.mouse_y - player.pos[1])).normalize(),
                    targetX = player.mouse_x,
                    targetY = player.mouse_y,
                    bulletAngle = bulletAngle         
                    )
                
        class ZombieBullet(Bullet):
            def __init__(self, bulletAngle, customSpawnPos):
                super().__init__(
                    name = "ZombieBullet",
                    baseImage = allBulletSprites[3],
                    rect = allBulletSprites[3].get_rect(center=customSpawnPos),
                    speed = 5 * gameDifficulity,
                    spawnPosition = Vector2(customSpawnPos),
                    vector = Vector2((player.pos.x - customSpawnPos[0]), (player.pos.y - customSpawnPos[1])).normalize(),
                    targetX = player.pos.x,
                    targetY = player.pos.y,
                    bulletAngle = bulletAngle,
                    damage = 100 * gameDifficulity
                    )

        ### WEAPONS

        class Weapon():
            def __init__(self,
                        name: str,
                        bulletAffiliation: str,
                        bulletType: str,
                        velocity: float,
                        bulletCount: int,
                        damage: float,
                        bulletClass: object,
                        bulletAngle: float,
                        weaponUpCost: int):
                self.name = name
                self.bulletAffiliation = bulletAffiliation
                self.bulletClass = bulletClass
                self.bulletType = bulletType
                self.bulletCount = bulletCount
                self.velocity = velocity ## shots per second
                self.shoot_time = pygame.time.get_ticks()
                self.delay = 1000 / self.velocity
                self.damage = damage
                self.bulletAngle = bulletAngle
                self.weaponUpCost = weaponUpCost * gameDifficulity
                self.level = 0

            def shoot(self, customSpawnPos = None):
                current_time = pygame.time.get_ticks()
                # We're ready to fire when 100 ms have passed.
                if current_time - self.shoot_time > self.delay:
                    bulletAngle = 0.0
                    for bullet in range(1, to_low(self.bulletCount)+1):
                        self.shoot_time = current_time
                        if self.bulletAffiliation == "Ally":
                            allyBulletsGroup.add(self.bulletClass(bulletAngle))
                        elif self.bulletAffiliation == "Enemy":
                            enemyBulletsGroup.add(self.bulletClass(bulletAngle, customSpawnPos))
                        if bulletAngle <= 0:
                            bulletAngle += self.bulletAngle * bullet
                        else:
                            bulletAngle -= self.bulletAngle * bullet
                        
            def upgrade(self, **upgradeMods):
                global points
                if self.level < 10:
                    if self.weaponUpCost <= points:
                        points = round(points - self.weaponUpCost)        
                        try: ### grading bullet count in shot
                            lbc = self.bulletCount
                            self.bulletCount += upgradeMods["newBullets"]
                            self.bulletAngle = self.bulletAngle * lbc / self.bulletCount
                            
                        except:
                            None
                        try: ### grading power in shot
                            self.damage *= upgradeMods["power"]

                        except:
                            None
                        try: ### grading velocity in shot
                            self.delay *= 1/upgradeMods["velocity"]

                        except:
                            None
                        self.level += 1
                        self.weaponUpCost = round(self.weaponUpCost * 1.65)
                if self.level == 10:
                    self.weaponUpCost = "MAX"
                        
        class Riffle(Weapon):
            def __init__(self):
                super().__init__(
                    name = "Пулемёт",
                    bulletType ="bullet",
                    bulletAffiliation = "Ally",
                    velocity = 6, ## shots per second
                    damage = 6,
                    bulletClass = RiffleBullet,
                    bulletCount = 1,
                    bulletAngle = 0.0,
                    weaponUpCost = 2500
                    )
            def upgrade(self):
                return super().upgrade(
                    power = 1.3,
                    velocity = 1.2,
                    newBullets = 0
                )
            
        class Shotgun(Weapon):
            def __init__(self):
                super().__init__(
                    name = "Дробовик",
                    bulletType="bullet",
                    bulletAffiliation = "Ally",
                    velocity = 2, ## shots per second
                    damage = 4.5,
                    bulletClass = ShotgunBullet,
                    bulletCount = 3,
                    bulletAngle = 10.0,
                    weaponUpCost = 2500
                    )
            def upgrade(self):
                return super().upgrade(
                    power = 1.2,
                    velocity = 1.125,
                    newBullets = 0.5
                )
                
        class Laser(Weapon):
            def __init__(self):
                super().__init__(
                    name = "Лазер",
                    bulletType="line",
                    bulletAffiliation = "Ally",
                    velocity = 1, ## shots per second
                    damage = 1,
                    bulletClass = LaserBullet,
                    bulletCount = 2,
                    bulletAngle = 180.0,
                    weaponUpCost = 2500
                    )
            def upgrade(self):
                return super().upgrade(
                    power = 1.25,
                    velocity = 1.08,
                    newBullets = 1
                )
            
        class ZombieBeam(Weapon):
            def __init__(self):
                super().__init__(
                    name = "Zombeam",
                    bulletType="line",
                    bulletAffiliation = "Enemy",
                    velocity = 0.5 * gameDifficulity, ## shots per second
                    damage = 100,
                    bulletClass = ZombieBullet,
                    bulletCount = 1,
                    bulletAngle = 0.0,
                    weaponUpCost = 0
                    )

        ### ADDITIONS

        class Crosshair(pygame.sprite.Sprite):
            def __init__(self):
                pygame.sprite.Sprite.__init__(self)
                self.image = pygame.image.load("sprites/crosshair/crosshair.png").convert_alpha()
                self.image = pygame.transform.scale(self.image, size=[i*2 for i in self.image.get_size()])
                self.rect = self.image.get_rect()
            
            def update(self, mousePos):
                self.rect.center = mousePos

        class Blood(pygame.sprite.Sprite):
            def __init__(self, spawnPos, deadSize):
                pygame.sprite.Sprite.__init__(self)
                self.image = pygame.transform.rotozoom(allEnemySprites[-1], random.randint(0, 180), deadSize[0] / allEnemySprites[-1].get_size()[0])
                self.timer = 60
                self.rect = self.image.get_rect(center=spawnPos)
            
            def update(self):
                self.timer -= 1
                if self.timer < 1:
                    self.kill()
                 
        

        def playerScore(screen):
            global points
            try:
                if points > weapon.weaponUpCost:
                    textColor = "#ffd700"
                else:
                    textColor = "#FFFFF0"
            except:
                textColor = "#FFFFF0"
            font = pygame.font.Font("fonts/game_font.ttf", round(windowSize[0] / 26.6))
            text = font.render(f'Очки: {points}', True, textColor)
            screen.blit(text, (0, windowSize[1]-text.get_size()[1]))

        def infoGameStage(screen):
            font = pygame.font.Font("fonts/game_font.ttf", round(windowSize[1] / 26.6))
            text = font.render(f'Сложность: {round(gameStage, 1)}', True, 'white')
            screen.blit(text, (0, windowSize[1]-windowSize[1]//30 - 2*text.get_size()[1]))

        def infoPlayerHealth(screen):
            font = pygame.font.Font("fonts/game_font.ttf", round(windowSize[1] / 26.6))
            text = font.render(f'Здоровье: {player.health}', True, 'white')
            screen.blit(text, (windowSize[0]-windowSize[0]//5, windowSize[1]-windowSize[1]//30))

        def infoRebootMessage(screen):
            font = pygame.font.Font("fonts/game_font.ttf", round(windowSize[0] / 26.6))
            phrase1, color1 = f"Ты погиб!", "#ff2400"
            phrase2, color2 = f"Для рестарта жми 'R'!", "#ff2400"
            text = font.render(phrase1, True, color1)
            screen.blit(text, (windowSize[0]/2.5, windowSize[1]/2))
            text = font.render(phrase2, True, color2)
            screen.blit(text, (windowSize[0]/3.5, windowSize[1]/2 + text.get_size()[1]))

        def writeRecordToFile():
            global recorded
            recorded = True
            with open("records.json", "r+", encoding="UTF-8") as records:
                data = json.load(records)
                records_df = pd.DataFrame.from_dict(data, orient='columns')
                df = pd.DataFrame([{"name" : getpass.getuser(), "points" : str(points)}])
                merged = pd.DataFrame.merge(records_df, df, how='outer')
                pd.DataFrame.to_json(merged, "records.json")
        
        def infoAboutWeapon(screen):
            weaponInfoTextSizes = (windowSize[0]-windowSize[0]//7.5, windowSize[1]-windowSize[1]*0.99)
            weaponInfoTextSizes2 = (windowSize[0]-windowSize[0]//7.5, windowSize[1]-windowSize[1]*0.95)
            weaponInfoTextSizes3 = (windowSize[0]-windowSize[0]//7.5, windowSize[1]-windowSize[1]*0.91)
            font = pygame.font.Font("fonts/game_font.ttf", round(windowSize[1] / 26.6))
            text = font.render(f'{weapon.name}', True, (0, 255, 60))
            screen.blit(text, weaponInfoTextSizes)
            text = font.render(f'Урон:{round(weapon.damage, 1)}', True, (0, 255, 60))
            screen.blit(text, (weaponInfoTextSizes2))
            text = font.render(f'UP:{weapon.weaponUpCost}', True, (0, 255, 60))
            screen.blit(text, (weaponInfoTextSizes3))

        def playthroughEnds(screen):
            font = pygame.font.Font("fonts/game_font.ttf", round(windowSize[0] / 26.6))
            phrase1, color1 = f"С победой!", "#42aaff"
            phrase2, color2 = f"Ты набрал {points} очк.", "#42aaff"
            text = font.render(phrase1, True, color1)
            screen.blit(text, (windowSize[0]/5, windowSize[1]/3))
            text = font.render(phrase2, True, color2)
            screen.blit(text, (windowSize[0]/10, windowSize[1]/3 + text.get_size()[1]))
            enemyGroup.empty()

        def music(gameSoundtracks):
            if not pygame.mixer.music.get_busy():
                    random.shuffle(gameSoundtracks)
                    pygame.mixer.music.load(f"audio/{gameSoundtracks[0]}")
                    pygame.mixer.music.set_volume(0.02)
                    pygame.mixer.music.play()
                

        backpack = [Riffle(), Shotgun(), Laser()]
        firstWeaponID = 0 ### -1 0 1
        lastWeaponID = len(backpack) - 1

        ID = firstWeaponID
        weapon = backpack[ID]

        ## Weapon upgrading

        startTime, endTime = pygame.time.get_ticks(), pygame.time.get_ticks()
        upgradingTime = 300

        ### Game parameters
        points = 0
        gameStage, wave_interval, progressSpeed = 1, 2350 / gameDifficulity, 0.03125 * gameDifficulity  ## Base params: 1, 0, 2500 ЧЕМ БОЛЬШЕ ТЕМ ЛЕГЧЕ, 0.025 ЧЕМ БОЛЬШЕ ТЕМ БЫСТРЕЕ ПРОГРЕСС
        next_wave_time = pygame.time.get_ticks() + wave_interval
        maxGameStage = 30
        allEnemySprites = [pygame.transform.scale(sprite, size=[xy * (self.windowSize[0]*self.windowSize[1])**0.075 for xy in sprite.get_size()]) for sprite in [pygame.image.load(f"sprites/enemies/{spriteName}").convert_alpha() for spriteName in os.listdir('sprites/enemies/')]]
        allBulletSprites = [pygame.image.load(f"sprites/objects/{sprite}").convert_alpha() for sprite in os.listdir('sprites/objects/')]

        windowSize = self.windowSize
        
        playerGroup = pygame.sprite.Group()
        enemyGroup = pygame.sprite.Group()
        cursorGroup = pygame.sprite.Group()
        bloodGroup = pygame.sprite.Group()
        allyBulletsGroup = pygame.sprite.Group()
        enemyBulletsGroup = pygame.sprite.Group()

        player = Player()
        playerGroup.add(player)
        cursorGroup.add(Crosshair())

        ### MAIN GAME LOOP

        pygame.mouse.set_visible(False)

        bossWave = False
        recorded = False

        while self.playing:
            self.clock.tick(self.TPS)
            self.mousePos, self.mousePress, self.keyPress, self.allEvents =  pygame.mouse.get_pos(), pygame.mouse.get_pressed(), pygame.key.get_pressed(), pygame.event.get()
            for event in self.allEvents:
                if event.type == pygame.QUIT:
                    self.playing = False
                    closeWindow()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and player.health <= 0:
                        game()
                    if event.key == pygame.K_ESCAPE:
                        self.playing = False
                        mainMenu()
                if event.type == pygame.MOUSEWHEEL: ### ВЫБОР ПУШКИ
                    ID += event.y
                    if ID > lastWeaponID:
                        ID = firstWeaponID
                    elif ID < firstWeaponID:
                        ID = lastWeaponID
                    weapon = backpack[ID]
            if self.keyPress[pygame.K_SPACE]:
                endTime = pygame.time.get_ticks()
                if endTime - upgradingTime > startTime:
                    weapon.upgrade()
                    startTime = endTime
            if self.mousePress[0] and player.health > 0:
                weapon.shoot()
            if self.mousePos != [player.mouse_x, player.mouse_y]:
                player.rotate()
            if self.keyPress[pygame.K_1]:
                ID = 0
                weapon = backpack[ID]
            if self.keyPress[pygame.K_2]:
                ID = 1
                weapon = backpack[ID]
            if self.keyPress[pygame.K_3]:
                ID = 2
                weapon = backpack[ID]

            ### ENEMY WAVES

            if pygame.time.get_ticks() >= next_wave_time and player.health > 0:
                next_wave_time += wave_interval / (gameStage ** (0.66))
                if gameStage >= maxGameStage:
                    gameStage = maxGameStage
                else:
                    gameStage += progressSpeed
                generatedEnemy = random.choices([Shrimp(), Zombie(), Runner(), Infected(), Terrible()], [1.0, 100.0, 10.0, 1.0, 0.5])[0]
                enemyGroup.add(generatedEnemy)
            if bossWave == False and gameStage > 25: #### 25
                bossWave = True
                boss = Ultimate()
                enemyGroup.add(boss)
                random.shuffle(bossSoundtracks)
                pygame.mixer.music.load(f"boss/{bossSoundtracks[0]}")
                pygame.mixer.music.play()
                bossArrived = pygame.image.load("sprites/bossArrived.png").convert_alpha()
                bossArrived = pygame.transform.scale(bossArrived, size=self.windowSize)
            if bossWave == True:
                if boss.alive() == False:
                    player.win = True
            ### UPDATES AND DRAWINGS

            playerGroup.update(self.keyPress)
            enemyGroup.update()
            [bullet.move() for bullet in allyBulletsGroup]
            allyBulletsGroup.update()
            [bullet.move() for bullet in enemyBulletsGroup]
            enemyBulletsGroup.update()
            cursorGroup.update(self.mousePos)
            bloodGroup.update()
            music(gameSoundtracks)

            self.tileGroup.draw(self.screen)
            bloodGroup.draw(self.screen)
            allyBulletsGroup.draw(self.screen)
            playerGroup.draw(self.screen)
            enemyGroup.draw(self.screen)
            enemyBulletsGroup.draw(self.screen)
            cursorGroup.draw(self.screen)
            if bossWave == True:
                self.screen.blit(bossArrived, (0, 0))

            playerScore(self.screen)
            infoPlayerHealth(self.screen)
            infoAboutWeapon(self.screen)
            infoGameStage(self.screen)
            infoRebootMessage(self.screen) if player.health <= 0 and player.win == False else None
            if player.win:
                writeRecordToFile() if not recorded else None
                self.screen.fill("black")
                playthroughEnds(self.screen)
            pygame.display.flip()
##########################################
##########################################
##########################################
##########################################
##########################################
##########################################
    def mainMenuUpdating(self):

        class Button(pygame.sprite.Sprite):
            def __init__(self, posx, posy, buttonText: str, onclickFunction, windowSize, fontsize, onePress=False):
                pygame.sprite.Sprite.__init__(self)
                self.x = posx
                self.y = posy
                self.onclickFunction = onclickFunction
                self.onePress = onePress
                self.font = pygame.font.Font("fonts/game_font.ttf", round(windowSize[0] * fontsize * 0.001))
                self.buttonText = buttonText
                self.buttonSurf = self.font.render(buttonText, True, (190, 0, 0))
                self.buttonRect = self.buttonSurf.get_rect(x=posx, y=posy)
                self.alreadyPressed = False
                buttonsGroup.append(self)

            def update(self, mousePos, allEvents):
                self.buttonSurf = self.font.render(self.buttonText, True, (190, 0, 0))
                if self.buttonRect.collidepoint(mousePos):
                    self.buttonSurf = self.font.render(self.buttonText, True, (255, 255, 255))
                    for event in allEvents:
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            self.buttonSurf = self.font.render(self.buttonText, True, (255, 180, 0))
                            if self.onePress:
                                self.onclickFunction()

                            elif not self.alreadyPressed:
                                self.onclickFunction()
                                self.alreadyPressed = True
                        else:
                            self.alreadyPressed = False



        def title(self):
            font = pygame.font.Font("fonts/game_font.ttf", round(self.windowSize[0] / 20))
            text = font.render(f'Zombie Annihilation', True, (255,0,4))
            self.screen.blit(text, (self.windowSize[0]/4.5, self.windowSize[1]/8))

        titleFontTabulation = (self.windowSize[0] / 20) * 1.5
        baseFontSize = 40

        buttonsGroup = []
        Button(self.windowSize[0] / 4,
               self.windowSize[1] / 8 + titleFontTabulation,
               'Новая игра',
               onclickFunction=difficulitySelect,
               windowSize=self.windowSize,
               fontsize=baseFontSize)
        
        Button(self.windowSize[0] / 4,
               self.windowSize[1] / 8 + titleFontTabulation * 2,
               'Рекорды',
               onclickFunction=records,
               windowSize=self.windowSize,
               fontsize=baseFontSize)
        
        Button(self.windowSize[0] / 4,
               self.windowSize[1] / 8 + titleFontTabulation * 3,
               'Выход',
               onclickFunction=closeWindow,
               windowSize=self.windowSize,
               fontsize=baseFontSize)

        while self.playing:
            self.clock.tick(self.TPS)
            self.mousePos, self.mousePress, self.keyPress, self.allEvents =  pygame.mouse.get_pos(), pygame.mouse.get_pressed(), pygame.key.get_pressed(), pygame.event.get()
            for event in self.allEvents:
                if event.type == pygame.QUIT:
                    self.playing = False
                    closeWindow()
            self.screen.blit(self.windowBackground, (0, 0))
            for button in buttonsGroup:
                button.update(self.mousePos, self.allEvents)
                self.screen.blit(button.buttonSurf, (button.x, button.y))
            title(self)
            pygame.display.flip()
##########################################
##########################################
##########################################
##########################################
##########################################
##########################################
    def recordsUpdating(self):

        class Button(pygame.sprite.Sprite):
            def __init__(self, posx, posy, buttonText: str, onclickFunction, windowSize, fontsize, onePress=False):
                pygame.sprite.Sprite.__init__(self)
                self.x = posx
                self.y = posy
                self.onclickFunction = onclickFunction
                self.onePress = onePress
                self.font = pygame.font.Font("fonts/game_font.ttf", round(windowSize[0] * fontsize * 0.001))
                self.buttonText = buttonText
                self.buttonSurf = self.font.render(buttonText, True, (190, 0, 0))
                self.buttonRect = self.buttonSurf.get_rect(x=posx, y=posy)
                self.alreadyPressed = False
                buttonsGroup.append(self)
            
            def update(self, mousePos, allEvents):
                self.buttonSurf = self.font.render(self.buttonText, True, (190, 0, 0))
                if self.buttonRect.collidepoint(mousePos):
                    self.buttonSurf = self.font.render(self.buttonText, True, (255, 255, 255))
                    for event in allEvents:
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            self.buttonSurf = self.font.render(self.buttonText, True, (255, 180, 0))
                            if self.onePress:
                                self.onclickFunction()

                            elif not self.alreadyPressed:
                                self.onclickFunction()
                                self.alreadyPressed = True
                        else:
                            self.alreadyPressed = False
        
        def title(self):
            font = pygame.font.Font("fonts/game_font.ttf", round(self.windowSize[0] / 20))
            text = font.render(f'Зал славы', True, (255,0,4))
            self.screen.blit(text, (self.windowSize[0]/4.5, self.windowSize[1]/8))


        def playerRecords(self):
            with open("records.json", "r+", encoding="UTF-8") as records:
                font = pygame.font.Font("fonts/game_font.ttf", round(self.windowSize[0] * 40 * 0.001))
                posx, posy, n = self.windowSize[0]/3, self.windowSize[1]/4, 1
                data = json.load(records)
                records_df = pd.DataFrame.from_dict(data, orient='columns')
                for record in list(sorted(records_df.values, key=lambda x: round(float(x[1])), reverse=True))[:5]:
                    text = font.render(f'{n}. {record[0]} — {record[1]}', True, (250, 180, 0))
                    text_size = text.get_size()[1]
                    if posy - self.windowSize[1]/4 > self.windowSize[1]/4 + (5*text_size):
                        n = 1
                        posy = self.windowSize[1]/4
                    else:
                        posy += text_size
                        n += 1
                    self.screen.blit(text, (posx, posy))

        def resetRecords():
            with open("records.json", "w", encoding="UTF-8") as records:
                data = {"name":{},"points":{}}
                records_df = pd.DataFrame.from_dict(data, orient='columns')
                pd.DataFrame.to_json(records_df, "records.json")

        titleFontTabulation = (self.windowSize[0] / 20) * 1.5
        baseFontSize = 40
        buttonsGroup = []

        Button(self.windowSize[0] / 1.2,
               self.windowSize[1] / 5 * 4.5,
               'Назад',
               onclickFunction=mainMenu,
               windowSize=self.windowSize,
               fontsize=baseFontSize)
        
        Button(0 ,
               self.windowSize[1] / 5 * 4.5,
               'Очисить рекорды',
               onclickFunction=resetRecords,
               windowSize=self.windowSize,
               fontsize=baseFontSize)

        while self.playing:
            self.clock.tick(self.TPS)
            self.mousePos, self.mousePress, self.keyPress, self.allEvents =  pygame.mouse.get_pos(), pygame.mouse.get_pressed(), pygame.key.get_pressed(), pygame.event.get()
            for event in self.allEvents:
                if event.type == pygame.QUIT:
                    self.playing = False
                    closeWindow()
            self.screen.blit(self.windowBackground, (0, 0))
            for button in buttonsGroup:
                button.update(self.mousePos, self.allEvents)
                self.screen.blit(button.buttonSurf, (button.x, button.y))
            title(self)
            playerRecords(self)

            pygame.display.flip()
##########################################
##########################################
##########################################
##########################################
##########################################
##########################################
    def difficulitySelectUpdating(self):

        class Button(pygame.sprite.Sprite):
            def __init__(self, posx, posy, buttonText: str, onclickFunction, windowSize, fontsize, colors: list, onePress=False):
                pygame.sprite.Sprite.__init__(self)
                self.x = posx
                self.y = posy
                self.onclickFunction = onclickFunction
                self.onePress = onePress
                self.font = pygame.font.Font("fonts/game_font.ttf", round(windowSize[0] * fontsize * 0.001))
                self.buttonText = buttonText
                self.buttonSurf = self.font.render(buttonText, True, colors)
                self.buttonRect = self.buttonSurf.get_rect(x=posx, y=posy)
                self.alreadyPressed = False
                self.buttonColors = colors
                buttonsGroup.append(self)

            def update(self, mousePos, allEvents):
                self.buttonSurf = self.font.render(self.buttonText, True, self.buttonColors)
                if self.buttonRect.collidepoint(mousePos):
                    self.buttonSurf = self.font.render(self.buttonText, True, (255, 255, 255))
                    for event in allEvents:
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            self.buttonSurf = self.font.render(self.buttonText, True, (255, 180, 0))
                            if self.onePress:
                                self.onclickFunction()

                            elif not self.alreadyPressed:
                                self.onclickFunction()
                                self.alreadyPressed = True
                        else:
                            self.alreadyPressed = False

        def title(self):
            font = pygame.font.Font("fonts/game_font.ttf", round(self.windowSize[0] / 20))
            text = font.render(f'Уровень сложности:', True, (255,0,4))
            self.screen.blit(text, (self.windowSize[0]/4.5, self.windowSize[1]/8))

        titleFontTabulation = (self.windowSize[0] / 20) * 1.5
        baseFontSize = 40
        buttonsGroup = []

        Button(self.windowSize[0] / 4,
               self.windowSize[1] / 8 + titleFontTabulation,
               'Легко',
               onclickFunction=setEasy,
               windowSize=self.windowSize,
               fontsize=baseFontSize,
               colors=[51, 255, 17])
        
        Button(self.windowSize[0] / 4,
               self.windowSize[1] / 8 + titleFontTabulation * 2,
               'Нормально',
               onclickFunction=setMedium,
               windowSize=self.windowSize,
               fontsize=baseFontSize,
               colors=[255, 170, 0])
        
        Button(self.windowSize[0] / 4,
               self.windowSize[1] / 8 + titleFontTabulation * 3,
               'Трудно',
               onclickFunction=setHard,
               windowSize=self.windowSize,
               fontsize=baseFontSize,
               colors=[255, 0, 60])

        while self.playing:
            self.clock.tick(self.TPS)
            self.mousePos, self.mousePress, self.keyPress, self.allEvents =  pygame.mouse.get_pos(), pygame.mouse.get_pressed(), pygame.key.get_pressed(), pygame.event.get()
            for event in self.allEvents:
                if event.type == pygame.QUIT:
                    self.playing = False
                    closeWindow()
            self.screen.blit(self.windowBackground, (0, 0))
            for button in buttonsGroup:
                button.update(self.mousePos, self.allEvents)
                self.screen.blit(button.buttonSurf, (button.x, button.y))
            title(self)
            pygame.display.flip()
        
##########################################
##########################################
##########################################
##########################################
##########################################
##########################################

def generateTileImage():
    return pygame.image.load(f"sprites/tiles/256x256/{random.choice(os.listdir('sprites/tiles/256x256/'))}").convert_alpha()

def mainMenu():
    pygame.mixer.music.stop()
    activeWindow = Window("mainMenu", True, 60)
    activeWindow.mainMenuUpdating()

def records():
    activeWindow = Window("records", True, 60)
    activeWindow.recordsUpdating()

def difficulitySelect():
    activeWindow = Window("difficulitySelect", True, 60)
    activeWindow.difficulitySelectUpdating()


def game():
    gameWindow = Window("game", True, 600)
    gameWindow.generateFloor(generateTileImage())
    gameWindow.gameUpdating()

def closeWindow():
    pygame.quit()
    sys.exit()

def setEasy():
    global gameDifficulity
    gameDifficulity = 0.80
    game()

def setMedium():
    global gameDifficulity
    gameDifficulity = 1.0
    game()

def setHard():
    global gameDifficulity
    gameDifficulity = 1.20
    game()

points = 0
gameDifficulity = 0
mainMenu()



    


