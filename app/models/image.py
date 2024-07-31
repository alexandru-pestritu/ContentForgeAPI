class Image:
    def __init__(self, data):
        self.id = data['id']
        self.url = data['source_url']
        self.mime_type = data['mime_type']
        self.title = data['title']['rendered']
        self.alt_text = data['alt_text']
        self.width = data['media_details']['width']
        self.height = data['media_details']['height']
        self.sizes = data['media_details']['sizes']
        self.author = data['author']
        self.modified = data['modified']
        self.uploaded_to = data.get('post', 0) 

    def get_image_details(self):
        return {
            'id': self.id,
            'url': self.url,
            'mime_type': self.mime_type,
            'title': self.title,
            'alt_text': self.alt_text,
            'width': self.width,
            'height': self.height,
            'sizes': self.sizes,
            'author': self.author,
            'modified': self.modified,
            'uploaded_to': self.uploaded_to
        }

    def get_size_url(self, size_key):
        """ Return the URL of the image for a specific size """
        size_info = self.sizes.get(size_key, {})
        return size_info.get('source_url', '')

    def get_all_sizes(self):
        """ Return all available sizes and their details """
        return self.sizes
