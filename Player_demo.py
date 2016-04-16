#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal
from pygame import mixer
from pygame import mixer_music as player


continue_reading = True
path = '/home/pi/Documents/Music/Florence_And_The_Machine-Between_Two_Lungs/'
song = '101-florence_and_the_machine-dog_days_are_over-caheso.mp3'
##path = '/home/pi/Documents/Music/'
##song = 'example.mp3'

song_started = False
song_paused = False

# Function for playing some music
def play_music():
    mixer.init()
    player.load(path+song)
    player.play()
##    while player.get_busy() == True:
##        continue

def pause_music():
    player.pause()

def stop_music():
    player.stop()

def unpause_music():
    player.unpause()



# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print "***********************************************"
print "Welcome to the RFID Home Music Player RF'n'Roll"
print "***********************************************"
print "Please put your RFIDisk to play some music!"
print "Press Ctrl-C to stop."


# This loop keeps checking for chips. If one is near it will get the UID and play the song
while continue_reading:
    
    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print "Card detected"
##    else:
##	print "Card not detected!"
    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:   # First check if there is something detected. 
                                       # If it is, then check if we're already playin something
        if not song_started:           # If not, start it
        # Print UID
            print "Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])
            # Check UID and play corresponding song
            if uid[0] == 93:
                play_music()
                song_started = True
                print 'sviramo pjesmu '+song

        else:                          # If we're playing, check if we paused it then unpause it
            if song_paused:
                print 'vracamo se na pjesmu'
                unpause_music()
                song_paused = False
            else:                      # otherwise, everything's fine
                continue

            
    elif status != MIFAREReader.MI_OK and song_started:     # If we' don't get any card read, pause the song
        song_paused = True
        print 'Pauziramo pjesmu!'
        pause_music()    
            
    


            

## LET'S TRY WITHOUT AUTHENTICATION    
##        # This is the default key for authentication
##        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
##        
##        # Select the scanned tag
##        MIFAREReader.MFRC522_SelectTag(uid)
##
##        # Authenticate
##        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)
##
##        # Check if authenticated
##        if status == MIFAREReader.MI_OK:
##            MIFAREReader.MFRC522_Read(8)
##            MIFAREReader.MFRC522_StopCrypto1()
##        else:
##            print "Authentication error"
##
