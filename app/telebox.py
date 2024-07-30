import requests
import hashlib
import os
import sys

from .config import Config


class Telebox:
    """
    The `Telebox` class represents a client to interact with the Telebox API.

    :param token: The access token required for authentication.
    :param folder_id: The ID of the folder to interact with.

    The class provides methods to connect, search, and perform various operations on the specified folder.
    """

    def __init__(self, token, folder_id):
        self.token = token
        self.folder_id = folder_id
        self.connect = Connect(Config.TELEBOX_BASE_URI, self.token)
        self.search = Search(self.connect)
        self.folder = Folder(self.connect)
        self.upload = Upload(self.connect)

class HttpClientService:
    """HTTP Client Service for making requests."""

    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, endpoint, params=None):
        response = requests.get(f"{self.base_url}{endpoint}", params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint, params=None):
        response = requests.post(f"{self.base_url}/{endpoint}", params=params)
        response.raise_for_status()
        return response.json()


class Connect:
    """Connect to the Telebox API."""

    def __init__(self, base_url, token):
        self.client = HttpClientService(base_url)
        self.token = token

    def get_data(self, endpoint, params):
        params["token"] = self.token
        return self.client.get(endpoint, params)

    def post_data(self, endpoint, params):
        params["token"] = self.token
        return self.client.post(endpoint, params)


class Search:
    """Search for files and folders in Telebox."""

    def __init__(self, connect):
        self.connect = connect
        self.url = 'api/open/file_search'

    def search(self, filename, folder_id):
        return self.connect.get_data(self.url, {'pid': folder_id, 'name': filename, 'pageNo': 1, 'pageSize': 50})

    def folder_exists(self, filename, folder_id):
        lot = self.search(filename, folder_id)
        if isinstance(lot['data']['list'], list) and len(lot['data']['list']) != 0:
            return lot['data']['list'][0]['id'] if lot['data']['list'][0]['type'] == 'dir' and lot['data']['list'][0]['pid'] == int(folder_id) else False
        return False


class Upload:
    """Handle file uploads to Telebox."""

    def __init__(self, connect):
        self.connect = connect

    def prepare(self, file_md5_of_pre_10m, file_size):
        return self.connect.get_data('api/open/get_upload_url', {'fileMd5ofPre10m': file_md5_of_pre_10m, 'fileSize': file_size})

    @staticmethod
    def upload(url, file):
        size = os.path.getsize(file)
        with open(file, "rb") as file:
            # Send the PUT request
            response = requests.put(url, data=file)
        return response

    def finish_upload(self, file_md5_of_pre_10m, file_size, pid, name):
        return self.connect.get_data('api/open/folder_upload_file', {'fileMd5ofPre10m': file_md5_of_pre_10m, 'fileSize': file_size, 'pid': pid, 'diyName': name})

    def upload_file(self, file, folder_id):
        file_size = os.path.getsize(file)
        file_md5_of_pre_10m = self.get_md5_of_first_10mb(file)
        lot = self.prepare(file_md5_of_pre_10m, file_size)
        if lot['status'] == 600:
            return 1

        if lot['status'] != 1:
            sys.exit("Prepare: Execution stopped. Cannot upload files")

        url = lot['data']['signUrl']
        self.upload(url, file)
        lotf = self.finish_upload(file_md5_of_pre_10m, file_size, folder_id, os.path.basename(file))
        if lotf['status'] != 1:
            sys.exit("Finish Upload: Execution stopped. Cannot upload files")

        return lotf['data']['itemId']

    @staticmethod
    def get_md5_of_first_10mb(file_path):
        md5_hash = hashlib.md5()

        with open(file_path, 'rb') as file:
            chunk = file.read(10 * 1024 * 1024)  # read first 10MB
            if chunk:
                md5_hash.update(chunk)

        return md5_hash.hexdigest()


class Folder:
    """Handle folder operations in Telebox."""

    def __init__(self, connect):
        self.connect = connect

    def create(self, filename, destination_folder_id):
        lot = self.connect.get_data('api/open/folder_create', {
            'pid': int(destination_folder_id),
            'name': filename,
            'isShare': 0,
            'canInvite': 1,
            'canShare': 1,
            'withBodyImg': 0,
            'desc': 'TheWNetwork Telebox Mass Creator'
        })
        if lot['status'] != 1:
            sys.exit("Execution stopped. Cannot create folders")

        return lot['data']['dirId']

    def get_details(self, destination_folder_id):
        return self.connect.get_data('api/open/folder_details', {'dirId': destination_folder_id})