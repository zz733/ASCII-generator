# 修改 ascii_api.py 中的导入部分
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import uvicorn
import cv2
import numpy as np
from typing import Optional
import imghdr
from pathlib import Path
import sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

# 将当前目录添加到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入 img2img 中的函数
from img2img import get_args, main

app = FastAPI(title="ASCII艺术生成器API")

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保输出目录存在
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def validate_image(file: UploadFile):
    """验证上传的图片文件"""
    # 检查文件类型
    content_type = file.content_type
    if content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="只支持JPEG和PNG图片")
    
    # 检查文件大小 (最大10MB)
    max_size = 10 * 1024 * 1024
    file.file.seek(0, 2)  # 移动到文件末尾
    file_size = file.file.tell()
    file.file.seek(0)  # 移回文件开头
    
    if file_size > max_size:
        raise HTTPException(status_code=400, detail="文件大小不能超过10MB")
    
    # 验证图片内容
    file_format = imghdr.what(file.file)
    if not file_format:
        raise HTTPException(status_code=400, detail="无效的图片文件")
    
    file.file.seek(0)  # 再次移回文件开头
    return True

def process_image(
    input_path: str,
    output_path: str,
    custom_text: str = "江雪利",
    language: str = "chinese",
    color: bool = True,
    portrait: bool = False
):
    """处理图片并生成ASCII艺术"""
    # 准备命令行参数
    args = [
        "--input", input_path,
        "--output", output_path,
        "--custom_text", custom_text,
        "--language", language
    ]
    
    if color:
        args.append("--color")
    if portrait:
        args.append("--portrait")
    
    # 解析参数
    args = get_args(args)
    
    # 调用主函数
    main(args)

@app.post("/api/generate/")
async def generate_ascii_art(
    file: UploadFile = File(...),
    custom_text: str = Form("江雪利"),
    language: str = Form("chinese"),
    color: bool = Form(True),
    portrait: bool = Form(False)
):
    """生成ASCII艺术图片"""
    try:
        # 验证文件
        validate_image(file)
        
        # 创建临时文件保存上传的图片
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            input_path = temp_file.name
        
        # 生成输出路径
        output_filename = f"ascii_{file.filename}"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        # 处理图片
        process_image(
            input_path=input_path,
            output_path=output_path,
            custom_text=custom_text,
            language=language,
            color=color,
            portrait=portrait
        )
        
        # 清理临时文件
        os.unlink(input_path)
        
        # 返回处理后的图片
        return FileResponse(
            output_path,
            media_type="image/jpeg",
            filename=output_filename
        )
        
    except Exception as e:
        # 清理临时文件
        if 'input_path' in locals() and os.path.exists(input_path):
            os.unlink(input_path)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("ascii_api:app", host="0.0.0.0", port=8000, reload=True)