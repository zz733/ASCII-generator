"""
使用中文字符生成ASCII艺术图片
"""
import argparse
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def get_args():
    parser = argparse.ArgumentParser("Chinese Character ASCII Art")
    parser.add_argument("--input", type=str, default="demo/input.jpg", help="输入图片路径")
    parser.add_argument("--output", type=str, default="demo/chinese_output.jpg", help="输出图片路径")
    parser.add_argument("--chars", type=str, default="刘德华", help="用于生成ASCII艺术的字符")
    parser.add_argument("--num_cols", type=int, default=50, help="输出图片的字符宽度")
    parser.add_argument("--font_size", type=int, default=20, help="字体大小")
    return parser.parse_args()

def main():
    args = get_args()
    
    # 读取图片并转为灰度图
    image = cv2.imread(args.input)
    if image is None:
        print(f"错误：无法读取图片 {args.input}")
        return
        
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    height, width = gray.shape
    
    # 尝试加载中文字体
    try:
        # 尝试加载系统默认中文字体
        font = ImageFont.truetype("Arial Unicode.ttf", args.font_size)
    except IOError:
        try:
            # 如果找不到Arial Unicode，尝试其他常见中文字体
            font = ImageFont.truetype("SimHei.ttf", args.font_size)
        except IOError:
            try:
                font = ImageFont.truetype("msyh.ttc", args.font_size)
            except IOError:
                # 如果都找不到，使用默认字体
                print("警告：未找到中文字体，将使用默认字体，可能无法正确显示中文")
                font = ImageFont.load_default()
    # 获取字符大小
    bbox = font.getbbox("刘")
    char_width = bbox[2] - bbox[0]
    char_height = bbox[3] - bbox[1]
    
    # 计算行数和列数
    num_cols = min(args.num_cols, width)
    cell_width = width / num_cols
    cell_height = cell_width * (char_height / char_width)
    num_rows = int(height / cell_height)
    
    # 创建输出图片
    out_width = char_width * num_cols
    out_height = int(char_height * num_rows * 1.2)  # 1.2 是行距调整系数
    out_image = Image.new("RGB", (out_width, out_height), "white")
    draw = ImageDraw.Draw(out_image)
    
    # 生成ASCII艺术
    for i in range(num_rows):
        for j in range(num_cols):
            # 计算当前单元格的像素区域
            x1 = int(j * cell_width)
            y1 = int(i * cell_height)
            x2 = min(int((j + 1) * cell_width), width - 1)
            y2 = min(int((i + 1) * cell_height), height - 1)
            
            # 计算单元格的平均灰度值
            cell = gray[y1:y2, x1:x2]
            if cell.size == 0:
                continue
            avg_intensity = np.mean(cell)
            
            # 根据灰度值选择字符
            char_index = int((avg_intensity / 255.0) * (len(args.chars) - 1))
            char = args.chars[char_index]
            
            # 计算字符位置
            x = j * char_width
            y = i * int(char_height * 1.2)  # 1.2 是行距调整系数
            
            # 绘制字符
            draw.text((x, y), char, fill="black", font=font)
    
    # 保存图片
    out_image.save(args.output)
    print(f"ASCII艺术图片已保存到: {args.output}")

if __name__ == '__main__':
    main()
