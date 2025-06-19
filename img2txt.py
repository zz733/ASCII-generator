"""
@author: Viet Nguyen <nhviet1009@gmail.com>
"""
import argparse

import cv2
import numpy as np


def get_args():
    parser = argparse.ArgumentParser("Image to ASCII")
    parser.add_argument("--input", type=str, default="data/input.jpg", help="Path to input image")
    parser.add_argument("--output", type=str, default="data/output.txt", help="Path to output text file")
    parser.add_argument("--mode", type=str, default="complex", choices=["simple", "complex"],
                        help="10 or 70 different characters")
    parser.add_argument("--num_cols", type=int, default=80, help="number of character for output's width")
    parser.add_argument("--color", action="store_true", help="Enable color output (only works when outputting to terminal)")
    parser.add_argument("--output_image", type=str, help="Save as a colored image (e.g., output.png)")
    parser.add_argument("--font_size", type=int, default=10, help="Font size for output image")
    args = parser.parse_args()
    return args


def main(opt):
    if opt.mode == "simple":
        CHAR_LIST = '@%#*+=-:. '
    else:
        CHAR_LIST = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "
    num_chars = len(CHAR_LIST)
    num_cols = opt.num_cols
    
    # 读取图片并转换颜色空间
    image = cv2.imread(opt.input)
    if image is None:
        raise ValueError(f"无法加载图片: {opt.input}")
        
    # 转换颜色空间
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width = image.shape[:2]
    
    # 如果是灰度模式，转换为灰度图
    if not (opt.color or opt.output_image):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cell_width = width / opt.num_cols
    cell_height = 2 * cell_width
    num_rows = int(height / cell_height)
    if num_cols > width or num_rows > height:
        print("Too many columns or rows. Use default setting")
        cell_width = 6
        cell_height = 12
        num_cols = int(width / cell_width)
        num_rows = int(height / cell_height)

    # 准备输出
    output = []
    color_data = []
    
    for i in range(num_rows):
        line = ""
        line_colors = []
        for j in range(num_cols):
            # 获取当前字符区域
            y_start = int(i * cell_height)
            y_end = min(int((i + 1) * cell_height), height)
            x_start = int(j * cell_width)
            x_end = min(int((j + 1) * cell_width), width)
            
            if opt.color or opt.output_image:
                # 计算平均颜色
                region = image_rgb[y_start:y_end, x_start:x_end]
                avg_color = np.mean(region, axis=(0, 1)).astype(int)
                r, g, b = avg_color
                
                # 计算灰度值用于选择字符
                gray = np.mean(region) if len(region) > 0 else 0
                char = CHAR_LIST[min(int(gray * num_chars / 255), num_chars - 1)]
                
                # 保存颜色信息
                line_colors.append((r, g, b))
                
                # 添加ANSI颜色代码（仅当输出到终端时）
                if opt.color and not opt.output_image:
                    line += f"\033[38;2;{r};{g};{b}m{char}"
                else:
                    line += char
            else:
                # 灰度模式
                region = image[y_start:y_end, x_start:x_end]
                gray = np.mean(region) if len(region) > 0 else 0
                char = CHAR_LIST[min(int(gray * num_chars / 255), num_chars - 1)]
                line += char
        
        if opt.color and not opt.output_image:
            line += "\033[0m"  # 重置颜色
        output.append(line + "\n")
        if opt.output_image:
            color_data.append(line_colors)
    
    # 保存为图片
    if opt.output_image:
        from PIL import Image, ImageDraw, ImageFont
        import os
        
        # 计算图片尺寸
        font_size = opt.font_size
        font = ImageFont.truetype("Arial.ttf" if os.name == 'nt' else "/System/Library/Fonts/Menlo.ttc", 
                                 font_size)
        char_width = font.getlength('M')  # 使用'M'作为参考字符
        char_height = font_size * 1.2  # 添加一些行间距
        
        # 创建新图片
        img_width = int(num_cols * char_width)
        img_height = int(num_rows * char_height)
        img = Image.new('RGB', (img_width, img_height), color='black')
        draw = ImageDraw.Draw(img)
        
        # 绘制文字
        for i, (line, colors) in enumerate(zip(output, color_data)):
            y = i * char_height
            for j, ((r, g, b), char) in enumerate(zip(colors, line.strip())):
                x = j * char_width
                draw.text((x, y), char, fill=(r, g, b), font=font)
        
        # 保存图片
        img.save(opt.output_image)
        print(f"Color ASCII art saved to {opt.output_image}")
    
    # 写入文本文件
    if opt.output:
        with open(opt.output, 'w', encoding='utf-8') as f:
            f.writelines(output)
    
    # 如果输出到终端，直接打印结果
    if opt.output != '/dev/stdout' and not opt.output_image:
        print(''.join(output), end='')
    elif opt.output_image:
        print(f"Text output saved to {opt.output}" if opt.output else "")


if __name__ == '__main__':
    opt = get_args()
    main(opt)
