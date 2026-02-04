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

@router.post("/images")
async def upload_multiple_images(
    files: list[UploadFile] = File(...),
    current_user: User = Depends(get_current_seller)
):
    """
    Upload multiple images to Cloudinary and return a list of URLs.
    Only authenticated sellers can upload images.
    """
    urls = []
    errors = []
    
    for file in files:
        if not file.content_type.startswith("image/"):
            errors.append(f"File {file.filename} is not an image")
            continue
            
        try:
            content = await file.read()
            url = upload_image(content)
            urls.append(url)
        except Exception as e:
            errors.append(f"Failed to upload {file.filename}: {str(e)}")
            
    if not urls and errors:
        raise HTTPException(status_code=400, detail=f"All uploads failed: {', '.join(errors)}")
        
    return {"urls": urls, "errors": errors if errors else None}
