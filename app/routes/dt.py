from fastapi import APIRouter , File, UploadFile
from PIL import Image
import io

router = APIRouter()

@router.get("/working" )
async def get_working():
    response = {"status":"working"}
    
    return response
