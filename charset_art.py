"""
字符集ASCII艺术生成器
使用自定义字符集（包含中英文字符）生成ASCII艺术
"""
import argparse
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def get_args():
    parser = argparse.ArgumentParser("Character Set ASCII Art")
    parser.add_argument("--input", type=str, default="demo/input.jpg", help="输入图片路径")
    parser.add_argument("--output", type=str, default="demo/charset_art.jpg", help="输出图片路径")
    parser.add_argument("--width", type=int, default=100, help="输出宽度（字符数）")
    parser.add_argument("--font_size", type=int, default=12, help="字体大小")
    return parser.parse_args()

def main():
    args = get_args()
    
    try:
        # 读取图片
        img = cv2.imread(args.input)
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
        new_width = args.width
        new_height = int(new_width / aspect_ratio * 0.5)  # 修正字符的宽高比
        
        resized = cv2.resize(gray, (new_width, new_height))
        
        # 定义字符集（从最暗到最亮）
        # 混合使用中英文字符
        chars = "@%#*+=-:. "  # 基础字符
        chinese_chars = "刘德华"  # 中文字符
        
        # 创建混合字符集
        mixed_chars = list(chars) + list(chinese_chars)
        
        # 创建输出图片
        font_size = args.font_size
        output_img = Image.new('RGB', (new_width * font_size, new_height * font_size * 2), color='white')
        draw = ImageDraw.Draw(output_img)
        
        # 尝试加载中文字体
        try:
            font = ImageFont.truetype("PingFang.ttc", font_size)
        except:
            try:
                font = ImageFont.truetype("Arial Unicode.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # 生成ASCII艺术
        for i in range(new_height):
            for j in range(new_width):
                # 获取当前像素的亮度
                pixel = resized[i, j]
                
                # 将亮度映射到混合字符集
                char_index = int((pixel / 255) * (len(mixed_chars) - 1))
                char = mixed_chars[char_index]
                
                # 计算字符位置
                x = j * font_size
                y = i * font_size * 2  # 增加行距以容纳中文字符
                
                # 绘制字符
                draw.text((x, y), char, fill="black", font=font)
        
        # 保存图片
        output_img.save(args.output)
        print(f"字符集艺术图片已保存到: {args.output}")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        raise

if __name__ == "__main__":
    main()
