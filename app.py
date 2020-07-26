import asyncio

from flask import Flask, request
from flask_restful import Resource, Api

import controller

app = Flask(__name__)
api = Api(app)

class Brightness(Resource):
  def get(self):
    asyncio.run(controller.bulb.update())
    return controller.bulb.brightness
  def post(self):
    data = request.json
    target = data['target']
    duration = data['duration']

    asyncio.run(controller.transition_brightness(target, duration))

class ColorTemperature(Resource):
  def get(self):
    asyncio.run(controller.bulb.update())
    return controller.bulb.color_temp

  def post(self):
    data = request.json
    target = data['target']
    duration = data['duration']

    asyncio.run(controller.transition_color_temp(target, duration))


api.add_resource(Brightness, '/brightness')
api.add_resource(ColorTemperature, '/temp')

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0')