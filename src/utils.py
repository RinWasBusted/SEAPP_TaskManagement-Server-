from cloudinary.utils import cloudinary_url

def getImageUrl(public_id):
    result_tuple = cloudinary_url(public_id, secure=True)
    return result_tuple[0]