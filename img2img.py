"""
@author: Viet Nguyen <nhviet1009@gmail.com>
"""
import argparse
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageOps, ImageFont
from utils import get_data


def get_args():
    parser = argparse.ArgumentParser("Image to ASCII")
    parser.add_argument("--input", type=str, default="data/input.jpg", help="Path to input image")
    parser.add_argument("--output", type=str, default="data/output.jpg", help="Path to output image file")
    parser.add_argument("--language", type=str, default="english", 
                        help="Character set language (english, chinese, etc.) or 'custom' for custom text")
    parser.add_argument("--custom_text", type=str, default="",
                        help="Custom text to use for ASCII art (e.g., '刘德华', '张学友')")
    parser.add_argument("--mode", type=str, default="standard",
                        help="Character set mode (standard, dense, sparse, etc.)")
    parser.add_argument("--background", type=str, default="black", choices=["black", "white"],
                        help="background's color")
    parser.add_argument("--num_cols", type=int, default=300, help="number of character for output's width")
    parser.add_argument("--color", action="store_true", help="Enable color output")
    parser.add_argument("--portrait", action="store_true", help="Optimize for portrait orientation (vertical images)")
    args = parser.parse_args()
    return args


def main(opt):
    # 设置背景色
    if opt.background == "white":
        bg_code = 255
    else:
        bg_code = 0
    
    # 处理自定义文本
    if opt.custom_text:
        # 使用自定义文本作为字符集
        char_list = opt.custom_text * 100  # 重复多次以确保有足够的字符
        
        # 设置中文字体
        try:
            # 尝试加载系统中文字体（macOS和Linux常见路径）
            font_paths = [
                "/System/Library/Fonts/PingFang.ttc",  # macOS 苹方
                "/System/Library/Fonts/STHeiti Light.ttc",  # macOS 黑体
                "/System/Library/Fonts/STHeiti Medium.ttc",
                "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",  # 文泉驿微米黑
                "simsun.ttc"  # Windows 宋体
            ]
            
            font = None
            for font_path in font_paths:
                try:
                    font = ImageFont.truetype(font_path, size=12)
                    print(f"使用字体: {font_path}")
                    break
                except:
                    continue
            
            if font is None:
                # 如果找不到中文字体，使用默认字体
                print("警告: 找不到中文字体，使用默认字体")
                font = ImageFont.load_default()
            
            sample_character = char_list[0] if char_list else "A"
            scale = 1.5  # 调整行高比例
            num_chars = len(set(char_list))  # 去重后的字符数量
            
        except Exception as e:
            print(f"使用自定义文本时出错: {e}, 回退到默认字符集")
            char_list, font, sample_character, scale = get_data(opt.language, opt.mode)
    else:
        # 使用预定义的字符集
        char_list, font, sample_character, scale = get_data(opt.language, opt.mode)
    
    num_chars = len(set(char_list))  # 使用唯一字符数量
    num_cols = opt.num_cols
    
    # 读取图片
    image = cv2.imread(opt.input)
    if image is None:
        raise ValueError(f"无法加载图片: {opt.input}")
    
    # 转换为RGB颜色空间
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width = image.shape[:2]
    
    # 如果不是彩色模式，转换为灰度图
    if not opt.color:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 计算单元格大小和行列数
    if opt.portrait and width > height:
        # 如果是横屏图片但启用了竖屏模式，则旋转图片
        image_rgb = cv2.rotate(image_rgb, cv2.ROTATE_90_CLOCKWISE)
        if not opt.color:
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        height, width = image_rgb.shape[:2]
    
    cell_width = width / opt.num_cols
    cell_height = scale * cell_width
    num_rows = int(height / cell_height)
    
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
    
    if opt.color:
        out_image = Image.new("RGB", (out_width, out_height), (bg_code, bg_code, bg_code))
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
            if opt.color:
                # 彩色模式：获取平均颜色
                region = image_rgb[y_start:y_end, x_start:x_end]
                if region.size > 0:
                    # 使用简单平均值计算颜色和灰度
                    avg_color = tuple(np.mean(region, axis=(0, 1)).astype(int))
                    # 计算灰度值用于选择字符
                    gray = np.mean(region)
                else:
                    avg_color = (bg_code, bg_code, bg_code)
                    gray = bg_code
            else:
                # 灰度模式
                region = image[y_start:y_end, x_start:x_end]
                gray = np.mean(region) if region.size > 0 else bg_code
            
            # 打印调试信息
            if i == num_rows // 2 and j == num_cols // 2:  # 只打印图像中心区域的信息
                print(f"原始灰度值: {gray:.1f}")
                
            # 确保灰度值在有效范围内
            gray = max(0, min(255, gray))
            
            # 调整亮度和对比度
            # 1. 提高整体亮度
            gray = min(255, gray * 1.3)
            
            # 2. 使用非线性映射增强暗部细节
            normalized_gray = (gray / 255.0) ** 0.8
            
            # 3. 确保最小字符索引为1（避免使用最暗的字符）
            char_idx = max(1, int(normalized_gray * (num_chars - 1)))
            char_idx = min(char_idx, num_chars - 1)
            
            if i == num_rows // 2 and j == num_cols // 2:  # 只打印图像中心区域的信息
                print(f"处理后灰度值: {gray:.1f}, 字符索引: {char_idx}")
            char = char_list[char_idx]
            
            # 计算绘制位置
            if opt.portrait:
                # 竖排文字（从上到下，从右到左）
                x = out_width - (j + 1) * char_width
                y = i * char_height * scale
            else:
                # 横排文字（从左到右，从上到下）
                x = j * char_width
                y = i * char_height * scale
            
            # 绘制字符
            if opt.color and region.size > 0:
                draw.text((x, y), char, fill=tuple(avg_color), font=font)
            else:
                fill_color = 255 - bg_code if region.size > 0 else bg_code
                draw.text((x, y), char, fill=fill_color, font=font)
    
    # 裁剪图片
    if opt.background == "white" and not opt.color:
        cropped_image = ImageOps.invert(out_image).getbbox()
    else:
        cropped_image = out_image.getbbox()
    
    if cropped_image:  # 确保有内容可以裁剪
        out_image = out_image.crop(cropped_image)
    
    # 保存图片
    out_image.save(opt.output, quality=95)
    print(f"Image saved to {opt.output}")


if __name__ == '__main__':
    opt = get_args()
    main(opt)
