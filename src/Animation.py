from tkinter import *

class Animation(object): # Animation Class from CMU 15-112 (edited)
    # Override these methods when creating your own animation
    def mousePressed(self, event): pass
    def keyPressed(self, event): pass
    def timerFired(self): pass
    def init(self): pass
    def redrawAll(self): pass

    @staticmethod
    def Label(text,**wars):
        return Button(master, **wars)
    
    @staticmethod
    def importImage(imagePath):
        return PhotoImage(file = imagePath)
    
    # Call app.run(width,height) to get your app started
    def run(self, width=300, height=300):
        # create the root and the canvas
        root = Tk()
        self.width = width
        self.height = height
        self.canvas = Canvas(root, width=width, height=height)
        self.canvas.pack()
        running = True

        # set up events
        def redrawAllWrapper():
            self.canvas.delete(ALL)
            self.redrawAll()
            self.canvas.update()

        def mousePressedWrapper(event):
            self.mousePressed(event)
            redrawAllWrapper()

        def keyPressedWrapper(event):
            self.keyPressed(event)
            redrawAllWrapper()

        def windowResized(event):
            canvas = event.widget
            canvas.width = event.width - 4
            canvas.height = event.height - 4
            


        root.bind("<Button-1>", mousePressedWrapper)
        root.bind("<Key>", keyPressedWrapper)
        root.bind("<Configure>", windowResized)

        # set up timerFired events
        self.timerFiredDelay = 250 # milliseconds
        def timerFiredWrapper():

            self.timerFired()
            redrawAllWrapper()
            # pause, then call timerFired again
            if running:
                self.canvas.after(self.timerFiredDelay, timerFiredWrapper)
            
        # init and get timerFired running
        self.init()
        timerFiredWrapper()
        # and launch the app
        root.mainloop()
        running = False
        print("Bye") # Animation Class from CMU 15-112 (edited)
        