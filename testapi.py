import requests
from PIL import Image
from io import BytesIO

def test_api():
    # 1. 测试GET请求
    print("Testing GET /")
    response = requests.get("http://127.0.0.1:8000/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

    # 2. 准备测试图片
    print("Creating test image...")
    img = Image.new('RGB', (400, 400), color='red')
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)

    # 3. 测试POST请求
    print("\nTesting POST /generate")
    files = {
        'file': ('test.jpg', img_byte_arr, 'image/jpeg')
    }
    params = {
        "text": "刘德华",
        "num_cols": 80,
        "background": "black",
        "color": "true",
        "portrait": "false"
    }
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/generate",
            params=params,
            files=files
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            # 保存返回的图片
            with open("test_output.jpg", "wb") as f:
                f.write(response.content)
            print("Image saved as 'test_output.jpg'")
            
            # 尝试显示图片
            try:
                img = Image.open("test_output.jpg")
                img.show()
            except Exception as e:
                print(f"Could not display image: {e}")
        else:
            print(f"Error: {response.text}")

    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_api()
