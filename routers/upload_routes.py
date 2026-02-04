from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from auth import get_current_seller
from models.User import User
from utils.cloudinary_utils import upload_image

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/image")
async def upload_product_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_seller)
):
    """
    Upload an image to Cloudinary and return the URL.
    Only authenticated sellers can upload images.
    """
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # Read file content
        content = await file.read()
        
        # Upload to Cloudinary
        url = upload_image(content)
        
        return {"url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")
