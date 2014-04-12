from flask import Flask, request, url_for
from pymongo import MongoClient
from bson.json_util import dumps, ObjectId
import string
import random
import sys
from pydub import AudioSegment
from tempfile import TemporaryFile, NamedTemporaryFile
import wave
import audioop
import glob
import os

# configuration
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
client = MongoClient(MONGODB_HOST, MONGODB_PORT)
db = client.sounds


# create the little application object
app = Flask(__name__)
app.config.from_object(__name__)

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/song/<songname>', methods=['GET', 'POST'])
def song_handle(songname):
    if request.method == 'GET':

        search = {'song': songname} #prepare search
        res = db.songs.find(search)

        files = []
        for entry in res:
            files.append(AudioSegment.from_file("songs/"+entry['audiofile']))
        if len(files) == 0:
            return '''
            <!doctype html>
            <title>Upload new File</title>
            <h1>Upload new File</h1>
            <form action="" method=post enctype=multipart/form-data>
              <p>audio<input type=file name=audio>
                 <input type=submit value=Upload>
            </form>
            '''
        bigass = files[0]
        for sound in files[1:]:
            bigass = bigass.overlay(sound)
        
        bigass.export("songs/combined/combined"+songname+".wav", format='wav')
        return 'songs/combined/combined'+songname+".wav"

    elif request.method == 'POST':    
        audio = request.files['audio']
        realAudio = AudioSegment.from_file(audio)
        filename = id_generator(10)+".mp3"
        realAudio.export('songs/'+filename, format='mp3')


        dic = {'song': songname, 'audiofile': filename}
        db.songs.insert(dic)
        return "success"
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p>audio<input type=file name=audio>
         <input type=submit value=Upload>
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)