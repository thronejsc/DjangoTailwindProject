from django.core.files.storage import Storage

class DatabaseOnlyStorage(Storage):
    def _open(self, name, mode='rb'):
        # Override the _open method to return the file directly from the database
        # Assuming you have a FileField or ImageField in your Document model
        return name

    def _save(self, name, content):
        # Do nothing since we don't want to save the file to disk
        return name

    def url(self, name):
        # Return an empty string since the file is not stored on disk
        return ''

    def exists(self, name):
        # Return False since the file doesn't exist in storage
        return False
