"""
Docker repository on-disk model
Based on code from https://github.com/docker/docker-registry by Docker
"""

import os
from os.path import join, basename
import json
import tempfile
from credentials import username, password

class Repository(object):
    def __init__(self, root_path, repositories='repository', images='images'):
        self.root_path = root_path
        self.repositories = repositories
        self.images = images

    def validate(self):
        """Returns the set of referenced images not found in the repository. 
           An empty set means the registry is in a valid state"""
        
        referenced_images = self.referenced_images()
        all_images = set(self.all_images())
        
        diff = referenced_images - all_images
        return diff

    def report(self):
        def get_size(img_id):
            try:
                return self.get_size(img_id)
            except:
                return -1

        report = {i: get_size(i) for i in self.unused_images()}
        return report


    def untag(self):
        pass

    def purge(self, delete=False):
        pass

    def revert(self, source, images=None):
        pass

    def unused_images(self):
        return set(self.all_images()) - self.referenced_images()
        
    def tagged_images(self):
        for tf in self.tagfiles():
            try:
                with open(tf, mode='rb') as f:
                    yield f.read().strip()
            except (IOError, OSError) as e:
                print(e)
                continue

    def all_images(self):
        path = join(self.root_path, self.images)
        return os.listdir(path)

    def referenced_images(self):
        """Returns a set of referenced image ids"""
        return {a for i in self.tagged_images()
                  for a in self.ancestry(i)}

    def ancestry(self, image_id):
        p = join(self.root_path, self.images, image_id, "ancestry")
        with open(p, mode='rb') as f:
            data = f.read()
            return iter(json.loads(data))
        
    def tagfiles(self):
        """Returns a list of all tagfiles in the repository"""
        # Functional directory walking!
        base = join(self.root_path, self.repositories)
        namespaces = [join(base, d) for d in os.listdir(base)]
        repos = {ns: os.listdir(ns) for ns in namespaces}
        tag_dirs = [os.path.join(r, t) for r in repos
                                       for t in repos[r]]
        tags = [os.path.join(d, t) for d in tag_dirs
                                   for t in os.listdir(d)]

        return filter(lambda t: basename(t).startswith('tag_'), tags)

    def get_size(self, image_id):
        path = join(self.root_path, self.images, image_id)
        return os.path.getsize(path)

    def remove(self, image_id, delete=False, dryrun=False):
        path = self.join(self.root_path, self.images, image_id)
        tmp = tempfile
        

    
