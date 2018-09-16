from flask import Flask, request, Response
import os 
from kik import KikApi, Configuration 
from kik.messages import messages_from_json, TextMessage
import unirest
import json
import pyrebase
import fuzzyset
import sys
from googleplaces import GooglePlaces, types, lang
from googlemaps import convert
import googlemaps

google_maps_api = 'AIzaSyBusndDrJxrEKVnWNpOBo3_LXK_rlrkDvU'
google_places = GooglePlaces(google_maps_api)
query_result = google_places.nearby_search(
    location='Waterloo, Ontario', keyword='Hospitals',
    radius=500)
gmaps = googlemaps.Client(key=google_maps_api)


for place in query_result.places:
    place.get_details()
    address = gmaps.reverse_geocode((place.geo_location['lat'],place.geo_location['lng']))[0]['formatted_address']
    print(address)
    '''
    kik.send_messages([
        TextMessage(
            to=user,                 
            body= str(place.name)+"\nAddress: "+str(address)+"\nPhone numeber: "+str(place.local_phone_number)
        )
    ])'''