import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("cloud_name"),
    api_key=os.getenv("api_key"),
    api_secret=os.getenv("api_secret")
)

def upload_image(file_object):
    """
    Uploads a file-like object to Cloudinary and returns the secure URL.
    """
    try:
        response = cloudinary.uploader.upload(file_object)
        return response.get("secure_url")
    except Exception as e:
        print(f"Cloudinary upload error: {e}")
        raise e
