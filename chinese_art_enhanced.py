"""
增强版中文字符ASCII艺术生成器
使用"刘德华"三个字生成更清晰的ASCII艺术效果
"""
import argparse
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os

def get_args():
    parser = argparse.ArgumentParser("Enhanced Chinese Character ASCII Art")
    parser.add_argument("--input", type=str, default="demo/input.jpg", help="输入图片路径")
    parser.add_argument("--output", type=str, default="demo/chinese_enhanced.jpg", help="输出图片路径")
    parser.add_argument("--width", type=int, default=100, help="输出宽度（字符数）")
    parser.add_argument("--font_size", type=int, default=12, help="字体大小")
    parser.add_argument("--contrast", type=float, default=2.0, help="对比度增强系数（1.0-3.0）")
    return parser.parse_args()

def load_font(font_size):
    """尝试加载中文字体"""
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",  # macOS
        "C:/Windows/Fonts/msyh.ttc",           # Windows 雅黑
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",  # Linux
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, font_size)
            except:
                continue
    
    # 如果找不到中文字体，使用默认字体
    print("警告：未找到中文字体，将使用默认字体")
    return ImageFont.load_default()

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
        gray = cv2.convertScaleAbs(gray, alpha=args.contrast, beta=0)
        
        # 调整大小
        height, width = gray.shape
        aspect_ratio = width / height
        new_width = args.width
        new_height = int(new_width / aspect_ratio * 0.5)  # 修正字符的宽高比
        
        resized = cv2.resize(gray, (new_width, new_height))
        
        # 创建字符图片
        char_size = args.font_size * 2
        chars = "刘德华"
        char_imgs = []
        
        # 为每个字符创建图片
        for char in chars:
            # 创建临时图片
            temp_img = Image.new('L', (char_size, char_size), 255)
            draw = ImageDraw.Draw(temp_img)
            
            # 尝试使用不同字体大小
            for fs in range(args.font_size, 5, -1):
                try:
                    font = ImageFont.truetype("PingFang.ttc", fs)
                    break
                except:
                    try:
                        font = ImageFont.truetype("Arial Unicode.ttf", fs)
                        break
                    except:
                        if fs == 6:  # 如果都失败，使用默认字体
                            font = ImageFont.load_default()
            
            # 绘制字符
            draw.text((0, 0), char, fill=0, font=font)
            char_imgs.append(temp_img)
        
        # 获取字符图片的平均亮度
        char_weights = []
        for img in char_imgs:
            # 计算字符图片的平均亮度（0-255，0为最暗）
            avg_brightness = 255 - np.mean(np.array(img))
            char_weights.append(avg_brightness)
        
        # 按亮度排序字符（从暗到亮）
        sorted_indices = np.argsort(char_weights)
        sorted_chars = [chars[i] for i in sorted_indices]
        sorted_imgs = [char_imgs[i] for i in sorted_indices]
        
        # 创建输出图片
        char_width, char_height = char_size, char_size
        output_width = char_width * new_width
        output_height = char_height * new_height
        output_img = Image.new('L', (output_width, output_height), 255)
        
        # 生成ASCII艺术
        for i in range(new_height):
            for j in range(new_width):
                # 获取当前像素的亮度
                pixel = resized[i, j]
                # 将亮度映射到中文字符集
                char_index = min(int((pixel / 255) * len(sorted_chars)), len(sorted_chars) - 1)
                char_img = sorted_imgs[char_index]
                # 粘贴字符图片
                output_img.paste(char_img, (j * char_width, i * char_height))
        
        # 保存图片
        output_img.save(args.output)
        print(f"中文字符艺术图片已保存到: {args.output}")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main()
