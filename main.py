from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ObjectProperty
from kivy.clock import Clock
from jnius import autoclass
from audiostream import get_input
import wave
#
import os
from android.permissions import request_permissions,Permission,check_permission
from kivy_garden.graph import Graph, LinePlot
import numpy as np 
from array import array
from datetime import datetime


import numpy as np
#import matplotlib.pyplot as plt
import pickle
from scipy import fft, signal
from scipy.io.wavfile import read
from create_constellations import create_constellation
from create_hashes import create_hashes








 
 
#if not os.path.isdir("/sdcard/kivyrecords/"):
#    os.mkdir("/sdcard/kivyrecords/")

PATH = "rec_test1.wav"
 
recordtime = 5
samples_per_second = 60
 
 
class RootScreen(BoxLayout): #
    pass
 


       

class Recorder(object):
    def __init__(self):
        # get the needed Java classes
        self.MediaRecorder = autoclass('android.media.MediaRecorder')
        self.AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
        self.AudioFormat = autoclass('android.media.AudioFormat')
        self.AudioRecord = autoclass('android.media.AudioRecord')
    # define our system
        self.SampleRate = 44100
        self.ChannelConfig = self.AudioFormat.CHANNEL_IN_MONO
        self.AudioEncoding = self.AudioFormat.ENCODING_PCM_16BIT
        self.BufferSize = self.AudioRecord.getMinBufferSize(self.SampleRate, self.ChannelConfig, self.AudioEncoding)
        #self.outstream = self.FileOutputStream(PATH)
        self.sData = []
        #self.mic = get_input(callback=self.mic_callback, source='mic', buffersize=self.BufferSize)
        self.mic = get_input(callback=self.mic_callback, source='default', buffersize=self.BufferSize)
        print("This is the audio source")
        print(self.AudioSource)
        print("This is the mic channels")
        print(self.mic.channels)
 
    def mic_callback(self, buf):
        self.sData.append(buf)
        print ('got : ' + str(len(buf)))
        print(self.sData)
        
        # convert our byte buffer into signed short array
        values = array("h", buf)

        # get right values only
        r_values = values[1::2]

        # reduce by 20%
        r_values = map(lambda x: x * 0.8, r_values)
        print("r_values")
        print(r_values)
        '''
        # you can assign only array for slice, not list
        # so we need to convert back list to array
        values[1::2] = array("h", r_values)
        print("values")
        print(values)
        '''
        # convert back the array to a byte buffer for speaker
        #sample.write(values.tostring())
 
 
    def start(self):
        self.mic.start()
        Clock.schedule_interval(self.readbuffer, 1/samples_per_second)
 
    def readbuffer(self, dt):
        self.mic.poll()
 
    def dummy(self, dt):
        print ("dummy")
 
    def stop(self):
        Clock.schedule_once(self.dummy, 0.5)
        Clock.unschedule(self.readbuffer)
        self.mic.stop()
        wf = wave.open(PATH, 'wb')
        wf.setnchannels(self.mic.channels)
        wf.setsampwidth(2)
        wf.setframerate(self.mic.rate)
        wf.writeframes(b''.join(self.sData))
        print("we at stop")
        wf.close()
        
        print("files in pwd")
        print(os.listdir())
        print("finished creating wav file")     
        self.play()
        
        
    def play(self):
        MediaPlayer = autoclass('android.media.MediaPlayer')
        AudioManager = autoclass('android.media.AudioManager')

        self.sound = MediaPlayer()
        #self.sound.setDataSource(yourDataSource) #you can provide any data source, if its on the devie then the file path, or its url if you are playing online
        #self.sound.setDataSource('testaudio.mp4') 
        #self.audio_path = self.storage_path + "/wav/output2.wav"
        #self.audio_path = self.storage_path + "/wav/output1.wav" ##cant find folder
     
        
        
        
        #self.audio_path = dirCheck1 + "/wav/output1.wav"
        #self.audio_path = "/storage/emulated/0/org.example.c4k_tflite_audio1/wav/output1.wav"##Not found
        #self.audio_path = "/data/data/org.example.c4k_tflite_audio1/files/app/wav/output2.wav"
        #self.audio_path = "/data/data/org.example.c4k_tflite_audio1/files/app/output2.wav"        
        #self.audio_path  = "/data/data/org.example.c4k_tflite_audio1/files/app/testaudio.mp4"
        self.audio_path  = "rec_test1.wav"
     
        self.sound.setDataSource(self.audio_path) 
        self.sound.prepare()
        self.sound.setLooping(False) #you can set it to true if you want to loop
        self.sound.start()
        print("start play")

        e = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
       
        print("time of start playing audio")
        print(e)
        # You can also use the following according to your needs
        #self.sound.pause()
        #self.sound.stop()
        #self.sound.release()
        #self.sound.getCurrentPosition()
        #self.sound.getDuration()   
        
        
        #Fs, audio_input = read("recording2.wav")
        Fs, audio_input = read("rec_test1.wav")


        constellation = create_constellation(audio_input, Fs)
        hashes = create_hashes(constellation, None)

        # %%
        database = pickle.load(open('database.pickle', 'rb'))
        song_index_lookup = pickle.load(open("song_index.pickle", "rb"))
        
               
        self.score_songs(hashes)   
        for song_index, score in scores:
            print(f"{song_index_lookup[song_index]=}: Score of {score[1]} at {score[0]}")
        
        
         
        
    def score_songs(hashes):


        matches_per_song = {}
        for hash, (sample_time, _) in hashes.items():
            if hash in database:
                matching_occurences = database[hash]
                for source_time, song_index in matching_occurences:
                    if song_index not in matches_per_song:
                        matches_per_song[song_index] = []
                    matches_per_song[song_index].append((hash, sample_time, source_time))
            

        # %%
        scores = {}
        for song_index, matches in matches_per_song.items():
            song_scores_by_offset = {}
            for hash, sample_time, source_time in matches:
                delta = source_time - sample_time
                if delta not in song_scores_by_offset:
                    song_scores_by_offset[delta] = 0
                song_scores_by_offset[delta] += 1

            max = (0, 0)
            for offset, score in song_scores_by_offset.items():
                if score > max[1]:
                    max = (offset, score)
        
            scores[song_index] = max

        # Sort the scores for the user
        scores = list(sorted(scores.items(), key=lambda x: x[1][1], reverse=True)) 
    
        return scores        



#scores = score_songs(hashes)

# # %%
'''
song_scores_by_offset = {}
for hash, sample_time, source_time in matches_per_song[0]:
     delta = source_time - sample_time
     if delta not in song_scores_by_offset:
         song_scores_by_offset[delta] = 0
         song_scores_by_offset[delta] += 1
     plt.scatter(song_scores_by_offset.keys(), song_scores_by_offset.values())
'''







           
 
REC = Recorder()
'''
class RecordApp(App):
	
    def __init__(self, **kwargs):
        super(RecordApp, self).__init__(**kwargs)
        
        	
 
    def build(self):
        #request_permissions([Permission.INTERNET, Permission.RECORD_AUDIO,Permission.READ_EXTERNAL_STORAGE,Permission.WRITE_EXTERNAL_STORAGE])
        self.title = 'Recording Application'
        return RecordForm()
        #return Builder.load_file("look.kv")
  
'''     
        
class RecordForm(BoxLayout): #
    #b_record = ObjectProperty()
    #p_bar = ObjectProperty()
 
    def start_record(self):
        #self.b_record.disabled = True
        #self.p_bar.max = recordtime
        #REC.prepare()
        REC.start()
        Clock.schedule_once(self.stop_record, recordtime)
        #Clock.schedule_interval(self.update_display, 1/30.)
 
    def stop_record(self, dt):
        #Clock.unschedule(self.update_display)
        #self.p_bar.value = 0
        REC.stop()
        #self.b_record.disabled = False
 
    def update_display(self,dt):
        #self.p_bar.value = self.p_bar.value + dt
        print("here")        
        
'''
class JKMain(AnchorLayout):
    def __init__(self, **kwargs):
        super(JKMain, self).__init__(**kwargs)

    def change_text(self, layers):
        self.the_time.text = "Total Layers : " + str(layers)
        print("Total Layers = " + str(layers))

    def popup_func(self):

        content = ConfirmPopup()
        content.bind(on_answer=self._on_answer)
        self.popup = Popup(title="Select .zip file",
                           content=content,
                           size_hint=(None, None),
                           size=(500, 500),
                           auto_dismiss=False)
        self.popup.open()

    def _on_answer(self, instance, answer, obj):
        self.popup.dismiss()
'''

class Main(App):

    def build(self):
        #return JKMain()
        request_permissions([Permission.INTERNET, Permission.RECORD_AUDIO,Permission.READ_EXTERNAL_STORAGE,Permission.WRITE_EXTERNAL_STORAGE])
        return RecordForm()
        


if __name__ == "__main__":
    Main().run()


