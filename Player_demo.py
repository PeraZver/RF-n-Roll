#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import MFRC522
import signal
from pygame import mixer
from pygame import mixer_music as player
import os


class Playlist:
    """ A Class that creates a playlist of songs based on the scanned code. It also updates the current song
    to be played. """
    # Set the playlist directories, common for all classes, song counter and song.
    path = '/home/pi/Documents/Music/'
    song_counter = 0
    song = ''
    folder = ''
    filename = ''
    
    def __init__ (self, name):
        self.name = name
            

    def createPlaylist(self, code):
        """ Creates playlist based on the code from the RFID tag. Returns a list of all songs
        in a given directory. Everytime the playlist is created the self.song becomes first song
        on that playlist. """
        self.folder = self.songCode(code)
        self.playlist = os.listdir(self.path + self.folder)   # Read all files from the Music directory and keep only mp3s
        for item in self.playlist:
            if item[-1] != '3':
                self.playlist.remove(item)
                
        self.playlist.sort()
        self.song_counter = 0
        self.song = self.playlist[0]
        self.filename = self.path + self.folder + self.song


    def songCode(self, code):
        """ A function that assigns a music directories to the code from RFID tag.
        The directories are coded elegantly in form of a dictionary. Better solution
        will be with if/elif/else control. """
        return {
               '93' : 'Florence_And_The_Machine-Between_Two_Lungs/',
               '182': 'Florence_And_The_Machine-Between_Two_Lungs/',
               '99' : 'Florence_And_The_Machine-Between_Two_Lungs/',
               }[code]
    
    def updateSong(self):
        """ Updates the current playing song within the playlist. """
        self.song_counter += 1
        if self.song_counter > len(self.playlist):  # If it comes till the end of the playlist, restart it.
            self.song_counter = 0
        self.song = self.playlist[self.song_counter]
        self.filename = self.path + self.folder + self.song


MyPlaylist = Playlist("Test Playlist")

song_started = False    # Flags to see the state of the player
song_paused = False
last_card = '0'         # Flag that remembers last card
continue_reading = True
number_of_no_detects = 0


# Function for playing some music
def playMusic():
    """ A function that plays music. It loads the song from the playlist and plays it. """
    player.load(MyPlaylist.filename)
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
    global last_card, song_started, Playlist
    last_card = code
    song_started = False   # if new card is scanned, stop current song
    stopMusic()
    MyPlaylist.createPlaylist(code)

def nextSong():
    """ A function that updates songs to be played in the class playlist. """
    MyPlaylist.updateSong()
    


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
            updatePlaylist(str(uid[0]))          # if not, then make a playlist
            print uid[0], last_card
            
        if not song_started:     # Now check if something's playing already      
                playMusic()      # If not, start it
                song_started = True
                song_paused = False
                print "We're playing  " + MyPlaylist.song

                                 
        elif song_paused:           # If we're playing, check if we paused it then unpause it
            print 'vracamo se na pjesmu'
            unpauseMusic()
            song_paused = False

        else:                      # otherwise, everything's fine
            continue

            
    elif status != MIFAREReader.MI_OK and song_started and not song_paused:     # If we don't get any card read, and song is started but unpaused --> pause the song
        number_of_no_detects += 1
        if number_of_no_detects > 2:
            number_of_no_detects = 0
            song_paused = True
            print 'Pauziramo pjesmu!'
            pauseMusic()
        else:
            continue
            
    if song_started and not player.get_busy():      # If the song has come to the end, read new song and rise the flag to play the new one.
        print "Song finished !"
        nextSong()
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
