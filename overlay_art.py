"""
叠加式ASCII艺术生成器
先生成清晰的ASCII艺术图，然后叠加中文字符
"""
import argparse
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

def get_args():
    parser = argparse.ArgumentParser("Overlay ASCII Art")
    parser.add_argument("--input", type=str, default="demo/input.jpg", help="输入图片路径")
    parser.add_argument("--output", type=str, default="demo/overlay_art.jpg", help="输出图片路径")
    parser.add_argument("--width", type=int, default=150, help="输出宽度（字符数）")
    return parser.parse_args()

def create_ascii_art(image_path, output_width=150):
    """生成清晰的ASCII艺术图"""
    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        raise Exception("无法读取图片")
    
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 增强对比度
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    
    # 调整大小
    height, width = gray.shape
    aspect_ratio = width / height
    new_width = output_width
    new_height = int(new_width / aspect_ratio * 0.5)  # 修正字符的宽高比
    
    resized = cv2.resize(gray, (new_width, new_height))
    
    # 定义字符集（从最暗到最亮）
    chars = "@%#*+=-:. "
    
    # 创建ASCII艺术文本
    ascii_art = []
    for i in range(new_height):
        line = []
        for j in range(new_width):
            pixel = resized[i, j]
            char_index = int((pixel / 255) * (len(chars) - 1))
            line.append(chars[char_index])
        ascii_art.append("".join(line))
    
    return ascii_art, new_width, new_height

def main():
    args = get_args()
    
    try:
        # 生成ASCII艺术
        ascii_art, width, height = create_ascii_art(args.input, args.width)
        
        # 创建输出图片
        font_size = 10
        char_width, char_height = 6, 12  # 默认字体大小
        output_width = char_width * width
        output_height = char_height * height
        
        # 创建基础ASCII艺术图片
        output_img = Image.new('RGB', (output_width, output_height), color='white')
        draw = ImageDraw.Draw(output_img)
        font = ImageFont.load_default()
        
        # 绘制ASCII艺术
        for i, line in enumerate(ascii_art):
            draw.text((0, i * char_height), line, fill="black", font=font)
        
        # 添加"刘德华"文字
        try:
            # 尝试使用中文字体
            chinese_font = ImageFont.truetype("PingFang.ttc", 80)
        except:
            try:
                chinese_font = ImageFont.truetype("Arial Unicode.ttf", 80)
            except:
                chinese_font = ImageFont.load_default()
        
        # 在图片中心添加"刘德华"
        text = "刘 德 华"
        # 使用 textbbox 替代 getsize
        left, top, right, bottom = chinese_font.getbbox(text)
        text_width = right - left
        text_height = bottom - top
        x = (output_width - text_width) // 2
        y = (output_height - text_height) // 2
        
        # 添加文字描边效果
        for x_offset in [-2, 0, 2]:
            for y_offset in [-2, 0, 2]:
                if x_offset == 0 and y_offset == 0:
                    continue
                draw.text((x + x_offset, y + y_offset), text, fill="black", font=chinese_font)
        
        # 添加白色文字（产生描边效果）
        draw.text((x, y), text, fill="white", font=chinese_font)
        
        # 保存图片
        output_img.save(args.output)
        print(f"叠加式艺术图片已保存到: {args.output}")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        raise

if __name__ == "__main__":
    main()
