#Some code taken From CMU 15-112 Fall 2015 course
### Website: http://www.cs.cmu.edu/~112/index.html
from Animation import Animation # Edited from CMU 15-112 Fall 2015
from SustainableBuilder import * #Import All classes that game uses.



class Simulator(Animation):

    def init(self): ### NEED MODE OF HOUSE AND SHED############
        self.timerFiredDelay = 250 # Milliseconds
        self.mode = 'splashScreen'
        self.visitedModes = []
        self.second = 1000//self.timerFiredDelay
        self.groundY = 3*self.height//4
        self.gameOver = False
        self.panelImage = self.importImage('../GifAssets/SolarCell.gif')
        self.artImages = [self.importImage('../GifAssets/FlowerPainting.gif'),
                            self.importImage('../GifAssets/PeaceIcon.gif')]
        self.rainIcon = self.importImage('../GifAssets/Raincloud.gif')
        self.sunIcon = self.importImage('../GifAssets/SunIcon.gif')
        self.fruitImages = {'apple': self.importImage('../GifAssets/AppleIcon.gif')}
        self.playerImages = [self.importImage('../GifAssets/PlayerLookRight.gif'),
                                self.importImage('../GifAssets/PlayerLookLeft.gif')]
        self.player = Player(self) # actions, attributes
        self.world = World(self.player) # contains objects and attributes
        self.openWorldInit()
        self.computerInit()

    def mousePressed(self, event):
        if self.mode == 'splashScreen': self.splashScreenMousePressed(event)
        elif self.mode == 'openWorld': self.openWorldMousePressed(event)
        elif self.mode == 'craft': self.craftMousePressed(event)
        elif self.mode == 'playerHouse': self.houseMousePressed(event)
        elif self.mode ==  'computer': self.computerMousePressed(event)
        elif self.mode == 'browser': self.browserMousePressed(event)


    def keyPressed(self, event):
        if self.mode == 'splashScreen': self.splashScreenKeyPressed(event)
        elif self.mode == 'openWorld': self.openWorldKeyPressed(event)
        elif self.mode == 'craft': self.craftKeyPressed(event)
        elif self.mode == 'playerHouse': self.houseKeyPressed(event)
        elif self.mode ==  'computer': self.computerKeyPressed(event)
        elif self.mode == 'browser': self.browserKeyPressed(event)

    def timerFired(self):
        if self.mode == 'splashScreen': self.splashScreenTimerFired()
        elif self.mode == 'openWorld': self.openWorldTimerFired()
        elif self.mode == 'craft': self.craftTimerFired()# stopTime
        elif self.mode == 'playerHouse': self.openWorldTimerFired()
        elif self.mode ==  'computer': self.computerTimerFired() # losePower
        elif self.mode == 'browser': self.craftTimerFired()# stopTime

    def redrawAll(self):
        if self.mode == 'splashScreen': self.splashScreenRedrawAll()
        elif self.mode == 'openWorld': self.openWorldRedrawAll()
        elif self.mode == 'craft': self.craftRedrawAll()
        elif self.mode == 'playerHouse': self.houseRedrawAll()
        elif self.mode ==  'computer': self.computerRedrawAll()
        elif self.mode == 'browser': self.browserRedrawAll()

    def switchMode(self, toMode):
        self.visitedModes.append(self.mode)
        self.mode = toMode

    def goToPrevMode(self):
        if self.visitedModes != []:
            self.mode = self.visitedModes.pop()

###################################################################
#                               MODES
###################################################################

################
#SplashScreen
################

    def splashScreenMousePressed(self, event): pass

    def splashScreenKeyPressed(self, event):
        if event.keysym == '1':
            self.switchMode('openWorld')

    def splashScreenTimerFired(self):
        if self.gameOver:
            self.init()

    def drawTitle(self):
        self.canvas.create_text(self.width//2, self.height//4,
        text = 'Sustainable Builder', font = 'Helvetica 32 bold',
        fill = 'darkgreen')

    def drawButtons(self): pass

    def drawInstructions(self):
        yOffset = self.height//8
        xPlace = self.width//2
        self.canvas.create_text(xPlace,yOffset*3,
            text = 'press 1 for QuickStart game ')

    def splashScreenRedrawAll(self):
        self.world.drawBackground(self)
        self.drawTitle()
        self.drawInstructions()

################
#Craft TODO Implement craft Screen
################
    def drawResources(self):
        self.player.drawInventory(self)
        j = 0
        for i,resource in enumerate(self.player.resources):
            i %= 4 # columns of 4
            if i % 4 == 0:
                j += 1 # when a col is full start new row
            i += 1 # from 1 to 4 inclusive
            (wX0, wY0, wX1, wY1) = self.player.invCoords
            xOffset = (wX1 - wX0)//6
            yOffset = (wY1 - wY0)//4
            image = self.importImage(resource.iconPath)
            resource.drawInInv(wX0 + i*xOffset, wY0 + j*yOffset, xOffset,
                                yOffset, image)
    def craftMousePressed(self, event): pass

    def craftKeyPressed(self, event):
        if event.keysym == 'Escape':
            self.switchMode('splashScreen')

        elif event.keysym == 'BackSpace':
            self.goToPrevMode()


    def craftTimerFired(self): pass

    def craftRedrawAll(self):
        self.world.shed.drawIn()

################
#OpenWorld
################
    def openWorldInit(self):
        self.genStep = self.width//self.player.step
        self.timerCount = 0
        self.iWieldCount = 0
        self.rightNewStepCount = 1 # rightward steps in new terrain
        self.leftNewStepCount = 1 # leftward steps in new terrain

    def updateSteps(self, d):
        gs = self.genStep
        if d > 0:
            self.rightNewStepCount += 1
            if self.rightNewStepCount % gs == 0: self.generateMoreWorld()
        else:
            self.leftNewStepCount += 1
            if self.leftNewStepCount % gs == 0: self.generateMoreWorld()
        # similar ifs are not in or statment to avoid false positives
        # (ie player went right just enough and then goes left)

    def generateMoreWorld(self):
        # called when player moves equivalent of window width in new direction
        self.world.generateTree()

    def openWorldMousePressed(self, event): pass

    def openWorldKeyPressed(self, event):
        if event.keysym == 'Escape':
            self.switchMode('splashScreen')

        elif self.gameOver: return

        elif event.keysym == 'Left':
            self.player.walk(-1)
            if self.player.updateVisitedTerrain():
                self.updateSteps(-1)

        elif event.keysym == 'Right':
            self.player.walk(1)
            if self.player.updateVisitedTerrain():
                self.updateSteps(1)

        elif event.keysym == 'e':
            for building in self.world.buildings:
                if self.player.enterBuilding(building):
                    self.switchMode(building.inside())
                    break
        elif event.keysym == 'i':
            self.player.toggleInv()

        elif event.keysym == 'f':
            self.player.eat()

        elif event.keysym == 'd':
            self.player.drink()

        elif event.keysym == 'w':
            maxI = len(self.player.wieldables)
            if maxI > 0:
                self.iWieldCount += 1
                wieldAtI = self.iWieldCount % maxI
                self.player.wield(wieldAtI)

        elif event.keysym == 'p':
            if self.player.wielding != None:
                self.player.placeInWorld()

        elif event.keysym == 'c':
            self.player.chop(self.world.trees)

        elif event.keysym == 'g':
            self.player.pickFruit(self.world.trees)


    def openWorldTimerFired(self):
        if not self.player.alive:
            self.gameOver = True
            return
        self.timerCount += 1
        #update daylightOffset for all Drawn Classes
        Drawn.updateDaylightOffset(self.world.adjustWorldColor())
        if self.timerCount % self.second == 0:
            seconds = self.world.tick()
            #Player gets hungry  and thirsty over time
            if seconds % (self.world.dayLength//6) == 0: # 6 times a day
                self.player.thirst()
                if seconds % (self.world.dayLength//3) == 0: # 3 times a day
                    self.player.hunger()
        if self.world.raining:
            self.world.moveRain() #move rain cloud

    def drawGameOver(self):
        self.canvas.create_text(self.width//2, self.height//2, anchor= 's',
                        text = 'Game Over', font = 'Helvetica 40', fill = 'red')
        self.canvas.create_text(self.width//2, self.height//2,
                        font = 'Helvetica 25', fill = 'darkred',
                        text = 'press the escape key to go to start screen')
    def openWorldRedrawAll(self):
        self.world.draw()
        self.player.draw() # draw last to keep in foreground
        if self.player.displayInv:
            self.drawInv()
        if self.gameOver:
            self.drawGameOver()

    def drawInv(self):
        self.player.drawInventory(self)
        j = 0
        for i,resource in enumerate(self.player.resources):
            i %= 4 # columns of 4
            if i % 4 == 0:
                j += 1 # when a col is full start new row
            i += 1 # from 1 to 4 inclusive
            (wX0, wY0, wX1, wY1) = self.player.invCoords
            xOffset = (wX1 - wX0)//6
            yOffset = (wY1 - wY0)//4
            image = self.importImage(resource.iconPath)
            resource.drawInInv(wX0 + i*xOffset, wY0 + j*yOffset, xOffset,
                                yOffset, image)

################
#inHouse
################

    def houseMousePressed(self, event): pass

    def houseKeyPressed(self, event):
        if event.keysym == 'Escape':
            self.switchMode('splashScreen')

        if self.gameOver: return

        elif event.keysym == 'Left':
            self.player.walk(-1)

        elif event.keysym == 'Right':
            self.player.walk(1)

        elif event.keysym == 'r':
            for thing in self.world.house.objects:
                if self.player.interact(thing):
                        self.switchMode(thing.name)
                #else display text with key function.

        elif event.keysym == 'BackSpace':
                self.goToPrevMode()

        elif event.keysym == 'f':
            self.player.eat()

        elif event.keysym == 'd':
            self.player.drink()

    def houseRedrawAll(self):
        self.world.house.drawIn()
        for thing in self.world.house.objects:
            image = self.importImage(thing.iconPath)
            thing.drawExt(image)
        self.player.draw()
        if self.gameOver:
            self.drawGameOver()

################
#Computer
################
    def computerInit(self):
        self.appsOpen = []

    def computerMousePressed(self, event):
        if self.world.house.computer.hasPower:
            computer = self.world.house.computer
            for icon in computer.icons:
                if icon.iconClicked(event.x, event.y):
                    self.appsOpen.append(icon)
                    break
            if computer.browserIcon in self.appsOpen:
                for resource in self.player.resources:
                    if resource.moreButton.isClicked(event.x, event.y):
                        resource.selling += 5
                    elif (resource.lessButton.isClicked(event.x, event.y)
                                                    and resource.selling > 0):
                        resource.selling -= 5
                for merch in computer.browserIcon.buyMerch:
                    if merch.moreButton.isClicked(event.x, event.y):
                        merch.buying += 1
                    elif (merch.lessButton.isClicked(event.x, event.y)
                                    and merch.buying > 0):
                        merch.buying -= 1

                for button in computer.browserIcon.buttons:
                   if button.isClicked(event.x, event.y):
                        if button.txt == 'Sell':
                            for resource in self.player.resources:
                                transact = resource.price * resource.selling
                                empty = resource.lose(transact)
                                if not empty:
                                    self.player.myMoney.gain(transact)
                        elif button.txt == 'Buy':
                            for merch in computer.browserIcon.buyMerch:
                                merch.buy(self.player, merch.buying)


    def computerKeyPressed(self, event):
        if event.keysym == 'BackSpace':
            if self.appsOpen != []:
                self.appsOpen.pop()
            else:
                self.goToPrevMode()

    def computerTimerFired(self):
        timerPerDay = self.world.dayLength*self.second
        # usage for a full power meter is a day of being on the computer
        pwrUsage = self.player.power.cap/(timerPerDay)
        use = self.player.usePower(pwrUsage)
        if not use:
            self.world.house.computer.turnOff()
            for i in range(len(self.appsOpen)):
                self.appsOpen.pop()


    def drawSell(self, app):
        money = self.player.myMoney
        money.drawInInv(3*self.width//4, self.height//10, self.width//8,
                        self.height//8, self.importImage(money.iconPath))
        for i,resource in enumerate(app.sellMerch):
            if i == 3: return # don't draw money
            (wX0, wY0, wX1, wY1) = app.windowCoords
            wWidth, wHeight = (wX1 - wX0, wY1 - wY0)
            xStart =wY0 + (5*wWidth//8)
            width = wWidth//4
            height = wHeight//8
            yOffset = wWidth//8
            image = self.importImage(resource.iconPath)
            resource.drawInMerchScreen(xStart, wY0 + (i+1)*yOffset, width,
                                            height, image)

    def drawBuy(self, app):
        for merch in app.buyMerch:
            (wX0, wY0, wX1, wY1) = app.windowCoords
            wWidth, wHeight = (wX1 - wX0, wY1 - wY0)
            xStart =wY0 + wWidth//8
            width = wWidth//4
            height = wHeight//8
            yOffset = wWidth//6
            image = self.importImage(merch.iconPath)
            merch.drawInMerchScreen(xStart, wY0 + yOffset, width, height,
                                        image)




    def computerRedrawAll(self):
        self.world.house.computer.drawIn()
        if self.world.house.computer.hasPower:
            for app in self.world.house.computer.icons:
                image = self.importImage(app.iconPath)
                app.drawExt(self, image)
            for app in self.appsOpen:
                if app.name == 'inventory':
                    self.drawInv()
                else:
                    app.drawIn(self) # app is browser
                    self.drawSell(app)
                    self.drawBuy(app)



################
#Browser
################
    def browserMousePressed(self, event): pass

    def browserKeyPressed(self, event): pass

    def browserRedrawAll(self, event): pass
        # draw buy icon, sell icon

################
#Inventor
################

simulation = Simulator()
simulation.run(900,700)
