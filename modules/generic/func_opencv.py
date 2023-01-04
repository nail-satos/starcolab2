### 必要な外部ライブラリをインポートする
import cv2
import numpy as np


### pillowのデータ型をOpenCVのデータ型に変換する関数
def pil2cv(image):

    ''' PIL型 -> OpenCV型 '''
    new_image = np.array(image, dtype=np.uint8)
    if new_image.ndim == 2:  # モノクロ
        pass
    elif new_image.shape[2] == 3:  # カラー
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
    elif new_image.shape[2] == 4:  # 透過
        new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)

    return new_image
# Docker Compose Python Streamlit OpenCV 画像の２値化処理webアプリをDocker上で稼働 | データサイエンス学習雑記
# https://data-science-learning.com/archives/688
