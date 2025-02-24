import os
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
import shutil
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import LLM functions
from llm import create_client
from review import review_lc


app = FastAPI()

# Load API Key
api_key = os.getenv("OPENAI_API_KEY")
client, model = create_client("gpt-4o-2024-05-13")

UPLOAD_FOLDER = "uploads"
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)  # Ensure base upload folder exists

@app.post("/upload/")
async def upload_file(file: UploadFile):
    file_path = Path(UPLOAD_FOLDER) / file.filename  # Store file in 'uploads/' directly
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"filename": file.filename, "stored_at": str(file_path)}

@app.get("/files/")
async def list_files():
    """ Lists all files in the uploads folder """
    files = [str(file) for file in Path(UPLOAD_FOLDER).iterdir() if file.is_file()]
    
    if not files:
        return {"message": "No files found in the uploads folder"}
    
    return {"files": files}

@app.delete("/delete/{filename}")
async def delete_file(filename: str):
    """ Deletes a specified file from the uploads folder """
    file_path = Path(UPLOAD_FOLDER) / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        os.remove(file_path)
        return {"message": f"{filename} has been deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")
    

class FilePaths(BaseModel):
    lc_filepath: str
    contract_filepath: str

@app.post("/review/")
async def review(paths: FilePaths):
    """ Process two file paths and return the result """
    
    # Ensure both files exist before proceeding
    if not Path(paths.lc_filepath).exists():
        raise HTTPException(status_code=404, detail=f"File not found: {paths.lc_filepath}")

    if not Path(paths.contract_filepath).exists():
        raise HTTPException(status_code=404, detail=f"File not found: {paths.contract_filepath}")

    try:
        # Call the review_lc function with the provided file paths
        return StreamingResponse(review_lc(model, client, paths.lc_filepath, paths.contract_filepath))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")

    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
