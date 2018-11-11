from os import listdir, remove
from os.path import isfile, join


class DirDict:
    def __init__(self, path=None):
        self.path = path or './'

    def __contains__(self, searched_file):
        return searched_file in self.keys()

    def __delitem__(self, file_name):
        full_path = join(self.path, file_name)
        if not isfile(full_path):
            raise KeyError(f"No such file :'{file_name}'")
        remove(full_path)

    def __getitem__(self, file_name):
        full_path = join(self.path, file_name)
        if not isfile(full_path):
            raise KeyError(f"No such file :'{file_name}'")
        return self._get_file_content(full_path)

    def __iter__(self):
        for file_name in listdir(self.path):
            full_path = join(self.path, file_name)
            if isfile(full_path):
                yield file_name, self[full_path]

    def __len__(self):
        return len(self.keys())

    def __repr__(self):
        return str(dict(self))

    def __setitem__(self, file_name, new_content):
        full_path = join(self.path, file_name)
        with open(full_path, 'w') as f:
            f.write(str(new_content))

    __hash__ = None

    @staticmethod
    def _get_file_content(path):
        with open(path, 'r') as file:
            content = ''
            while True:
                update = file.read(2048)
                if not update:
                    break
                content += update
        return content

    def values(self):
        return [content for _, content in self]

    def keys(self):
        return [file for file, _ in self]

    def clear(self):
        for file_name in self.keys():
            del self[file_name]