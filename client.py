import requests


class Client():

    SERVER_ADDRESS = 'http://localhost:5000'

    def hello_world():
        return requests.get(Client.SERVER_ADDRESS).content
