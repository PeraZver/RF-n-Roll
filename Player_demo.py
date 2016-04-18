#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal
from pygame import mixer
from pygame import mixer_music as player


continue_reading = True

# Set the playlist directories
path = '/home/pi/Documents/Music/Florence_And_The_Machine-Between_Two_Lungs/'
#song = '101-florence_and_the_machine-dog_days_are_over-caheso.mp3'
song_list = open("song_list.dat").read().split("\n")   # Import all song titles from the datafile, and make a python list out of them
song_list.pop()
song = song_list[0]

song_started = False    # Flags to see the state of the player
song_paused = False
last_card = '0'         # Flag that remembers last card

# Function for playing some music
def playMusic():
    """ A function that plays music. It loads the song from the playlist and plays it. """
    player.load(path + song)
    player.play()

def pauseMusic():
    player.pause()

def stopMusic():
    player.stop()

def unpauseMusic():
    player.unpause()

def isAlreadyScanned(code):
    """ A function that checks if the currently scanned card is already been scanned. """
    if code == last_card:
        print "This card is already scanned!"
        return True
    else:
        print "This is some new card!"
        return False

def updatePlaylist(code):
    """ A function to update current playlist. """
    global song
    global last_card, song_started
    last_card = code
    song_started = False   # if new card is scanned, stop current song
    stopMusic()
    song = songCode(code)


def songCode(code):
    """ A function that assigns a song playlist to the code from RFID tag.
        The songs are assigned elegantly in form of a dictionary. Better solution
        will be with if/elif/else control. """
    return {
           '93' : song_list[0],
           '182': song_list[1],
           '99' : song_list[2],
           }[code]
        

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
# Initialize the mixer from Pygame
mixer.init()

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
    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:   # First check if there is something detected, and then decide wether to play new song or unpause the old one
       # Print UID
        print "Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])
        if not isAlreadyScanned(str(uid[0])):    # Check if this card was scanned earlier 
            updatePlaylist(str(uid[0]))          # if not, then pick a song
            print uid[0], last_card
            
        if not song_started:     # Now check if something's playing already      
                playMusic()      # If not, start it
                song_started = True
                song_paused = False
                print 'Sviramo pjesmu ' + song

                                 
        elif song_paused:           # If we're playing, check if we paused it then unpause it
            print 'vracamo se na pjesmu'
            unpauseMusic()
            song_paused = False

        else:                      # otherwise, everything's fine
            continue

            
    elif status != MIFAREReader.MI_OK and song_started and not song_paused:     # If we don't get any card read, and song is started but unpaused --> pause the song
        song_paused = True
        print 'Pauziramo pjesmu!'
        pauseMusic()
    else:
        continue
            
    if song_started and not player.get_busy():
        print "Song not playing ..."
        song_started = False
            

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
