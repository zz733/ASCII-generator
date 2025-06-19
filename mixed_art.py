"""
混合字符ASCII艺术生成器
结合中英文字符生成更好的艺术效果
"""
import argparse
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def get_args():
    parser = argparse.ArgumentParser("Mixed Character ASCII Art")
    parser.add_argument("--input", type=str, default="demo/input.jpg", help="输入图片路径")
    parser.add_argument("--output", type=str, default="demo/mixed_art.jpg", help="输出图片路径")
    parser.add_argument("--width", type=int, default=150, help="输出宽度（字符数）")
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
        
        # 创建输出图片
        font_size = 10
        font = ImageFont.load_default()
        char_width, char_height = 6, 12  # 默认字体大小
        
        output_width = char_width * new_width
        output_height = char_height * new_height
        output_img = Image.new('RGB', (output_width, output_height), color='white')
        draw = ImageDraw.Draw(output_img)
        
        # 生成ASCII艺术
        for i in range(new_height):
            for j in range(new_width):
                # 获取当前像素的亮度
                pixel = resized[i, j]
                
                # 根据位置决定使用中文字符还是英文字符
                # 在图片中心区域使用中文字符
                center_region = (i > new_height/4 and i < 3*new_height/4 and 
                               j > new_width/4 and j < 3*new_width/4)
                
                if center_region and chinese_chars:
                    # 使用中文字符
                    char_index = int((pixel / 255) * (len(chinese_chars) - 1))
                    char = chinese_chars[char_index]
                    # 使用更大的字体突出显示中文字符
                    try:
                        large_font = ImageFont.truetype("PingFang.ttc", font_size*2)
                        draw.text((j*char_width, i*char_height), char, fill="black", font=large_font)
                    except:
                        # 如果找不到中文字体，使用默认字体
                        draw.text((j*char_width, i*char_height), char, fill="black", font=font)
                else:
                    # 使用英文字符
                    char_index = int((pixel / 255) * (len(chars) - 1))
                    char = chars[char_index]
                    draw.text((j*char_width, i*char_height), char, fill="black", font=font)
        
        # 保存图片
        output_img.save(args.output)
        print(f"混合字符艺术图片已保存到: {args.output}")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main()
