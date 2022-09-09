#!/usr/bin/env python

import random

class MusicBot:
    def __init__(self, voice_channel):
        self.is_playing = False
        self.music_queue = []
        self.voice_channel = voice_channel
        self.artist_playing = random.choice(["harry styles", "taylor swift", "drake", "eminem", "beyonce"])
        self.current_song = None
        self.voice_client = None

    def add_to_queue(self, *song):
        self.music_queue.extend(song)


    def get_next_song(self):
        return self.music_queue.pop(0)

    def get_current_song(self):
        return self.current_song

    def get_voice_channel(self):
        return self.voice_channel


    def get_artist_playing(self):
        return self.artist_playing


    def set_artist_playing(self, artist):
        self.artist_playing = artist


    def alternate_state(self):
        self.is_playing = not self.is_playing


    def music_queue_is_empty(self):
        return not self.music_queue


    def is_playing(self):
        return self.is_playing


    def set_current_song(self, song):
        self.current_song = song

    def get_music_queue(self):
        return self.music_queue


    def agregar_cancion_colada(self, song):
        self.music_queue.insert(0, song)

    def get_voice_client(self):
        return self.voice_client