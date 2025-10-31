import base64
from io import BytesIO
from PIL import Image


def encode_image_base64(image: Image.Image) -> str:
    """이미지를 Base64로 인코딩"""
    buf = BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")
