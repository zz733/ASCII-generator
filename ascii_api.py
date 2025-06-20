import os
import io
import cv2
import numpy as np
import traceback
from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import Response, StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Union, BinaryIO
import time
from PIL import Image, ImageDraw, ImageFont, ImageOps
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    # 始终使用中文字符集
    from utils import get_data
    
    # 如果提供了文本，则使用文本中的字符，否则使用默认中文字符集
    if text and text.strip():
        # 使用自定义文本作为字符集，去重并确保有足够的字符
        unique_chars = list(dict.fromkeys(text))  # 去重保持顺序
        if not unique_chars:
            unique_chars = ['*']  # 如果文本中没有有效字符，使用默认字符
        # 添加一些灰度字符以增强细节表现
        if len(unique_chars) < 10:
            unique_chars.extend(['。', '，', '、', '：', '；', '“', '”', '《', '》', '（', '）'])
        # 重复字符集以确保有足够的字符用于绘制
        char_list = (unique_chars * (100 // len(unique_chars) + 1))[:100]
        
        # 设置中文字体，增大字体大小以显示更多细节
        font_size = 14
        font = get_font(font_size)
        sample_character = char_list[0] if char_list else "A"
        scale = 1.6  # 增加行高比例
    else:
        # 使用预定义的中文字符集，使用dense模式获取更清晰的字符集
        char_list, font, sample_character, scale = get_data("chinese", "dense")
        # 调整字体大小以优化显示效果
        font = get_font(14)  # 增大字体大小
    
    num_chars = len(set(char_list))  # 唯一字符数量
    
    # 处理图片
    if isinstance(image_path, (str, os.PathLike)):
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"无法读取图片: {image_path}")
    else:
        # 如果是文件对象，从内存中读取
        file_bytes = np.asarray(bytearray(image_path.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    
    # 1. 调整图像大小，保持宽高比
    height, width = image.shape[:2]
    aspect_ratio = width / height
    new_height = int(num_cols / aspect_ratio * 1.5)  # 调整高度比例
    image = cv2.resize(image, (num_cols, new_height), interpolation=cv2.INTER_CUBIC)
    
    # 2. 应用高斯模糊去噪
    image = cv2.GaussianBlur(image, (3, 3), 0)
    
    # 3. 应用自适应直方图均衡化 (CLAHE)
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl,a,b))
    image = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    
    # 4. 锐化图像
    kernel = np.array([[-1,-1,-1],
                      [-1, 9,-1],
                      [-1,-1,-1]])
    image = cv2.filter2D(image, -1, kernel)
    
    # 转换为RGB颜色空间
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width = image.shape[:2]
    
    if color:
        # 对彩色图像应用CLAHE增强对比度
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl,a,b))
        image_enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
        image_rgb = cv2.cvtColor(image_enhanced, cv2.COLOR_BGR2RGB)
    else:
        # 对灰度图应用直方图均衡化
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image_gray = cv2.equalizeHist(image_gray)
    
    # 如果是横屏图片但启用了竖屏模式，则旋转图片
    if portrait and width > height:
        if color:
            image_rgb = cv2.rotate(image_rgb, cv2.ROTATE_90_CLOCKWISE)
        else:
            image_gray = cv2.rotate(image_gray, cv2.ROTATE_90_CLOCKWISE)
        height, width = (width, height)  # 交换宽高
    
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
    
    # 获取字符大小
    temp_img = Image.new('L', (100, 100), 255)
    draw = ImageDraw.Draw(temp_img)
    bbox = draw.textbbox((0, 0), sample_character, font=font)
    char_width, char_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    # 调整字符大小和间距
    char_spacing = 0  # 字符间距
    line_spacing = 0   # 行间距
    
    # 计算输出图片大小
    out_width = num_cols * char_width
    out_height = int(num_rows * char_height * 1.5)  # 1.5倍行高
    
    # 创建输出图片
    if color:
        out_image = Image.new("RGB", (out_width, out_height), (0, 0, 0) if background == "black" else (255, 255, 255))
    else:
        out_image = Image.new("L", (out_width, out_height), 0 if background == "black" else 255)
    
    draw = ImageDraw.Draw(out_image)
    
    if color:
        # 彩色模式下使用与背景色对应的 RGB 颜色
        bg_rgb = (255, 255, 255) if background == "white" else (0, 0, 0)
        out_image = Image.new("RGB", (out_width, out_height), bg_rgb)
    else:
        out_image = Image.new("L", (out_width, out_height), bg_code)
    
    draw = ImageDraw.Draw(out_image)
    
    # 处理每个单元格
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
                    # 计算平均颜色
                    avg_color = tuple(np.mean(region, axis=(0, 1)).astype(int))
                    # 计算灰度值用于选择字符（使用简单平均值，与img2img.py一致）
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
            x = j * char_width
            y = i * int(char_height * 1.5)  # 1.5倍行高
            
            # 绘制字符
            if color:
                if region.size > 0:
                    draw.text((x, y), char, fill=tuple(avg_color), font=font)
            else:
                # 黑白模式
                fill_color = 255 - int(gray) if background == "black" else int(gray)
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
    color: bool = Query(True, description="是否生成彩色图像"),
    portrait: bool = False,
    language: str = "chinese",
    mode: str = "standard"
):
    """
    生成ASCII艺术图片API (优化版)
    
    Args:
        file: 上传的图片文件
        text: 用于生成ASCII艺术的文本
        num_cols: 输出图像的列数
        background: 背景颜色 ('black' 或 'white')
        color: 是否生成彩色图像
        portrait: 是否使用竖排模式
        language: 字符集语言 ('chinese' 或 'english')
        mode: 字符集模式 ('standard' 或 'dense')
    """
    print(f"API received parameters - color: {color}, type: {type(color)}")  # 调试信息
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
    
    try:
        # 参数验证
        if background not in ["black", "white"]:
            raise HTTPException(status_code=400, detail="Background must be 'black' or 'white'")
        
        if num_cols <= 0 or num_cols > 1000:
            raise HTTPException(status_code=400, detail="Number of columns must be between 1 and 1000")
            
        # 如果 text 为空字符串，使用 language 和 mode 获取默认字符集
        if not text.strip():
            text = None  # 设置为 None 让 process_image 使用默认字符集
        
        # 验证文件类型
        content_type = file.content_type
        if not content_type or not content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
            
        # 直接读取文件内容到内存
        file_content = await file.read()
        
        # 处理图片
        start_process = time.time()
        print(f"Processing image with color mode: {color}")  # 调试信息
        result_image = process_image(
            io.BytesIO(file_content),  # 使用BytesIO避免临时文件
            text=text,
            num_cols=num_cols,
            background=background,
            color=color,
            portrait=portrait,
            language=language,
            mode=mode
        )
        print(f"Generated image mode: {result_image.mode}")  # 调试信息
        process_time = time.time() - start_process
        
        # 将图片转换为字节流
        img_byte_arr = io.BytesIO()
        result_image.save(img_byte_arr, format='JPEG', quality=95)
        img_byte_arr = img_byte_arr.getvalue()
        
        # 记录处理时间
        logger.info(f"Image processed in {process_time:.2f} seconds")
        
        # 返回图片
        return Response(
            content=img_byte_arr,
            media_type="image/jpeg",
            headers={
                "X-Processing-Time": f"{process_time:.2f}s"
            }
        )
            
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
