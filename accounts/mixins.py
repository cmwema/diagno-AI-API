import cloudinary.uploader


class ImageUploadMixin:
    def upload_image(self, image_data):
        if image_data:
            return cloudinary.uploader.upload(image_data)['url']
        return None
