from pickle import TRUE
import requests
from PIL import Image
from io import BytesIO
import os

def test_api():
    # 1. 测试GET请求
    print("Testing GET /")
    response = requests.get("http://127.0.0.1:8000/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_generate(text=None, num_cols=300, background="black", color=True, portrait=False, language="chinese", mode="standard", image_path=None):
    """
    测试生成ASCII艺术图
    
    Args:
        image_path: 测试图片路径，如果为None则使用demo/input.jpg
    """
    print(f"\nTesting with: text={text}, num_cols={num_cols}, background={background}, color={color}, portrait={portrait}, language={language}, mode={mode}")
    
    # 设置默认图片路径
    if image_path is None:
        image_path = os.path.join("demo", "input.jpg")
    
    # 检查图片是否存在
    if not os.path.exists(image_path):
        print(f"Error: Test image not found at {image_path}")
        return False
        
    print(f"Using test image: {image_path}")
    with open(image_path, 'rb') as f:
        img_byte_arr = BytesIO(f.read())
    
    # 准备请求参数
    files = {'file': ('test.jpg', img_byte_arr, 'image/jpeg')}
    params = {
        "num_cols": num_cols,
        "background": background,
        "color": color,  # 直接传递布尔值，FastAPI会自动处理
        "portrait": portrait,  # 直接传递布尔值
        "language": language,
        "mode": mode,
        "text": text if text is not None else ""  # 确保text参数总是存在
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/generate",
            params=params,
            files=files
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            # 生成输出文件名
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            
            filename_parts = []
            # 始终添加语言和模式信息
            filename_parts.append(language)
            filename_parts.append(mode)
            
            # 如果有自定义文本，添加到文件名中
            if text:
                filename_parts.append(text[:10])
                
            # 添加其他参数信息
            filename_parts.append(f"cols{num_cols}")
            filename_parts.append(background)
            filename_parts.append("color" if color else "bw")
            if portrait:
                filename_parts.append("portrait")
                
            output_file = os.path.join(output_dir, f"{'__'.join(filename_parts)}.jpg")
            
            # 保存返回的图片
            with open(output_file, "wb") as f:
                f.write(response.content)
            print(f"Image saved as '{output_file}'")
            
            # 不自动打开图片，只打印保存路径
            print(f"Image saved to: {os.path.abspath(output_file)}")
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Request failed: {e}")
        return False
        
    return True

def run_tests():
    # 设置测试图片路径
    test_image = os.path.join("demo", "input2.jpg")
    
    # 测试1: 使用默认字符集
    test_generate(text="江雪利", color=True,language="chinese", mode="standard", image_path=test_image)
    
    # 测试2: 自定义文本
    test_generate(text="江雪利", color=True,num_cols=200, image_path=test_image)
    
    # 测试3: 黑白模式
    test_generate(text="江雪利", color=True, image_path=test_image)
    
    # 测试4: 竖排模式
    test_generate(text="江雪利", color=True,portrait=True, image_path=test_image)
    
    # 测试5: 白底黑字
    test_generate(text="江雪利", color=True,background="white", image_path=test_image)
    
    # 测试6: 使用英文默认字符集
    test_generate(text="江雪利", color=True,language="english", mode="standard", image_path=test_image)
    
    # 测试7: 密集字符集
    test_generate(text="江雪利", color=True,language="chinese", mode="dense", image_path=test_image)

if __name__ == "__main__":
    # 测试所有用例
    run_tests()
