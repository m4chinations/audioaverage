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
import datetime

# configuration
MONGODB_HOST = 'localhost'
MONGODB_PORT = 6420
client = MongoClient(MONGODB_HOST, MONGODB_PORT)
db = client.sounds


# create the little application object
app = Flask(__name__)
app.config.from_object(__name__)

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

@app.route('/popular')
def popular():
    popularGs = {'genres':db.genres.find().limit(5).sort("pop")}
    return dumps(popularGs)

@app.route('/comment/<songname>', methods=['POST'])
def comment(songname):
    if request.method == 'POST':

        commentText = request.form['comment']
        commentTime = request.form['time']
        comment = {'time': commentTime, 'comment': commentText, 
                'song': songname, 'realtime': datetime.datetime.now()}

        db.comments.insert(comment)

        return "Posted comment: " + str(comment)
    return '''
    <!doctype html>
    <title>Post new comment</title>
    <h1>Post new comment</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p>comment<input type=text name=comment>
         commentMusicTime<input type=text name=time>
         <input type=submit value=Upload>
    </form>
    '''


@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/song/<songname>', methods=['GET', 'POST'])
def song_handle(songname):
    if request.method == 'GET':
        search = {'song': songname} #prepare search
        res = db.songs.find(search) #execute search
        files = []
        for entry in res:
            files.append(AudioSegment.from_file("songs/"+entry['audiofile']))
        print(len(files))
        print(files)
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
        
        bigass.export("songs/combined/combined"+songname+".mp3", format='mp3')
        comments = db.comments.find({'song':songname}).limit(20).sort('realTime')
        resDict = {"url":'songs/combined/combined'+songname+".mp3",
                    "comments" : comments}
        return dumps(resDict)

    elif request.method == 'POST':
        audio = request.files['audio']
        realAudio = AudioSegment.from_file(audio)
        filename = id_generator(10)+".mp3"
        realAudio.export('songs/'+filename, format='mp3')

        dic = {'song': songname, 'audiofile': filename}

        db.songs.insert(dic)
        genreSearch = {'genre':request.form['genre']}
        genreInc = { '$inc' : { 'pop' : 1 } }
        db.genres.update(genreSearch, genreInc, { 'upsert' : True })
        return "success"
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p>audio<input type=file name=audio>
         genre<input type=text name=genre>
         <input type=submit value=Upload>
    </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)