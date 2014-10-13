import requests
import os


# This class is for communicating between the server and the editor
# The server is simply used for saving the games so they can be played
class Client():

    VERBOSE = True

    SERVER_ADDRESS = 'http://localhost:5000'
    ROUTES = {
        "upload": '/upload'
    }

    # Main function for uploading game files to the server
    # Will construct a dict of the files, read them, and
    # send to the server using a HTTP POST
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

    # Find the game files from the given folder, and save
    # their names into a { <folder>: [<full_path>, <full_path>, ..]}
    def get_list_of_game_files(self, game_root):
        if self.VERBOSE:
            print("Client :: get_list_of_game_files in " + game_root)
        struct = os.walk(game_root)
        ret = {}

        # Root is the "current" folder, dirs is folders in that folder,
        # files is files in that folder
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

    # Gets the list of files from get_list_of_game_files,
    # opens the files, and returns a dict:
    # { <full_path>: <opened_file> }
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
