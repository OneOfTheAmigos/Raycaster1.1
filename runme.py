import pygame
import math
from ray_class import Ray
from boundary_class import Boundary
import numpy as np

FPS = 60
Window = None

#if True, it's in first person. if false, it's in top down view
IsFPDisplay = False

#angle that the player can see, also how many rays are cast out
FieldOfView = 100

#speeds
MovementSpeed = 2
TurningSpeed = 2

#if true, the 3d graphics adjust for fish eye effect
IsFishEyeCorrection = True

#FOV * (1 / PerformanceValue) = number of rays
#assuming FOV == 100:
# >1 = worse graphics and the smoothness isn't drastically effected
# 1 = rendered rectangle for every 5 pixels (really smooth performance)
# 0.8 = this is the best balance imo
# 0.4 = twice as good looking at 0.8 but it's twice as slow
# 0.2 = pixel perfect rendering (but it's really laggy and slow)
# <0.2 = won't render anything
#anything between 1 and 0.2 that wasn't mentioned above will create a weird transparent effect
#anything 0 or below will break it
#if using an FoV values that isn't 100, scale FOV : 100 and PV : Desired_Performance
PerformanceValue = 0.8

#colors
SquareColor = (255, 0, 0) #red
DarkSquareColor = (150, 0, 0) #dark red
FloorColor = (238, 177, 224) #pink 
SkyColor = (47, 194, 225) #light blue
RayColor = (0, 255, 0) #green
PlayerColor = (0, 0, 255) #dark blue

WindowHeight = 500
WindowLength = 500
SquareNumber = 8
UnitLength = WindowLength / SquareNumber


#here's the map. if you rotate this grid 90' clockwise and flip it, you'll get the rendered map
mapArray = [[1, 1, 1, 1, 1, 1, 1, 1], 
            [1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 0, 0, 1, 1, 0, 1],
            [1, 0, 1, 1, 1, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1]]

additionalrects = [pygame.Rect(1200, 250, 200, 10)]

#creates all of the rectangles
activeRectangles = []
def CreateRectangles():
    for i in range(len(mapArray)):
        for j in range(len(mapArray[i])):
            if mapArray[i][j] == 1:
                thisrectangle = pygame.Rect(i * (WindowLength / len(mapArray)), j * (WindowHeight / len(mapArray[i])), WindowLength / len(mapArray), WindowHeight / len(mapArray[i]))
                activeRectangles.append(thisrectangle)
    for k in additionalrects:
        activeRectangles.append(k)

def DrawRectangles():
    for rectangles in activeRectangles:
        pygame.draw.rect(Window, SquareColor, rectangles)

activeBoundaries = []
def CreateBoundaries():
    for rectangles in activeRectangles:
        topboundary = Boundary(rectangles.x, rectangles.y, rectangles.x + rectangles.width, rectangles.y)
        bottomboundary = Boundary(rectangles.x, rectangles.y + rectangles.height, rectangles.x + rectangles.width, rectangles.y + rectangles.height)
        leftboundary = Boundary(rectangles.x, rectangles.y, rectangles.x, rectangles.y + rectangles.height)
        rightboundary = Boundary(rectangles.x + rectangles.width, rectangles.y, rectangles.x + rectangles.width, rectangles.y + rectangles.height)
        activeBoundaries.extend([topboundary, bottomboundary, leftboundary, rightboundary])

         
def DrawPlayer(player):
    pygame.draw.circle(Window, PlayerColor, player.center, player.radius)

def DrawRays(rayarray):
    for ray in rayarray:
        pygame.draw.line(Window, RayColor, (ray.startingx, ray.startingy), (ray.endx, ray.endy), 1)

def DrawTopDownBackground():
    bg = pygame.Rect(0, 0, WindowLength, WindowHeight)
    pygame.draw.rect(Window, FloorColor, bg)

def TopDownGraphics(player, rayarray):
    DrawTopDownBackground()
    DrawRectangles()
    DrawRays(rayarray)
    DrawPlayer(player)

#handles the calculation and display of first person graphics
iiidrects = []
def FPGraphics(arraydistances):
    iiidrects.clear()
    rectwidth = WindowLength / len(arraydistances)
    multiplier = 10000
    for ii in range(len(arraydistances)):
        rectheight = multiplier * (1 / arraydistances[ii])
        if rectheight < 0:
            rectheight = rectheight * -1
        iiidrects.append(pygame.Rect(rectwidth * ii, (WindowHeight / 2) - (rectheight / 2), rectwidth, rectheight))
    
    for ii in range(len(iiidrects)):
        if ii >= len(iiidrects):
            if iiidrects[ii].height > iiidrects[ii - 1].height:
                pygame.draw.rect(Window, SquareColor, iiidrects[ii])
            else:
                pygame.draw.rect(Window, DarkSquareColor, iiidrects[ii])
        else:
            if iiidrects[ii].height < iiidrects[ii - 1].height:
                pygame.draw.rect(Window, SquareColor, iiidrects[ii])
            else:
                pygame.draw.rect(Window, DarkSquareColor, iiidrects[ii])

def DrawFloor():
    floor = pygame.Rect(0, WindowHeight / 2, WindowLength, WindowHeight / 2)
    pygame.draw.rect(Window, FloorColor, floor)
    

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 2
        self.center = (self.x, self.y)
        self.angle = 0
        self.visionwidth = FieldOfView
        self.anglevelocity = TurningSpeed
        self.velocity = MovementSpeed
        self.x_movement_amount = self.velocity * math.cos(math.radians(self.angle))
        self.y_movment_amount = self.velocity * math.sin(math.radians(self.angle))
        self.rayarray = []
        self.allraydistances = []
        self.correctarraydistances = []
        self.quadrent = 1

        self.PopulateRayArray()
        
    def AngleCorrection(self):
        if self.angle < 0:
            self.angle == 359
        elif self.angle > 360:
            self.angle == 1
            
    def Move(self, keys_pressed):
        anglemovment = 0
        if keys_pressed[pygame.K_RIGHT]:
            self.angle += self.anglevelocity
            anglemovment = self.anglevelocity
        if keys_pressed[pygame.K_LEFT]:
            self.angle -= self.anglevelocity
            anglemovment = -self.anglevelocity
        if keys_pressed[pygame.K_DOWN]:
            self.x_movement_amount = self.velocity * math.cos(math.radians(self.angle))
            self.x -= self.x_movement_amount
            self.y_movment_amount = self.velocity * math.sin(math.radians(self.angle))
            self.y -= self.y_movment_amount
        if keys_pressed[pygame.K_UP]:
             self.x_movement_amount = self.velocity * math.cos(math.radians(self.angle))
             self.x += self.x_movement_amount
             self.y_movment_amount = self.velocity * math.sin(math.radians(self.angle))
             self.y += self.y_movment_amount

        if self.angle > 360:
            self.angle = 0 + self.anglevelocity

        if self.angle < 0:
            self.angle = 360 - self.anglevelocity

        self.center = (self.x, self.y)
        #self.UpdateQuadrent()
        self.CastingRays()
        self.UpdateRayArray(anglemovment)
        self.RayCorrection()

    def PopulateRayArray(self):
        for ii in np.arange((-self.visionwidth // 2) + self.angle, (self.visionwidth // 2) + self.angle, PerformanceValue):
            self.rayarray.append(Ray(self.x, self.y, ii))

    def UpdateRayArray(self, anglemovment):
        for rays in self.rayarray:
            rays.Update(self.x, self.y, rays.angle + anglemovment)

    def CastingRays(self):
        self.allraydistances.clear()
        for rays in self.rayarray:
            self.allraydistances.append(FindRayDistance(rays))

    def RayCorrection(self):
        self.correctarraydistances.clear()
        for ii in range(len(self.allraydistances)):
            self.correctarraydistances.append(self.allraydistances[ii] * math.cos(math.radians(self.rayarray[ii].angle - self.angle)))

    '''
    def UpdateQuadrent(self):
        global checks
        checks += 1
        if self.angle >= 0 and self.angle < 90:
            self.quadrent = 4
        elif self.angle >= 90 and self.angle < 180:
            self.quadrent = 3
        elif self.angle >= 180 and self.angle < 270:
            self.quadrent = 2
        else:
            self.quadrent = 1
    '''
        

#returns a filtered list of boundaries that should be checked. 
#all boundaries that do not need to be checked will be filtered out
#nevermind, this actually does more harm than good
def BoundaryFilter(x, y, quadrent):
    filteredboundaries = []
    for wall in activeBoundaries:
        global checks
        checks += 1
        if quadrent == 1:
            if wall.startingx > x or wall.startingy < y:
                filteredboundaries.append(wall)
        elif quadrent == 2:
            if wall.startingx < x or wall.startingy < y:
                filteredboundaries.append(wall)
        elif quadrent == 3:
            if wall.startingx < x or wall.startingy > y:
                filteredboundaries.append(wall)
        else:
            if wall.startingx > x or wall.startingy > y:
                filteredboundaries.append(wall)
    return filteredboundaries
            


def FindRayDistance(ray):
    
    ray.distances.clear()
    #loops through every wall and determines whether an indefinite ray would hit it. if yes, it adds the distance to that wall to an array of distances
    searchBoundaries = []
    for wall in activeBoundaries:
        x1 = wall.startingx
        y1 = wall.startingy
        x2 = wall.endingx
        y2 = wall.endingy
        x3 = ray.startingx
        y3 = ray.startingy
        x4 = ray.endx
        y4 = ray.endy

        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denominator == 0:
            continue

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator

        if (t > 0 and t < 1 and u > 0):
            ptx = x1 + t * (x2 - x1)
            pty = y1 + t * (y2 - y1)
            dis = math.sqrt(((ptx - ray.startingx) ** 2) + ((pty - ray.startingy) ** 2))
            ray.distances.append(dis)
        else:
            continue
    
    #finds the shortest distance out of the array and returns it
    ray.length = 10000
    for diss in ray.distances:
        if diss < ray.length:
            ray.length = diss
    return ray.length



def gameloop():
    MainPlayer = Player(200, 200)
    CreateRectangles()
    CreateBoundaries()
    global IsFPDisplay
    global SquareColor
    global DarkSquareColor
    global FloorColor
    global SkyColor

    clock = pygame.time.Clock() 
    run = True
    while run == True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            #changes the perspective when you click the space key
            #changes the color when you click the number keys
            if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if IsFPDisplay == True:
                            IsFPDisplay = False
                        else:
                            IsFPDisplay = True
                    elif event.key == pygame.K_1:
                        SquareColor = (255, 0, 0) 
                        DarkSquareColor = (150, 0, 0) 
                        FloorColor = (238, 177, 224) 
                        SkyColor = (47, 194, 225) 
                    elif event.key == pygame.K_2:
                        SquareColor = (255, 255, 255)
                        DarkSquareColor = (200, 200, 200)
                        FloorColor = (0, 0, 0)
                        SkyColor = (0, 0, 0)
                    elif event.key == pygame.K_3:
                        SquareColor = (188, 90, 13)
                        DarkSquareColor = (141, 50, 0)
                        FloorColor = (210, 190, 0)
                        SkyColor = (85, 109, 255)
                    elif event.key == pygame.K_4:
                        SquareColor = (0, 100, 0)
                        DarkSquareColor = (0, 60, 0)
                        FloorColor = (0, 0, 75)
                        SkyColor = (0, 0, 150)
                    elif event.key == pygame.K_5:
                        SquareColor = (134, 182, 225)
                        DarkSquareColor = (100, 139, 185)
                        FloorColor = (180, 0, 169)
                        SkyColor = (50, 0, 50)
                    elif event.key == pygame.K_6:
                        SquareColor = (171, 167, 102)
                        DarkSquareColor = (102, 90, 23)
                        FloorColor = (200, 198, 155)
                        SkyColor = (172, 155, 100)
                    elif event.key == pygame.K_x:
                        SquareColor = (0, 0, 60)
                        DarkSquareColor = (0, 0, 30)
                        FloorColor = (0, 30, 0)
                        SkyColor = (0, 0, 0)
                    

        #happens every loop
        keys_pressed = pygame.key.get_pressed()
        MainPlayer.Move(keys_pressed)

        if MainPlayer.x > 1000:
            SquareColor = (71, 71, 71)
            DarkSquareColor = (71, 71, 71)
            FloorColor = (230, 230, 230)
            SkyColor = (255, 255, 255)
        
        Window.fill(SkyColor)
        if IsFPDisplay == True:
            if IsFishEyeCorrection:
                DrawFloor()
                FPGraphics(MainPlayer.correctarraydistances)
            else:
                DrawFloor()
                FPGraphics(MainPlayer.allraydistances)
        else:
            TopDownGraphics(MainPlayer, MainPlayer.rayarray)
               
        pygame.display.update()
        



def Customize():
    print("Would you like to customize the raycaster?")
    print("[c] Customize")
    print("[q] Quickstart")
    aa = input()
    if aa == "q":
        return
    while aa != "c":
        aa = input("Please input a valid choice:")
        if aa == "q":
            return
    Customizer()

def Customizer():
    global FieldOfView
    global MovementSpeed
    global TurningSpeed
    global PerformanceValue
    global IsFishEyeCorrection
    global SquareColor
    global DarkSquareColor
    global FloorColor
    global SkyColor

    print("Set a number for field of view:   ")
    bbcheck = False 
    while bbcheck == False:
        try:
            bb = input()
            FOV = int(bb)
            if FOV < 0 or FOV > 360:
                raise Exception()
            bbcheck = True
        except:
            print("Field of view needs to be a whole number between 0 and 360:")
    FieldOfView = FOV

    print("Set a number for your movement speed:   [Reccomended: 2]")
    cccheck = False 
    while cccheck == False:
        try:
            cc = input()
            MS = int(cc)
            if MS < 0:
                raise Exception()
            cccheck = True
        except:
            print("Movement speed needs to be a positive whole number:")
    MovementSpeed = MS

    print("Set a number for your turning speed:   [Reccomended: 2]")
    ddcheck = False 
    while ddcheck == False:
        try:
            dd = input()
            TS = int(dd)
            if TS < 0:
                raise Exception()
            ddcheck = True
        except:
            print("Turning speed needs to be a positive whole number:")
    TurningSpeed = TS

    print("Select the performance:")
    print("[1] Better performance and worse graphics")
    print("[2] Balanced performance. This one is reccomended.")
    print("[3] Worse performance and better graphics")
    print("[4] Bad performance and pixel perfect graphics")
    eecheck = False
    while eecheck == False:
        try:
            ee = input()
            PN = int(ee)
            if PN > 4 or PN < 1:
                raise Exception()
            eecheck = True
        except:
            print("Please select a valid performance option:")
    if PN == 1:
        PerformanceValue = (1 * FieldOfView) / 100
    elif PN == 2:
        PerformanceValue = (0.8 * FieldOfView) / 100
    elif PN == 3:
        PerformanceValue = (0.4 * FieldOfView) / 100
    elif PN == 4:
        PerformanceValue = (0.2 * FieldOfView) / 100

    print("Select a color scheme:")
    print("[1] Carnival (default)")
    print("[2] Monochrome")
    print("[3] Desert")
    print("[4] Underwater")
    print("[5] Dreamscape")
    print("[6] Backrooms")
    ggcheck = False
    while ggcheck == False:
        try:
            gg = input()
            CL = int(gg)
            if PN > 6 or PN < 1:
                raise Exception()
            ggcheck = True
        except:
            print("Please select a valid color option:")
        if CL == 1:
            pass
        elif CL == 2:
            SquareColor = (255, 255, 255)
            DarkSquareColor = (200, 200, 200)
            FloorColor = (0, 0, 0)
            SkyColor = (0, 0, 0)
        elif CL == 3:
            SquareColor = (188, 90, 13)
            DarkSquareColor = (141, 50, 0)
            FloorColor = (210, 190, 0)
            SkyColor = (85, 109, 255)
        elif CL == 4:
            SquareColor = (0, 100, 0)
            DarkSquareColor = (0, 60, 0)
            FloorColor = (0, 0, 75)
            SkyColor = (0, 0, 150)
        elif CL == 5:
            SquareColor = (134, 182, 225)
            DarkSquareColor = (100, 139, 185)
            FloorColor = (180, 0, 169)
            SkyColor = (50, 0, 50)
        elif CL == 6:
            SquareColor = (171, 167, 102)
            DarkSquareColor = (102, 90, 23)
            FloorColor = (200, 198, 155)
            SkyColor = (172, 155, 100)
        

    print("Do you want fisheye effect?")
    print("[y] Yes")
    print("[n] No   [reccomended]")
    ff = input()
    if ff == "y":
        IsFishEyeCorrection = False
        return
    while ff != "n":
        ff = input("Please input a valid choice:")
        if ff == "y":
            IsFishEyeCorrection = False
            return
    IsFishEyeCorrection = True
    return


def main():
    Customize()
    global Window
    Window = pygame.display.set_mode((WindowLength, WindowHeight))
    gameloop()


if __name__ == "__main__":
    #write main() here
    main()
    