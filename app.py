from flask import Flask, request, Response
import os 
from kik import KikApi, Configuration 
from kik.messages import messages_from_json, TextMessage
import unirest
import json
import pyrebase
import fuzzyset
import sys


#pip install python-google-places
#from googleplaces import GooglePlaces, types, lang
# YOUR_API_KEY = ''

# google_places = GooglePlaces(YOUR_API_KEY)
# query_result = google_places.nearby_search(
#     location='Waterloo, Ontario', keyword='Hospitals',
#     radius=500)

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
data = {"index": -1,"name":"","gender":"","sympindex":1,"symptom1":0,"symptom2":0,"symptoms":"","year":0}
db.child("Users").child("ericawng").set(data)

app = Flask(__name__)
kik = KikApi('htn2018', '2c9245d3-7101-4565-b6a1-f67212e08433')
kik.set_configuration(Configuration(webhook='http://a42cefa2.ngrok.io/incoming'))


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
        db.child("Users").child("ericawng").update({"name":body.lower()})
        name = db.child("Users").child('ericawng').get().val()['name']
        kik.send_messages([
            TextMessage(
                to=message.from_user,
                body='Hi '+name+', what is your gender?'
            )
        ])
        index+=1
    elif(index==1):
        db.child("Users").child("ericawng").update({"gender":body.lower()})
        kik.send_messages([
            TextMessage(
                to=user,                 
                body='Please describe two of your most significant symptoms as best as you can. Text "Done" if you have no more symptoms to input.'
            )
        ])
        index+=1
    elif(index==2):
        sympindex = db.child("Users").child('ericawng').get().val()['sympindex']
        if(body=='Done'):
            kik.send_messages([
                TextMessage(
                    to=user,                 
                    body='In which year were you born?'
                )
            ])
            index+=1
        elif (sympindex==2):
            kik.send_messages([
                TextMessage(
                    to=user,                 
                    body='In which year were you born?'
                )
            ])
            id = getid(body.lower())
            db.child("Users").child("ericawng").update({"symptom2":id})
            db.child("Users").child("ericawng").update({"sympindex":sympindex+1})
            index+=1
        else:
            id = getid(body.lower())
            if(sympindex==1):
                db.child("Users").child("ericawng").update({"symptom1":id})
                db.child("Users").child("ericawng").update({"sympindex":sympindex+1})
    else:
        sympindex = db.child("Users").child('ericawng').get().val()['sympindex']
        symp1 = db.child("Users").child('ericawng').get().val()['symptom1']
        sym = '%5B'+symp1
        if(sympindex>2):
            symp2 = db.child("Users").child('ericawng').get().val()['symptom2']
            sym += '%2C'+symp2
        sym+='%5D'
        db.child("Users").child("ericawng").update({"symptoms":sym})

        db.child("Users").child("ericawng").update({"year":body})
        reply(user)

    print (db.child("Users").child('ericawng').get().val()['sympindex'])

    db.child("Users").child("ericawng").update({"index":index})

    return Response(status=200)


def getid(msgs):
    with open('data.json') as f:
        data = json.load(f)
    a = fuzzyset.FuzzySet()
    a.add(str(msgs))
    value = sys.maxint
    id = 0
    name = ''
    for dt in data:
        val = a.get(str(dt['Name']))
        if(val>value):
            value = val
            id = dt['ID']
    return str(id)

def reply(user):
    kik.send_messages([
        TextMessage(
            to=user,                 
            body="Here are the three most likely problems you may have."
        )
    ])

    gender = db.child("Users").child('ericawng').get().val()['gender']
    symptoms = db.child("Users").child('ericawng').get().val()['symptoms']
    year = db.child("Users").child('ericawng').get().val()['year']
    link = "https://priaid-symptom-checker-v1.p.mashape.com/diagnosis?format=json&gender="+gender+"&language=en-gb&symptoms="+symptoms+"&year_of_birth="+year
    response = unirest.get(link,
      headers={
        "X-Mashape-Key": "H1C4a5gLxlmshtDy9kaV5b8TNYg1p1lcN7wjsnJUGx0cAL0dlJ",
        "Accept": "application/json"
      }
    )
    result = response.raw_body

    result = result.replace("'",'"')
    j = json.loads(result)
    index = 1
    for j1 in j:
        name = j1['Issue']['Name']
        profname = j1['Issue']['ProfName']
        accuracy = j1['Issue']['Accuracy']

        kik.send_messages([
            TextMessage(
                to=user,                 
                body="There is a "+str(accuracy)+"% chance that you have "+profname+", more commonly known as "+name
            )
        ])
        index+=1
        if(index==4):
            break
    # kik.send_messages([
    #         TextMessage(
    #             to=user,                 
    #             body="The closest clinical facilities are:"
    #         )
    #     ])
    # for place in query_result.places:
    #         kik.send_messages([
    #             TextMessage(
    #                 to=user,                 
    #                 body= place.name + "," place.geo_location + "," place.place_id
    #             )
    #         ])
      



if __name__ == "__main__":
    app.run(port=8080)

    