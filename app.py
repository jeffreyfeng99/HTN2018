from flask import Flask, request, Response
import os 
from kik import KikApi, Configuration 
from kik.messages import messages_from_json, TextMessage
import unirest
import json
import pyrebase

config = {
    'apiKey': "AIzaSyBXgZbPWz-YEl4BKZFN3ZiWdNM-syN1qjI",
    'authDomain': "htn2018-85959.firebaseapp.com",
    'databaseURL': "https://htn2018-85959.firebaseio.com",
    'projectId': "htn2018-8595",
    'storageBucket': "htn2018-85959.appspot.com",
    'messagingSenderId': "469098036102"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
data = {"index": -1,"name":"","gender":"","symptoms":[],"year":0}
db.child("Users").child("ericawng").set(data)

app = Flask(__name__)
kik = KikApi('htn2018', '2c9245d3-7101-4565-b6a1-f67212e08433')
kik.set_configuration(Configuration(webhook='http://3facc81a.ngrok.io/incoming'))


@app.route('/incoming', methods=['POST'])
def incoming():
    if not kik.verify_signature(request.headers.get('X-Kik-Signature'),    request.get_data()):
    	return Response(status=403) 
    messages = messages_from_json(request.json['messages'])

    for message in messages:
        if isinstance(message, TextMessage):
            user = str(message.from_user)
            body = str(message.body)

    index = db.child("Users").child('ericawng').get().val()['index']

    if(index==-1):
        kik.send_messages([
            TextMessage(
                to=user,
                body='Hello, what\'s your name?'
            )
        ])
        index+=1
    elif(index==0):
        db.child("Users").child("ericawng").update({"name":body})
        kik.send_messages([
            TextMessage(
                to=message.from_user,
                body='Hi '+name+', what is your gender?'
            )
        ])
        index+=1
    elif(index==1):
        db.child("Users").child("ericawng").update({"gender":body})
        kik.send_messages([
            TextMessage(
                to=user,                 
                body='Please describe three of your most significant symptoms as best as you can. Text "Done" if you have no more symptom to input.'
            )
        ])
        index+=1
    elif(index==2):
        if(messages=='Done'):
            kik.send_messages([
                TextMessage(
                    to=user,                 
                    body='In which year were you born?'
                )
            ])
            index+=1
        elif (len(symptoms)==2):
            kik.send_messages([
                TextMessage(
                    to=user,                 
                    body='In which year were you born?'
                )
            ])
            id = getid(messages.body)
            symptoms.append(id)
            index+=1
        else:
            id = getid(messages.body)
            symptoms.append(id)
    else:
        sym = '%5B'+symptoms[0]
        for x in range (1,len(symptoms)-1):
            sym+='%2C'+symptoms[x]
        sym+='%5D'
        db.child("Users").child("ericawng").update({"symo":body})
        year_of_birth = messages
        reply(messages)

    db.child("Users").child("ericawng").update({"index":index})

    return Response(status=200)


def getid(msgs):
    return msgs

def reply(messages):
    for message in messages:
        if isinstance(message, TextMessage):
            gender = messages.body
            kik.send_messages([
                TextMessage(
                    to=message.from_user,                 
                    body="Here are the three most likely problems you may have."
                )
            ])
    response = unirest.get("https://priaid-symptom-checker-v1.p.mashape.com/diagnosis?format=json&gender="+gender+"&language=en-gb&symptoms="+sym+"&year_of_birth="+year_of_birth,
      headers={
        "X-Mashape-Key": "H1C4a5gLxlmshtDy9kaV5b8TNYg1p1lcN7wjsnJUGx0cAL0dlJ",
        "Accept": "application/json"
      }
    )
    result = response.raw_body

    result = result.replace("'",'"')
    j = json.loads(result)
    i
    for j1 in j:
        name = j1['Issue']['Name']
        profname = j1['Issue']['ProfName']
        accuracy = j1['Issue']['Accuracy']

        for message in messages:
            if isinstance(message, TextMessage):
                gender = messages.body
                kik.send_messages([
                    TextMessage(
                        to=message.from_user,                 
                        body="There is a "+accuracy+"% chance that you have "+profname+", more commonly known as "+name
                    )
                ])


if __name__ == "__main__":
    app.run(port=8080)