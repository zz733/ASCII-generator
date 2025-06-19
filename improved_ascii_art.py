"""
改进的ASCII艺术生成器
使用更精细的字符集和图像处理来生成更好的效果
"""
import argparse
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def get_args():
    parser = argparse.ArgumentParser("Improved ASCII Art Generator")
    parser.add_argument("--input", type=str, default="demo/input.jpg", help="输入图片路径")
    parser.add_argument("--output", type=str, default="demo/improved_art.jpg", help="输出图片路径")
    parser.add_argument("--width", type=int, default=150, help="输出宽度（字符数）")
    parser.add_argument("--invert", action="store_true", help="反转颜色（黑底白字）")
    return parser.parse_args()

def main():
    args = get_args()
    
    # 读取图片
    try:
        img = cv2.imread(args.input)
        if img is None:
            raise Exception("无法读取图片")
        
        # 转换为灰度图并调整对比度
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 调整对比度
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        
        # 调整大小
        height, width = gray.shape
        aspect_ratio = width / height
        new_width = args.width
        new_height = int(new_width / aspect_ratio * 0.5)  # 修正字符的宽高比
        
        resized = cv2.resize(gray, (new_width, new_height))
        
        # 定义字符集（从最暗到最亮）
        chars = "@%#*+=-:. "
        if args.invert:
            chars = chars[::-1]
        
        # 创建输出图片
        font_size = 10
        font = ImageFont.load_default()
        char_width, char_height = 6, 12  # 默认字体大小
        
        output_width = char_width * new_width
        output_height = char_height * new_height
        output_img = Image.new('RGB', (output_width, output_height), color='white' if not args.invert else 'black')
        draw = ImageDraw.Draw(output_img)
        
        # 生成ASCII艺术
        for i in range(new_height):
            for j in range(new_width):
                # 获取当前像素的亮度
                pixel = resized[i, j]
                # 将亮度映射到字符集
                char_index = int((pixel / 255) * (len(chars) - 1))
                char = chars[char_index]
                # 绘制字符
                x = j * char_width
                y = i * char_height
                fill_color = (0, 0, 0) if not args.invert else (255, 255, 255)
                draw.text((x, y), char, fill=fill_color, font=font)
        
        # 保存图片
        output_img.save(args.output)
        print(f"ASCII艺术图片已保存到: {args.output}")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main()
