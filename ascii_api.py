import os
import io
import cv2
import numpy as np
import traceback
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import time
import uuid
from typing import Union, BinaryIO
from PIL import Image, ImageDraw, ImageFont, ImageOps
from typing import Optional, Tuple, List, Dict, Any, Union, BinaryIO
import tempfile
import sys
import time
from pydantic import BaseModel
from alphabets import *

class AsciiArtRequest(BaseModel):
    text: str = "刘德华"
    num_cols: int = 120
    background: str = "black"
    color: bool = True
    portrait: bool = False

app = FastAPI(title="ASCII Art Generator API")

def get_font(font_size: int = 12) -> ImageFont.FreeTypeFont:
    """获取中文字体"""
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",  # macOS 苹方
        "/System/Library/Fonts/STHeiti Light.ttc",  # macOS 黑体
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # 文泉驿微米黑
        "simsun.ttc"  # Windows 宋体
    ]
    
    for font_path in font_paths:
        try:
            return ImageFont.truetype(font_path, size=font_size)
        except:
            continue
    
    # 如果找不到中文字体，使用默认字体
    return ImageFont.load_default()

def process_image(
    image_path: Union[str, BinaryIO],
    text: str = "刘德华",
    num_cols: int = 300,
    background: str = "black",
    color: bool = True,
    portrait: bool = False,
    language: str = "chinese",
    mode: str = "standard"
) -> Image.Image:
    """
    处理图片并生成ASCII艺术图
    
    Args:
        image_path: 输入图片路径或文件对象
        text: 用于生成ASCII艺术的文本
        num_cols: 输出图像的列数
        background: 背景颜色 ('black' 或 'white')
        color: 是否生成彩色图像
        portrait: 是否使用竖排模式
        
    Returns:
        PIL.Image: 生成的ASCII艺术图像
    """
    # 设置背景色代码
    bg_code = 0 if background == "black" else 255
    
    # 处理自定义文本
    if text:
        # 使用自定义文本作为字符集
        char_list = text * 100  # 重复多次以确保有足够的字符
        
        # 设置中文字体
        font_size = 12
        font = get_font(font_size)
        sample_character = char_list[0] if char_list else "A"
        scale = 1.5  # 行高比例
        num_chars = len(set(char_list))  # 去重后的字符数量
    else:
        # 使用预定义的字符集
        from utils import get_data
        char_list, font, sample_character, scale = get_data(language, mode)
        num_chars = len(set(char_list))  # 使用唯一字符数量
    
    # 读取图片
    if isinstance(image_path, (str, os.PathLike)):
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"无法读取图片: {image_path}")
    else:
        # 如果是文件对象，从内存中读取
        file_bytes = np.asarray(bytearray(image_path.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    # 转换为RGB颜色空间
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width = image.shape[:2]
    
    # 如果不是彩色模式，转换为灰度图
    if not color:
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 如果是横屏图片但启用了竖屏模式，则旋转图片
    if portrait and width > height:
        image_rgb = cv2.rotate(image_rgb, cv2.ROTATE_90_CLOCKWISE)
        if not color:
            image_gray = cv2.rotate(image_gray, cv2.ROTATE_90_CLOCKWISE)
        height, width = image_rgb.shape[:2]
    
    # 计算单元格大小和行列数
    cell_width = width / num_cols
    cell_height = scale * cell_width
    num_rows = int(height / cell_height)
    
    # 如果列数或行数过多，使用默认设置
    if num_cols > width or num_rows > height:
        print("Too many columns or rows. Use default setting")
        cell_width = 6
        cell_height = 12
        num_cols = int(width / cell_width)
        num_rows = int(height / cell_height)
    
    # 创建一个临时图片来获取字符大小
    temp_img = Image.new('L', (100, 100), 255)
    draw = ImageDraw.Draw(temp_img)
    bbox = draw.textbbox((0, 0), sample_character, font=font)
    char_width, char_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    # 创建输出图片
    out_width = char_width * num_cols
    out_height = int(scale * char_height * num_rows)
    
    if color:
        out_image = Image.new("RGB", (out_width, out_height), (255, 255, 255))
    else:
        out_image = Image.new("L", (out_width, out_height), bg_code)
    
    draw = ImageDraw.Draw(out_image)
    
    # 处理每一行
    for i in range(num_rows):
        y_start = int(i * cell_height)
        y_end = min(int((i + 1) * cell_height), height)
        
        for j in range(num_cols):
            x_start = int(j * cell_width)
            x_end = min(int((j + 1) * cell_width), width)
            
            # 获取当前单元格区域
            if color:
                # 彩色模式：获取平均颜色
                region = image_rgb[y_start:y_end, x_start:x_end]
                if region.size > 0:
                    avg_color = tuple(np.mean(region, axis=(0, 1)).astype(int))
                    # 计算灰度值用于选择字符
                    gray = np.mean(region)
                else:
                    avg_color = (bg_code, bg_code, bg_code)
                    gray = bg_code
            else:
                # 灰度模式
                region = image_gray[y_start:y_end, x_start:x_end]
                gray = np.mean(region) if region.size > 0 else bg_code
            
            # 选择字符
            char_idx = min(int(gray / 255 * num_chars), num_chars - 1)
            char = char_list[char_idx] if char_list else " "
            
            # 计算绘制位置
            if portrait:
                # 竖排文字（从上到下，从右到左）
                x = out_width - (j + 1) * char_width
                y = i * char_height * scale  # 应用行高比例
            else:
                # 横排文字（从左到右，从上到下）
                x = j * char_width
                y = i * char_height * scale  # 应用行高比例
            
            # 绘制字符
            if color and region.size > 0:
                draw.text((x, y), char, fill=tuple(avg_color), font=font)
            else:
                fill_color = 255 - bg_code if region.size > 0 else bg_code
                draw.text((x, y), char, fill=fill_color, font=font)
    
    # 裁剪图片
    if background == "white" and not color:
        # 对于白底黑字的灰度图，需要反相后裁剪
        cropped_image = ImageOps.invert(out_image).getbbox()
    else:
        cropped_image = out_image.getbbox()
    
    if cropped_image:  # 确保有内容可以裁剪
        out_image = out_image.crop(cropped_image)
    
    return out_image

@app.post("/generate")
async def generate_ascii_art(
    file: UploadFile = File(..., description="上传的图片文件"),
    text: str = "",
    num_cols: int = 300,
    background: str = "black",
    color: bool = True,
    portrait: bool = False,
    language: str = "chinese",
    mode: str = "standard"
):
    """
    生成ASCII艺术图片API
    
    Args:
        file: 上传的图片文件
        text: 用于生成ASCII艺术的文本
        num_cols: 输出图像的列数 (默认: 100)
        background: 背景颜色 ('black' 或 'white', 默认: 'black')
        color: 是否生成彩色图像 (默认: True)
        portrait: 是否使用竖排模式 (默认: False)
    
    Returns:
        JPEG格式的ASCII艺术图片
    """
    start_time = time.time()
    request_id = f"req_{int(start_time)}_{os.urandom(4).hex()}"
    temp_upload_path = None
    
    try:
        print(f"[{request_id}] 收到请求: text={text}, num_cols={num_cols}, "
              f"background={background}, color={color}, portrait={portrait}")
        
        # 参数验证
        if background not in ["black", "white"]:
            error_msg = f"[{request_id}] 无效的背景颜色: {background}"
            print(error_msg)
            raise HTTPException(status_code=400, detail="Background must be 'black' or 'white'")
        
        if num_cols <= 0 or num_cols > 1000:
            error_msg = f"[{request_id}] 无效的列数: {num_cols}"
            print(error_msg)
            raise HTTPException(status_code=400, detail="Number of columns must be between 1 and 1000")
            
        if not text.strip():
            error_msg = f"[{request_id}] 文本不能为空"
            print(error_msg)
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # 验证文件类型
        content_type = file.content_type
        if not content_type or not content_type.startswith('image/'):
            error_msg = f"[{request_id}] 无效的文件类型: {content_type}"
            print(error_msg)
            raise HTTPException(status_code=400, detail="File must be an image")
            
        print(f"[{request_id}] 参数验证通过")
        
        # 1. 保存上传的文件
        try:
            print(f"[{request_id}] 开始保存上传文件...")
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_upload:
                content = await file.read()
                if not content:
                    error_msg = f"[{request_id}] 上传的文件为空"
                    print(error_msg)
                    raise HTTPException(status_code=400, detail="Uploaded file is empty")
                
                file_size = len(content)
                if file_size > 10 * 1024 * 1024:  # 10MB限制
                    error_msg = f"[{request_id}] 文件大小超过10MB限制"
                    print(error_msg)
                    raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
                    
                temp_upload.write(content)
                temp_upload_path = temp_upload.name
                print(f"[{request_id}] 已保存上传文件到: {temp_upload_path} (大小: {file_size/1024:.2f} KB)")
        except HTTPException:
            raise
        except Exception as e:
            error_msg = f"[{request_id}] 保存上传文件失败: {str(e)}"
            print(error_msg)
            raise HTTPException(status_code=500, detail=f"保存上传文件失败: {str(e)}") from e
        
        try:
            # 2. 处理图片
            print(f"[{request_id}] 开始处理图片...")
            try:
                result_image = process_image(
                    temp_upload_path,
                    text=text,
                    num_cols=num_cols,
                    background=background,
                    color=color,
                    portrait=portrait,
                    language=language,
                    mode=mode
                )
                print(f"[{request_id}] 图片处理完成")
            except Exception as e:
                error_msg = f"[{request_id}] 处理请求时发生未预期的错误: {str(e)}"
                print(f"{error_msg}\n{traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=f"处理请求时发生错误: {str(e)}") from e
            
            # 3. 将结果保存到内存
            print(f"[{request_id}] 正在编码图片...")
            img_byte_arr = io.BytesIO()
            try:
                result_image.save(img_byte_arr, format='JPEG', quality=90, optimize=True)
                img_byte_arr.seek(0)
                result_size = len(img_byte_arr.getvalue()) / 1024  # KB
                process_time = time.time() - start_time
                print(f"[{request_id}] 图片编码完成. 大小: {result_size:.2f} KB, 处理时间: {process_time:.2f}秒")
                
                # 4. 返回图片数据
                return Response(
                    content=img_byte_arr.getvalue(),
                    media_type="image/jpeg",
                    headers={
                        "Content-Disposition": f"inline; filename=ascii_art_{int(time.time())}.jpg",
                        "X-Request-ID": request_id,
                        "X-Image-Size-KB": f"{result_size:.2f}",
                        "X-Process-Time": f"{process_time:.2f}s"
                    }
                )
            except Exception as e:
                error_msg = f"[{request_id}] 图片编码失败: {str(e)}"
                print(error_msg)
                raise HTTPException(status_code=500, detail=f"生成图片数据失败: {str(e)}") from e
                
        except HTTPException:
            raise
        except Exception as e:
            import traceback
            error_msg = f"[{request_id}] 处理图片时出错: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            raise HTTPException(status_code=500, detail=f"处理图片时出错: {str(e)}") from e
            
        finally:
            # 清理临时文件
            if temp_upload_path and os.path.exists(temp_upload_path):
                try:
                    os.unlink(temp_upload_path)
                    print(f"[{request_id}] 已清理临时文件: {temp_upload_path}")
                except Exception as e:
                    print(f"[{request_id}] 警告: 删除临时文件失败: {str(e)}")
                
    except HTTPException as he:
        # 记录HTTP异常
        print(f"[{request_id}] 请求处理失败 (HTTP {he.status_code}): {he.detail}")
        raise
    except Exception as e:
        import traceback
        error_msg = f"[{request_id}] 服务器内部错误: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        # 返回通用错误信息，避免泄露敏感信息
        raise HTTPException(
            status_code=500,
            detail="服务器内部错误，请稍后重试",
            headers={"X-Request-ID": request_id}
        ) from e

@app.get("/")
async def read_root():
    return {"message": "ASCII Art Generator API is running! Use /docs for interactive documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
