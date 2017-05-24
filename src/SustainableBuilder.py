#Emilio Vargas-Vite
#evargasv, Section I, 15-112
# Fall 2015 Term Project
### Some code taken From CMU 15-112 Fall 2015 course
### Website: http://www.cs.cmu.edu/~112/index.html
### Took: Animation Class, rgbString Method, scroll Implementation
## I do not own any of the images used in this program
# Player sprite from :
# http://www.picgifs.com/graphics/walking/graphics-walking-859804-821606/

from random import random, choice, randint
from math import sin, pi

class Drawn(object):
    # light offset passes the time to all Drawn children to represent day time
    daylightOffset = 1
    #game = none # init in player

    @staticmethod  #from CMU 15-112
    def rgbString(red, green, blue, outside = False): #edited to suit game
        offset = lambda x: __class__.daylightOffset * x if outside else x
        return "#%02x%02x%02x" % (offset(red),offset(green), offset(blue))


    @staticmethod
    def updateDaylightOffset(colorOffset):
        minDayLight = 0.15 # set minimum rgb product
        __class__.daylightOffset = max(colorOffset, minDayLight)

class GameAttribute(Drawn):

    def __init__(self, owner, value, cap = None , name = None, kind = None):
        self.kind = kind
        self.owner = owner
        self.cap = cap
        self.value = value
        self.name = name
        self.addToList()

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, GameAttribute) and (self.kind == other.kind)

    def addToList(self):
        if self.name.endswith('stat'):
            self.owner.stats.append(self)
        else:
            self.owner.resources.append(self)


    def isEmpty(self):
        if self.value <= 0:
            return True
        return False

    def lose(self, loss):
        empty = self.isEmpty()
        if not empty and self.value >= loss:
            self.value -= loss
        return self.value < loss


    def gain(self, gain):
        if self.cap == None or self.value < self.cap:
            self.value += gain
        else:
            self.value = self.cap

    def getValue(self):
        return self.value

class MyButton(Drawn):
        def __init__(self, x0 , y0, width, height, text = None, color = None,
                            font = None):
            self.x0 = x0
            self.y0 = y0
            self.width = width
            self.height = height
            self.x1 = self.x0 + width
            self.y1 =self.y0 + height
            self.txt = text
            self.font = font
            self.color = color

        def draw(self, game):
            game.canvas.create_rectangle(self.x0, self.y0, self.x1, self.y1,
                fill = self.color)
            game.canvas.create_text(self.x0 + self.width/2,
                            self.y0 + self.height/2,
                            text = self.txt, font = self.font)

        def isClicked(self, x, y):
            if x>=self.x0 and x<=self.x1 and y<=self.y1 and y>= self.y0:
                return True
            return False

###################################################################
#                               Player
###################################################################

class Player(Drawn):
    '''Creates player with all actions and attributes'''

    def __init__(self, game):
        self.game = game
        self.lookRightIcon = game.playerImages[0]
        self.lookLeftIcon = game.playerImages[1]
        self.dir = 'right'
        self.walking = False
        self.screenInsteps = 30# 30 steps to move accross screen
        self.step = game.width//self.screenInsteps
        self.displayInv = False
        self.wieldables = []
        self.specialItems = []
        self.itemsPlaced = []
        self.wielding = None

        #Define position and dimensions
        self.xPos = self.step * 10 # arbitrary
        self.yPos = self.game.groundY
        self.width  = self.lookRightIcon.width()
        self.height = self.lookRightIcon.height()
        self.xScrollMargin = self.width + 20 # min distance from canvas edge
        self.xScroll = 0 # amount scrolled (right increase), (left decrease)
        self.curX = self.xPos - self.xScroll # actuall player xPos on screen
        self.xVisited =  {0, game.width} # set of visited x coords in world

        #Initialize player stats
        self.alive = True
        self.stats = []
        # does not kill player
        self.power = GameAttribute(self, 100, 100, 'Powerstat', kind = 'power')
        #essential
        self.food = GameAttribute(self, 20, 20, 'Foodstat', kind = 'food')
        #essential
        self.water = GameAttribute(self, 30, 30, 'Waterstat', kind = 'water')
        #Initialize player Resources
        self.resources = []
        self.myWater = playerResource(self, self.water.value*3, name ='myWater',
                                kind = 'water',  iconPath = '../GifAssets/WaterIcon.gif')
        self.myFood = playerResource(self, self.food.value*3, name ='myFood',
                                    kind = 'food',iconPath = '../GifAssets/FoodIcon.gif')
        self.myWood = playerResource(self, 40, name ='myWood', kind = 'wood',
                                        iconPath = '../GifAssets/WoodIcon.gif')
        self.myMoney = playerResource(self, 100, name = 'myMoney',
                                    kind ='money',iconPath = '../GifAssets/MoneyIcon.gif')
        self.mySeeds = None #Seeds()
        self.myLeaves = None #Leaves



    def walk(self, d): # Scroll implementation From CMU's 15-112
        #changes player's x position and updates xScroll
        sx= self.xScroll
        self.dir = 'right' if d > 0 else 'left'
        canvasWidth = self.game.width
        self.xPos += (d * self.step)
        if self.xPos < sx + self.xScrollMargin :
           self.xScroll = self.xPos - self.xScrollMargin
        elif self.xPos > sx + canvasWidth - self.xScrollMargin:
            self.xScroll = self.xPos - canvasWidth + self.xScrollMargin
        self.curX = self.xPos - sx

    def updateVisitedTerrain(self):
        # returns True if in new terrain, and updates xVisited
        vx = self.xVisited
        if self.xPos not in set(range(min(vx), max(vx), self.step)):
        # only add new positions, max/min has step to skip unnecessary values
            self.xVisited.add(self.xPos)
            return True
        return False

    def enterBuilding(self, building):
        # has to be 2 steps away from left of player
        xDoor = building.x1 - self.xScroll
        if xDoor <= self.curX and xDoor >= self.curX - (2*self.step):
            return True
        return False

    def interact(self, thing):
        if thing.x1 >= self.curX and thing.x0 <= self.curX:
            return True
        return False

    def wield(self, i):
        self.wielding = self.wieldables[i]

    def placeInWorld(self):
        print(self.wieldables, 'before')
        if self.wielding != None:
            self.itemsPlaced.append((self.wielding, self.xPos))
            self.wieldables.remove(self.wielding)
            self.wielding = None
        print(self.wieldables, 'after')
        print(self.wielding, 'wielding')


    def chop(self, trees):
        '''Optimization for onScreen only trees is not great,
    because I would still need to loop over the entire treelist,
    make a smaller list, and then loop through that one again.
    It's better to just loop through the tree list and compare xCoordinates'''
        for tree in trees:
            if tree.x1 >= self.xPos and tree.x0 <= self.xPos:
                tree.chopped()
                if tree.integrity <= 0:
                    for resource in tree.resources:
                        for myResource in self.resources:
                            if resource == myResource:
                                myResource.gain(resource.value)
                    trees.remove(tree)
                break

    def pickFruit(self, trees):
        for tree in trees:
            if (isinstance(tree, FruitTrees) and tree.x1 >= self.xPos
                    and tree.x0 <= self.xPos):
                value = tree.picked()
                self.myFood.gain(value)

    def hunger(self):
        empty = self.food.lose(1)
        if empty: #empty
            self.alive = False

    def thirst(self):
        empty = self.water.lose(1)
        if empty: #empty
            self.alive = False


    def eat(self):
        if not self.myFood.isEmpty():
            self.myFood.lose(1)
            self.food.gain(1)

    def drink(self):
        if not self.myWater.isEmpty():
            self.myWater.lose(1)
            self.water.gain(1)

    def usePower(self, output):
        empty = self.power.lose(output)
        if empty:
            return False
        return True

    def drawStat(self, game, stat, i):
        barWidth = game.width//4
        barHeight = game.height//20
        x0 = 5
        y0 = 10
        yOffset = x0 + barHeight * i # brings next stat lower
        # Draw Encasing box
        barOutline = (x0,yOffset, x0 + barWidth, yOffset + barHeight)
        game.canvas.create_rectangle(*barOutline, width = 2)
        # Draw Colored bar to indicate actual value
        colors = ['yellow', 'orange', 'blue']
        statStatus = stat.getValue()/stat.cap
        statBar = (x0, yOffset, x0 + barWidth * statStatus, yOffset + barHeight)
        game.canvas.create_rectangle(*statBar, fill = colors[i], width = 0)
        # Draw Text To indicate what stat is
        game.canvas.create_text(x0, yOffset, text = str(stat).strip('stat'),
                                    anchor = 'nw')

    def drawPlayer(self, game):
        if self.dir == 'right':
            self.curImage = self.lookRightIcon
        else: self.curImage = self.lookLeftIcon
        game.canvas.create_image(self.curX, self.yPos,
                                    anchor = 'se',  image = self.curImage)
    def toggleInv(self):
        self.displayInv = not self.displayInv

    def drawInventory(self, game):
        (xMargin, yMargin) = (game.width//8, game.height//8)
        self.invCoords = (xMargin, yMargin, game.width - xMargin,
                                                    game.height - yMargin)
        game.canvas.create_rectangle(*self.invCoords, fill = 'grey')

        #yiconOffset =
        #for i,resource in enumerate(self.resources):

            #resource.drawInInv()


    def draw(self):
        game = self.game
        self.drawPlayer(game)
        for i,stat in enumerate(self.stats):
            self.drawStat(game, stat, i)
        #if self.wielding != None:
            #self.wielding.drawEx(game, sx)

class playerResource(GameAttribute):
    PRICES = {'water': 4, 'food': 5, 'wood': 3, 'money':0}
    def __init__(self, owner, value, cap = None , name = None, kind = None,
                    iconPath = None):
        super().__init__(owner,value, cap, name, kind)
        self.game = self.owner.game
        self.iconPath = iconPath
        self.price = __class__.PRICES[self.kind]
        self.selling = 0
        self.moreButton = MyButton(0, 0, 0, 0, 'Dummy')
        self.lessButton = MyButton(0, 0, 0, 0, 'Dummy')#will create when drawing

    def drawInInv(self, x0, y0, width, height, image):
        canvas = self.game.canvas
        canvas.create_rectangle(x0, y0, x0+width, y0+height)
        self.image = image # need reference
        display = 'Amount: %d' % (self.value)
        canvas.create_text(x0, y0 + self.image.height() ,anchor = 'nw',
                            text = display)
        canvas.create_image(x0, y0, anchor = 'nw', image = self.image)

    def drawInMerchScreen(self, x0, y0, width, height, image):
        canvas = self.game.canvas
        self.image = image #need reference
        display = str(self.selling)
        textXOffset = 10
        canvas.create_text(x0 + self.image.width() + textXOffset,
                            y0 + height//2, anchor = 'w', text = display)
        canvas.create_text(x0 + self.image.width() + textXOffset*2,
            y0 + height//2, anchor = 'w', text = '$' + str(self.price))

        canvas.create_image(x0, y0, anchor = 'nw', image = self.image)
        buttonW, buttonH = width//4, height//2
        self.moreButton = MyButton(x0 + width-buttonW, y0, buttonW, buttonH,
        'MORE', 'green')
        self.lessButton = MyButton(x0 + width-buttonW, y0 + buttonH, buttonW,
                                    buttonH, 'LESS', 'red')
        self.moreButton.draw(self.game)
        self.lessButton.draw(self.game)



###################################################################
#                               World
###################################################################

class World(Drawn):

    def __init__(self, player):
        self.game = player.game
        # set up time
        minute = 60
        self.secondCount = 0
        self.todaySecCount = 0
        self.dayStage = 'day'
        self.dayTimeFrac = 0
        self.dayCount = 0
        self.dayLength = 0.5* minute
        # set up the player
        self.player = player
        # make world and set environmental variables
        self.makeWorld()
        self.newDay()
        self.setTreeDensity(4)
        self.raining = False
        self.rainIcon = self.game.rainIcon
        self.rainx0 = 0
        self.sunIcon = self.game.sunIcon
        self.sunY0 = self.game.groundY


    def makeWorld(self):
        self.trees = [Trees(self,self.game.width, 3) ,
                        FruitTrees(self, 5*self.game.width//3, 3, 'apple')]
        self.buildings = []
        self.house = House(self, 0, 2*self.game.width//3,
                            2*self.game.height//3, 'playerHouse')

        self.shed = Shed(self, -5*self.game.width//6,
                            self.game.width//3, self.game.height//2, 'craft')

    def rollProbability(self):
        self.prob = [1]+[2]+[3]*3 + [4]*3 + [5]*2 + [6]*2 +[7]+[8]
        return choice(self.prob)

    def newDay(self):
        self.dayCount += 1
        self.sunIntensity = self.rollProbability()
        self.rainProbability = self.rollProbability()/max(self.prob) # 0 to 1
        self.setRainTime()
        for tree in self.trees:
            tree.grow()

    def setRainTime(self):
        if self.rainProbability > 0.15: # any lower means no rain that day
            duration = round(self.rainProbability * self.dayLength)
            self.rainStart = randint(0, self.dayLength - duration)
            self.rainEnd = self.rainStart + duration
        else:
            self.rainStart = self.rainEnd = None

    def setDayLen(self, length):pass

    def setTreeDensity(self, maxTreesPerScreen):
        self.treeDensity = maxTreesPerScreen

    def generateTree(self):
        newTreeXs = set()
        pX = self.player.xPos
        xPositive = pX > 0 # true if headed right
        # roll variables
        rollNumTrees = randint(1,4)
        # xOffset so with max tree width so they  don't overlap
        xOffset = self.game.width//(Trees.width*Trees.ageCap)
        xDir = 1 if xPositive else -1 # going left is negative x
        for tree in range(rollNumTrees):
            # random distance from player
            def rollTreeX():
                return xDir * randint(1, Trees.width*Trees.ageCap)
            xFactor = rollTreeX()
            if xFactor * xOffset + pX in newTreeXs:
                xFactor = rollTreeX() # roll untill unique x is found
            treeX = xFactor * xOffset # placement in new scree
            selectTreeRoll = randint(1,10)
            age = randint(1, Trees.ageCap-2)
            if selectTreeRoll <= 7: # Prob = 0.7
                self.trees.append(Trees(self, pX + treeX, age))
            else: # Prob = 0.3
                self.trees.append(FruitTrees(self, pX + treeX, age, 'apple'))

    def tick(self):
        '''advances time in game, returns current second count'''
        self.secondCount += 1
        self.todaySecCount = self.secondCount % self.dayLength
        if self.todaySecCount == 0: self.newDay()
        if self.rainStart and self.todaySecCount == self.rainStart:
            self.raining = True
        elif self.rainStart and self.todaySecCount == self.rainEnd:
            self.raining = False
        if self.todaySecCount <= self.dayLength//3: # split day in thirds
            self.dayStage = 'day'
            self.moveSun(1)
            self.chargePannels(1)
        elif self.todaySecCount <= 2*self.dayLength//3:
            self.dayStage = 'afternoon'
            self.moveSun(-1)
            self.chargePannels(2)
        else:
            self.dayStage = 'night'
        if self.raining:
            self.player.myWater.gain(1)
        return self.secondCount

    def adjustWorldColor(self): # called in Simulator.py in openWorldTimerFired
        #Calculates product for rgb values of objects outside due to day/night
        self.dayTimeFrac = self.game.timerCount/(self.dayLength*
                                                            self.game.second)
        # only need first half of sin graph, so multiply by pi, not 2pi
        adjustTimeColor = self.dayTimeFrac * pi
        phaseShift = pi/6 # don't want to start day at darkest point.
        myDayNightFunction = lambda t, C: abs(sin(t + C)) # yay for trig
        return myDayNightFunction(adjustTimeColor, phaseShift)

    def moveRain(self):
        rainStep = 5
        self.rainx0 += rainStep
        if self.rainx0 + self.rainIcon.width() >= self.game.width:
            self.rainx0 = 0

    def moveSun(self, d):
        yInterval = self.game.height - self.game.groundY # height of sky
        # step through yInterval in one third of day, two thirds is up and down
        step = 2*yInterval//(self.dayLength//3)
        if d > 0:
            self.sunY0 -= step # move up screen
        else:
            self.sunY0 += step # move down screen

    def drawBackground(self, game):
        skyBlue = self.rgbString(135, 206, 255, True)
        groundGreen = self.rgbString(0,201,87, True)
        # Draw Sky
        game.canvas.create_rectangle(0,0,self.game.width, self.game.height,
                                        fill = skyBlue)
        # Draw Ground
        game.canvas.create_rectangle(0, game.groundY, self.game.width,
                                        self.game.height, fill = groundGreen)

    def drawRain(self, game):
        game.canvas.create_image(self.rainx0, game.height//8, anchor = 'w',
                                    image = self.rainIcon)

    def drawSun(self, game):
        game.canvas.create_image(3*game.width//4, self.sunY0, anchor = 's',
                                    image = self.sunIcon)

    def chargePannels(self, chargePerSec):
        for item,xPos in self.player.itemsPlaced:
            if isinstance(item, SolarCells):
                item.charge(self.player, chargePerSec)

    def draw(self):
        game = self.game
        sx = self.player.xScroll
        self.drawBackground(game)
        if self.dayStage != 'night':
            self.drawSun(game)
        for building in self.buildings:
            building.drawExt(game, sx)
        for tree in self.trees:
            tree.draw(sx)
        for item,xPos in self.player.itemsPlaced:
            item.drawExt(game,xPos, sx)
        if self.raining:
            self.drawRain(game)


##################
#Outside Objects
##################

class GameObjects(Drawn):
    def __init__(self, world, x0, width, height, name):
        self.world = world # for dimensions, and time
        self.owner = self.world.player
        self.game = self.owner.game
        self.name = name
        self.width = width
        self.height = height
        self.x0 = x0
        self.x1 = self.x0 + width

    def __repr__(self):
        return self.name

    def getBounds(self):
        return (self.x0, self.y0, self.x1, self.y1)




 #######################WHAT I WILL WORK ON TODAY

class Trees(GameObjects):
    counter = 0
    ageCap = 6
    (width, height) = (10, 30)
    def __init__(self, world, x0, age):
        __class__.counter += 1
        self.count = __class__.counter
        self.age = age
        self.size = self.age* randint(2,4) # roll
        self.woodProcuct = randint(1,5) # roll
        super().__init__(world, x0, self.size * __class__.width,
            self.size * __class__.height, 'tree%d' % self.count)
        self.resources = []
        self.wood = GameAttribute(self, self.size*self.woodProcuct,
                                kind = 'wood', name= 'tree%dWood' % self.count)
        self.integrity = age

    def grow(self):
        # increase wood, and leaves.
        if self.age < __class__.ageCap:
            oldSizeRoll = self.size/self.age # get old size roll
            self.age += 1
            self.size = oldSizeRoll * self.age
            self.wood.gain(self.woodProcuct) # increase wood by change in size
            self.width = self.size * __class__.width
            self.height = self.size * __class__.height # recalculate dimensions
            self.x1 = self.x0 + self.width

    def chopped(self):
        self.integrity -= 1

    def draw(self, sx):
        game = self.game
        leafColor = self.rgbString(58, 95, 11, True)
        trunkColor = self.rgbString(165, 100, 6, True)
        self.y0, self.y1 = self.game.groundY - self.height, game.groundY
        xOffset = self.width//3
        yOffset = self.height//3
        #draw Trunk
        trunkX0, trunkX1 = self.x0 + xOffset, self.x1 - xOffset
        game.canvas.create_rectangle(trunkX0 - sx, self.y1 - yOffset,
                                    trunkX1 - sx, self.y1, fill = trunkColor)
        # draw greenery
        leavesCoords = [
                (self.x0 - sx, self.y1 - yOffset),
                (trunkX0 - sx, self.y0 +yOffset),
                (self.x0 - sx, self.y0 +yOffset),
                (self.x0 - sx + self.width/2, self.y0),
                (self.x1 - sx, self.y0 + yOffset),
                (trunkX1 - sx, self.y0 + yOffset),
                (self.x1 - sx, self.y1 - yOffset)]
        game.canvas.create_polygon(leavesCoords, fill = leafColor)

class FruitTrees(Trees):
    # map fruits to values
    FRUITS= {'apple': 3, 'orange': 3, 'apricot': 2, 'cherry': 1,}
    def __init__(self, world, x0, age, fruit):
        super().__init__(world, x0, age)
        self.fruit = fruit
        self.fruitImage = self.game.fruitImages[self.fruit]
        self.fruitNumber = min(self.size, 8) # max 8 fruits
        self.foodValue = __class__.FRUITS[self.fruit]
        self.food = GameAttribute(self, self.fruitNumber * self.foodValue,
             name= 'tree%dWood' % self.count,  kind = 'food')

    def picked(self):
        if self.fruitNumber>0:
            self.fruitNumber -= 1
            self.food.lose(self.foodValue)
            return self.foodValue
        return 0

    def grow(self):
        super().grow()
        self.fruitNumber = min(self.fruitNumber +1, 8) # keep max, regen fruit

    def drawFruit(self, sx):
        xOffset = self.width//4
        yOffset = self.height//3
        j = 0
        for i in range(self.fruitNumber):
            i %= 4 # columns of 4
            if i % 4 == 0:
                j += 1 # when a col is full start new row
            self.game.canvas.create_image((self.x0 + i*xOffset) - sx,
                    self.y1 - j*yOffset, anchor = 's', image = self.fruitImage)

    def draw(self, sx):
        super().draw(sx)
        self.drawFruit(sx)

class SolarCells(Drawn):
    counter = 0
    def __init__(self, world):
        __class__.counter += 1
        self.count = __class__.counter
        self.price = 100
        self.iconPath = '../GifAssets/SolarCellIcon.gif'
        self.world = world
        timeOffset = Drawn.daylightOffset
        self.buying = 0

    def __repr__(self):
        return ('SolarCell %d' % self.count)

    def buy(self, player, amount):
        if amount <= 0:
            return
        else:
            if player.myMoney.value >= self.price:
                player.myMoney.lose(self.price)
                player.wieldables.append(SolarCells(self.world))
            self.buy(player, amount - 1)

    def charge(self, player, n):
        player.power.gain(n)
        print(player.power.value)

    def drawExt(self, game, x0, sx):
        self.x0 = x0
        game.canvas.create_image(self.x0 - sx, game.groundY,
                                    image = game.panelImage)


    def drawInMerchScreen(self, x0, y0, width, height, image):
        canvas = self.world.game.canvas

        self.image = image #need reference
        display = str(self.buying)
        textXOffset = 10
        canvas.create_text(x0 + self.image.width() + textXOffset,
                            y0 + height//2, anchor = 'w', text = display)
        canvas.create_text(x0 + self.image.width() + 2*textXOffset,
                            y0 + height//2, anchor = 'w',
                            text ='$'+ str(self.price))
        canvas.create_image(x0, y0, anchor = 'nw', image = self.image)
        buttonW, buttonH = width//4, height//2
        self.moreButton = MyButton(x0 + width-buttonW, y0, buttonW, buttonH,
        'MORE', 'green')
        self.lessButton = MyButton(x0 + width-buttonW, y0 + buttonH, buttonW,
                                    buttonH, 'LESS', 'red')
        self.moreButton.draw(self.world.game)
        self.lessButton.draw(self.world.game)

##################
#Structures
##################
class Structure(GameObjects):
    def __init__(self, world, x0, width, height, name): # windows
        super().__init__(world, x0, width, height, name)
        #self.windows = windows ADD WINDOWS
        world.buildings.append(self)

    def __repr__(self):
        return self.name

    def inside(self): # called when entering building to switch mode
        return self.name

    # When in openWorld, Draw exterior
    def drawExt(self, game, sx):
        mainY0 = game.groundY - 2*self.height/3
        roofY0 = game.groundY - self.height
        windowWidth = self.width//6
        windowHeight = self.height//5
        self.drawMain(game, self.x0 - sx, mainY0, self.x1 - sx, game.groundY)
        self.drawRoof(game, self.x0 - sx, roofY0, self.x1 - sx, mainY0)
        #self.drawWindow(game, windowWidth, windowHeight)

    def drawMain(self, game, x0, y0, x1, y1,):
        color = self.rgbString(139, 105, 20, True)
        game.canvas.create_rectangle(x0, y0, x1, y1, fill = color)


    def drawRoof(self, game, x0, y0, x1, y1):
        color =  self.rgbString(107, 66, 38, True)
        xOffset = abs(x0 - x1)//8 # for trapezium shape
        polygonCoords = [(x0-xOffset,y1), (x0+xOffset,y0), (x1-xOffset,y0),
                            (x1+xOffset,y1)]
        game.canvas.create_polygon(polygonCoords,fill = color)

    def drawWindow(self, game, wWidth, wHeight):
        #for window in range(self.windows): Draw window
            pass

    # When inside, Draw interior
    def drawIn(self):
        ''' For House: workbench, bed, computer, fridge'''
        game = self.world.game
        wallColor = self.rgbString(139, 105, 20)
        game.canvas.create_rectangle(0,0, game.width, game.height,
                                       fill = wallColor)


class Shed(Structure):
    def __init__(self, world, x0, width, height, name):  # windows
        super().__init__(world, x0, width, height, name)

    def drawIn(self):
        super().drawIn()
        self.drawSideBars(self.game)
        self.drawTable(self.game)
        self.drawText(self.game)

    def drawText(self, game):
        game.canvas.create_text(5,0, text = 'toolBar', anchor = 'nw',
            font = 'Helvetica 22')
        game.canvas.create_text(5*game.width//6,0, text = 'Materials',
            anchor = 'nw', font = 'Helvetica 22')

    def drawSideBars(self, game):
        game.canvas.create_rectangle(0,0, game.width//6, 2*(game.height//3),
            fill = 'brown')
        game.canvas.create_rectangle(5*game.width//6,0, game.width, game.height,
            fill = 'brown')

    def drawTable(self, game):
        tableColor = self.rgbString(133, 87, 35)
        game.canvas.create_rectangle(game.width//6,0, 5*game.width//6,
            game.height, fill= tableColor)

class House(Structure):
    def __init__(self, world, x0, width, height, name): # windows
        super().__init__(world, x0, width, height, name)
        self.computer = Computer(world, self.game.width//3, self.game.width//8,
                        self.game.height//15, 'computer', '../GifAssets/ComputerIcon.gif')
        self.objects = [self.computer]
        self.flowerPainting = self.game.artImages[0]
        self.peacePainting = self.game.artImages[1]

    def drawIn(self):
        super().drawIn()
        game = self.game
        game.canvas.create_image(game.width//4, game.height//2,
                                    image = self.flowerPainting)
        game.canvas.create_image(3*game.width//4, 2*game.height//3,
                                    image = self.peacePainting)

####################
# Computer
####################


class Computer(GameObjects):
    def __init__(self, world, x0, width, height, name, iconPath = None):
        super().__init__(world, x0, width, height, name)
        self.screenColor = self.rgbString(102, 178, 255)
        self.y0 = self.owner.yPos - self.owner.height
        self.iconPath = iconPath
        self.icons = []
        iconOffset = self.game.height//8
        iconX0 = self.game.width//15
        self.browserIcon = BrowserIcon(self, iconX0, iconOffset, 'browser',
                                    '../GifAssets/BrowserIcon.gif')
        self.inventoryIcon = CompIcon(self, iconX0, 3*iconOffset, 'inventory',
            '../GifAssets/Inventory.gif')
        self.hasPower = True

    def turnOff(self):
        self.hasPower = False

    def drawIn(self):
        # draw Background
        self.drawBackground(self.game)
        self.owner.drawStat(self.game, self.owner.power, 0) # draw power stat

        # icons are drawn in computerRedrawAll in simulator.py

    def drawBackground(self, game):
        if self.hasPower:
            game.canvas.create_rectangle(0,0, game.width, game.height,
                                        fill = self.screenColor)
        else: # draw black screen
            game.canvas.create_rectangle(0,0, game.width, game.height,
                                        fill = 'black')


    def drawExt(self, image):
        self.image = image # need reference
        self.game.canvas.create_image(self.x0, self.y0, image = self.image)

class CompIcon(Drawn):
    def __init__(self, computer, x0, y0, name, iconPath = None):
        self.iconPath = iconPath
        self.x0 = x0
        self.y0 = y0
        self.name = name
        computer.icons.append(self)
        self.game = computer.game
        self.world = computer.world
        self.margin = computer.game.width//8
        self.windowCoords = (0 + self.margin, 0 + self.margin,
            self.game.width - self.margin, self.game.height - self.margin)

    def __repr__(self):
        return self.name

    def iconClicked(self, x, y):
            width = self.image.width()
            height = self.image.height()
            if (x>=self.x0 and x<=self.x0 + width and y<=self.y0 + height and
                        y >= self.y0):
                return True
            return False

    def drawIn(self, game): # draw 'Application' contents
        windowColor = self.rgbString(0, 51, 102)
        game.canvas.create_rectangle(*self.windowCoords, fill = windowColor)
        for button in self.buttons:
            button.draw(self.game)


    def drawExt(self, game, image): #draw icon in desktop screen
        self.image = image # need reference to redraw
        game.canvas.create_image(self.x0, self.y0, anchor = 'nw',
                                image = self.image)

class BrowserIcon(CompIcon):
    def __init__(self, computer, x0, y0, name, iconPath = None):
        super().__init__(computer, x0, y0, name, iconPath)
        self.buttons = []
        self.player = self.world.player
        self.createButtons()
        self.sellMerch = [resource for resource in self.player.resources]
        solarCell = SolarCells(self.world)
        self.buyMerch = [solarCell]

    def createButtons(self):
        (wX0, wY0, wX1, wY1) = self.windowCoords
        wWidth, wHeight = (wX1 - wX0, wY1 - wY0)
        self.buyButton(wX0, wY0, wX1, wY1, wWidth, wHeight)
        self.sellButton(wX0, wY0, wX1, wY1, wWidth, wHeight)

    def buyButton(self, wX0, wY0, wX1, wY1, wWidth, wHeight):
        self.merchColor = self.rgbString( 153, 204, 255)
        buy = MyButton(wX0 + wWidth//6, wY0, wWidth//6,
            wHeight//6, text = 'Buy', color = self.merchColor,
            font = 'Helvetica 24')

        self.buttons.append(buy)

    def sellButton(self, wX0, wY0, wX1, wY1, wWidth, wHeight):
        sell = MyButton(wX0 + 3*wWidth//6, wY0, wWidth//6,
                        wHeight//6, text = 'Sell', color = self.merchColor,
                        font = 'Helvetica 24')
        self.buttons.append(sell)

class Garden(Structure):
    def __init__(self, world, x0, width, height, name):
        pass
