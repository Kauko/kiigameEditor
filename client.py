import requests
import os


class Client():

    VERBOSE = True

    SERVER_ADDRESS = 'http://localhost:5000'
    ROUTES = {
        "upload": '/upload'
    }

    def hello_world():
        return requests.get(Client.SERVER_ADDRESS).content

    def test_upload(self, folder_path):
        files = Client.get_test_file(self)
        return requests.post(Client.SERVER_ADDRESS, files=files)

    def get_test_file(self):
        return {'file1': open('../test.txt', 'rb')}

    def download_test_file(self, filename):
        return requests.get(Client.SERVER_ADDRESS+'/uploads/'+filename)

    def upload_game_files(self, game_root):
        if self.VERBOSE:
            print("Client :: upload_game_files")
        # Get a list of the files we want to upload
        file_list = self.get_list_of_game_files(game_root)
        # Build a dictionary using the file_list
        files = self.build_file_dictionary(file_list)
        # Post the list to the server
        if self.VERBOSE:
            print("Client :: Attempting to POST")
        response = requests.post(
            self.SERVER_ADDRESS + self.ROUTES['upload'], files=files)
        # Return the response so we can access,
        # for example the status code elsewhere
        if self.VERBOSE:
            print(
                "Client :: Response status code: " + str(response.status_code))
        return response

    def get_list_of_game_files(self, game_root):
        if self.VERBOSE:
            print("Client :: get_list_of_game_files in " + game_root)
        struct = os.walk(game_root)
        ret = {}

        for root, dirs, files in struct:

            ret[root] = []
            for f in files:
                ret[root].append(root+'/'+f)

        if self.VERBOSE:
            print("Client :: Found the following files")
            for root in ret:
                print("* " + root)
                for f in ret[root]:
                    print(' - ' + f)
        return ret

    def build_file_dictionary(self, file_list):
        if self.VERBOSE:
            print("Client :: build_file_dictionary")

        ret = {}
        for root in file_list:
            for f in file_list[root]:
                path = f
                if path[:1] == '.':
                    path = path[1:]
                if path[:1] == '/':
                    path = path[1:]
                ret[path] = open(f, 'rb')

        if self.VERBOSE:
            print("Client :: Built the following dictionary:")
            for name in ret:
                print("* " + name)

        return ret
