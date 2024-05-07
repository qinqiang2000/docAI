import json
import os
from core.extractor import Extractor  # Make sure to import the Extractor class


class ExtractorManager:
    EXTRACTORS_FILE = 'data/extractors.json'

    def __init__(self):
        self.extractors = self.load_extractors()

    def load_extractors(self):
        if os.path.exists(self.EXTRACTORS_FILE):
            with open(self.EXTRACTORS_FILE, 'r') as f:
                data = json.load(f)
            # Ensure 'name' is not duplicated in the details
            return {name: Extractor(name, **{k: v for k, v in details.items() if k != 'name'}) for name, details in
                    data.items()}

    def save_extractor(self, extractor):
        self.extractors[extractor.name] = extractor
        self.save_to_disk()

    def delete_extractor(self, name):
        if name in self.extractors:
            del self.extractors[name]
            self.save_to_disk()
            return True
        return False

    def save_to_disk(self):
        with open(self.EXTRACTORS_FILE, 'w') as f:
            json.dump({name: extractor.__dict__ for name, extractor in self.extractors.items()}, f, indent=4,
                      ensure_ascii=False)

    def get_extractors_list(self):
        return list(self.extractors.keys())

    def get_extractor(self, name):
        return self.extractors.get(name)
