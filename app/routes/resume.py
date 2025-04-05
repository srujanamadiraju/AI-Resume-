from fastapi import APIRouter , File, UploadFile , HTTPException , Form
from models.resume_converter.web_app import convert_resume
from PIL import Image
import io
import shutil
import os

router = APIRouter()

@router.post("/resume-convert")
async def convert_resume_route(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...)
): 
    file_path = ""
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save the uploaded file
        file_path = os.path.join(upload_dir, resume_file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(resume_file.file, buffer)
        
        resume_latex , metrics = convert_resume(file_path,job_description)
        result = {
            "resume_latex":resume_latex,
            "metrics":metrics
        }
        
        resume_file.file.close()
        
        # Delete the resume file
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {str(e)}")
        
        return {
            "status": "success",
            "message": "Resume processed successfully",
            "result": result
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the resume: {str(e)}"
        )
    
    # finally:
    #     # Close the file
    #     pass
    
