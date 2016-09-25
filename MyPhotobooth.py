import RPi.GPIO as gpio
import picamera
import pygame
import time
import os
import PIL.Image
import PIL.ImageDraw
import cups
import datetime

from threading import Thread
from pygame.locals import *
from time import sleep
from PIL import Image

#initialise global variables
shutter = 17
reprint = 24
closeme = True #Loop Control Variable
#timepulse = 999 #Pulse Rate of LED
#LEDon = False #LED Flashing Control
gpio.setmode(gpio.BCM) #Set GPIO to BCM Layout
numeral = "" #numeral is the number display
message = "" #Message is a fullscreen message
smallMessage = "" #SmallMessage is a lower banner message
totalImageCount = 1 #Counter for Display and to monitor paper usage
photosPerCart = 16 #Selphy takes 16 sheets per tray

#initialise pygame
pygame.mixer.pre_init(44100, -16, 1, 1024*3) #PreInit Music, plays faster
pygame.init() #Initialise pygame
#screen = pygame.display.set_mode((1440,900),pygame.FULLSCREEN)
screen = pygame.display.set_mode((1920,1080),pygame.FULLSCREEN) #testing
background = pygame.Surface(screen.get_size()) #Create the background object
background = background.convert() #Convert it to a background

def updateDisplay():
    global numeral
    global message
    global smallMessage
    global totalImageCount
    global screen
    global background
    global pygame
    smallText = "Made by Mitesh"
    #paper low warning at 2 shets left
    if(totalImageCount >= (photosPerCart-2)):
        smallText = "Paper Running Low!..."
    #paper out warning.
    if(totalImageCount >= photosPerCart):
        smallText = "Paper Out!..."
        totalImageCount = 0

    background.fill(pygame.Color("black")) #Black background
    smallfont = pygame.font.Font(None, 50) #Small font for banner message
    smallText = smallfont.render(smallText,1, (255,0,0))
    background.blit(smallText,(10,1045)) #Write the small text
    smallText = smallfont.render(`totalImageCount`+"/"+`photosPerCart`,1, (255,0,0))
    background.blit(smallText,(1830,1045)) #Write the image counter
    if(message != ""): #If the big message exits write it
        font = pygame.font.Font(None, 180)
        text = font.render(message, 1, (255,0,0))
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        textpos.centery = background.get_rect().centery
        background.blit(text, textpos)
    elif(numeral != ""): # Else if the number exists display it
        font = pygame.font.Font(None, 800)
        text = font.render(numeral, 1, (255,0,0))
        textpos = text.get_rect()
        textpos.centerx = background.get_rect().centerx
        textpos.centery = background.get_rect().centery
        background.blit(text, textpos)

    screen.blit(background, (0,0))
    pygame.draw.rect(screen,pygame.Color("red"),(10,10,1890,1030),2) #Draw the red outer box
    pygame.display.flip()

def main(threadName, *args):
    print('test')
    gpio.setup(reprint, gpio.IN) #Button on Pin 24 Reprints last image
    gpio.setup(shutter, gpio.IN) #Button on Pin shutter is the shutter
    global closeme
    global timepulse
    global totalImageCount
    global numeral
    global smallMessage
    global message
    global shutter
    global reprint

    message = "Loading..."
    print(message)
    updateDisplay()
    time.sleep(5)

    camera = picamera.PiCamera()
    camera.preview_alpha = 120
    camera.vflip = False
    camera.hflip = True
    camera.rotation = 180
    camera.exposure_compensation = 6
    camera.contrast = 8
    camera.resolution = (1280,720)
    camera.start_preview()

    message = "USB Check..."
    print(message)
    updateDisplay()
    imagefolder = '/home/pi/Desktop/PhotoBooth'

    #****************Not storing files on USB, but on Main Drive**************
    #Following is a check to see there is a USB mounted if not it loops with a USB message
    # usbcheck = False
    # rootdir = '/home/pi/Downloads/PhotoBooth'
    #
    # while not usbcheck:
    #     dirs = os.listdir(rootdir)
    #     for file in dirs:
    #         folder = os.path.join(rootdir,file)
    #         if not file == 'SETTINGS' and os.path.isdir(folder):
    #             usbcheck = True
    #             imagedrive = os.path.join(rootdir,file)
    #             imagefolder = os.path.join(imagedrive,'PhotoBooth')
    #             #If a photobooth folder on the usb doesn't exist create it
    #             if not os.path.isdir(imagefolder):
    #                 os.makedirs(imagefolder)
    # message = "Initialise"
    # updateDisplay()

    imageCounter = 0
    picDir = os.path.join(imagefolder,datetime.datetime.now().strftime('%Y-%m-%d'))
    tempDir = picDir
    success = False
    folderno = 1
    while not success:
        try:
            os.mkdir(tempDir)
            success = True
        except OSError as e:
            folderno = folderno + 1
            tempDir = os.path.join(picDir,`folderno`)

    imagefolder = tempDir
    message = ""
    updateDisplay()

    while closeme:
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    closeme = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        closeme = False
        except KeyboardInterrupt:
            closeme = False

        #input_value is the shutter
        input_value = gpio.input(shutter)
        #for testing - push p on keybaord to take photograph
        #input_value = (pygame.key.get_pressed()[pygame.K_p] != 0)
        #input_value2 is photo reprint
        #input_value2 = gpio.input(reprint) -- no secondary button to reprint yet



        #Reprint Button has been pressed
        # if input_value2==False:
        #     #If the temp image exists send it to the printer
        #     if os.path.isfile('/home/pi/Desktop/tempprint.jpg'):
        #         #Open a connection to cups
        #         conn = cups.Connection()
        #         #get a list of printers
        #         printers = conn.getPrinters()
        #         #select printer 0
        #         printer_name = printers.keys()[0]
        #         message = "Re-Print..."
        #         updateDisplay()
        #         #print the buffer file
        #         printqueuelength = len(conn.getJobs())
        #         if  printqueuelength > 1:
        #             message = "PRINT ERROR"
        #             conn.enablePrinter(printer_name)
        #             updateDisplay()
        #         elif printqueuelength == 1:
        #             smallMessage = "Print Queue Full!"
        #             updateDisplay()
        #             conn.enablePrinter(printer_name)
        #             conn.printFile(printer_name,'/home/pi/Desktop/tempprint.jpg',"PhotoBooth",{})
        #             time.sleep(20)
        # message = ""
        # updateDisplay() # don't know why it was false originally
        #messages to print for
        messagDict = {1: 'Get Ready',2:'Another One',3:'Final One',4:''}
        if input_value==False:
            subCounter = 0
            #Increment the image number
            imageCounter = imageCounter + 1
            #stores images
            imageArray = []

            #loop that takes all the pictures and stores them in the imageArray
            while(subCounter < 4):
                #Load a beep music file
                pygame.mixer.music.load('/home/pi/Desktop/Beep.mp3')
                #play the beep
                pygame.mixer.music.play(0)
                #Display the countdown number
                # numeral = "5"
                # updateDisplay()
                # #Flash the light at half second intervals
                # #timepulse = 0.5
                # # 1 second between beeps
                # time.sleep(1)

                pygame.mixer.music.play(0)
                numeral = "4"
                updateDisplay()
                #timepulse = 0.4
                time.sleep(1)

                pygame.mixer.music.play(0)
                numeral = "3"
                updateDisplay()
                #timepulse = 0.3
                time.sleep(1)

                pygame.mixer.music.play(0)
                numeral = "2"
                updateDisplay()
                #timepulse = 0.2
                time.sleep(1)

                pygame.mixer.music.play(0)
                numeral = "1"
                updateDisplay()
                #timepulse = 0.1
                time.sleep(1)

                #Camera shutter sound
                pygame.mixer.music.load('/home/pi/Desktop/shutter.mp3')
                pygame.mixer.music.play(0)
                numeral = ""
                message = "Smile!"
                updateDisplay()
                #increment the sub
                subCounter = subCounter + 1
                #create the filename
                filename = 'image'
                filename += `imageCounter`
                filename += '_'
                filename += `subCounter`
                filename += '.jpg'
                #capture the image
                camera.capture(os.path.join(imagefolder,filename))
                message = messagDict[subCounter]
                updateDisplay()
                time.sleep(2)
                message=""
                updateDisplay
                #create an image object
                im = PIL.Image.open(os.path.join(imagefolder,filename)).transpose(Image.FLIP_LEFT_RIGHT)
                imageArray.append(im)

            #create thumbnails
            for i in range(0,len(imageArray)):
                imageArray[i].thumbnail((560,400))

            bgimage = PIL.Image.open("/home/pi/Desktop/template.jpg")
            #paste the thumbnails to the background images
            bgimage.paste(imageArray[0],(15,20))
            bgimage.paste(imageArray[1],(15,410))
            bgimage.paste(imageArray[2],(15,820))
            bgimage.paste(imageArray[3],(15,1230))
            #two columns of 4
            bgimage.paste(imageArray[0],(620,20))
            bgimage.paste(imageArray[1],(620,410))
            bgimage.paste(imageArray[2],(620,820))
            bgimage.paste(imageArray[3],(620,1230))

            #Create the final filename
            Final_Image_Name = os.path.join(imagefolder,"Final_"+`imageCounter`+".jpg")
            #Save it to the usb drive
            bgimage.save(os.path.join(imagefolder,"Final_"+`imageCounter`+".jpg"))
            #Save a temp file, its faster to print from the pi than usb
            #bgimage.show()
            bgimage.save('/home/pi/Desktop/tempprint.jpg')
            totalImageCount = totalImageCount + 1
            while input_value == False:
                input_value = gpio.input(shutter)

    camera.stop_preview()

Thread(target=main, args=('Main',1)).start()

time.sleep(5)
