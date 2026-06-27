import os
import sys
import tempfile
import uuid
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from img2img import get_args, main

app = FastAPI(title="ASCII艺术生成器API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Serve static files
app.mount("/api/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")


def validate_image(file: UploadFile):
    content_type = file.content_type
    if content_type not in ["image/jpeg", "image/png", "image/jpg", "image/webp"]:
        raise HTTPException(status_code=400, detail="只支持 JPEG/PNG/WebP 图片")

    max_size = 10 * 1024 * 1024
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > max_size:
        raise HTTPException(status_code=400, detail="文件大小不能超过 10MB")

    try:
        file.file.seek(0)
        img = Image.open(file.file)
        img.verify()
        file.file.seek(0)
    except Exception:
        raise HTTPException(status_code=400, detail="无效的图片文件")


def process_image(
    input_path: str,
    output_path: str,
    custom_text: str = "西施",
    language: str = "chinese",
    color: bool = True,
    portrait: bool = False,
):
    argv = [
        "--input", input_path,
        "--output", output_path,
        "--custom_text", custom_text,
        "--language", language,
    ]
    if color:
        argv.append("--color")
    if portrait:
        argv.append("--portrait")

    args = get_args(argv)
    main(args)


@app.post("/api/generate/")
async def generate_ascii_art(
    file: UploadFile = File(...),
    custom_text: str = Form("西施"),
    language: str = Form("chinese"),
    color: bool = Form(True),
    portrait: bool = Form(False),
):
    input_path = None
    try:
        validate_image(file)

        suffix = Path(file.filename or "input.jpg").suffix or ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=OUTPUT_DIR) as temp_file:
            content = await file.read()
            temp_file.write(content)
            input_path = temp_file.name

        output_filename = f"ascii_{uuid.uuid4().hex}{suffix}"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        process_image(
            input_path=input_path,
            output_path=output_path,
            custom_text=custom_text,
            language=language,
            color=color,
            portrait=portrait,
        )

        image_url = f"/api/outputs/{output_filename}"
        return JSONResponse(content={"image_url": image_url, "filename": output_filename})

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if input_path and os.path.exists(input_path):
            os.unlink(input_path)


if __name__ == "__main__":
    uvicorn.run("ascii_api:app", host="0.0.0.0", port=8000, reload=True)
