### 必要な標準ライブラリをインポートする
from PIL import Image   # 画像表示用
import requests         # Custom Vison APIコール用
import io               # 画像データのバイナリ変換用

### 必要な外部ライブラリをインポートする
import streamlit as st
import cv2
import numpy as np

### 自作のモジュールをインポートする ###
from modules.generic import func_opencv


### 定数の設定
PROBABILITY_THRESHOLD_BODY = 0.30     # 物体検出の閾値
PROBABILITY_THRESHOLD_FACE = 0.05     # 物体検出の閾値
PROBABILITY_THRESHOLD_HEAD = 0.05     # 物体検出の閾値

# ### pillowのデータ型をOpenCVのデータ型に変換する関数
# def pil2cv(image):

#     ''' PIL型 -> OpenCV型 '''
#     new_image = np.array(image, dtype=np.uint8)
#     if new_image.ndim == 2:  # モノクロ
#         pass
#     elif new_image.shape[2] == 3:  # カラー
#         new_image = cv2.cvtColor(new_image, cv2.COLOR_RGB2BGR)
#     elif new_image.shape[2] == 4:  # 透過
#         new_image = cv2.cvtColor(new_image, cv2.COLOR_RGBA2BGRA)

#     return new_image
# # Docker Compose Python Streamlit OpenCV 画像の２値化処理webアプリをDocker上で稼働 | データサイエンス学習雑記
# # https://data-science-learning.com/archives/688


### レッスンのメイン画面を表示する関数
def view_activity(step_dict={}, status_dict={}):

    ### 各種フラグなどを初期化するセクション ###
    if 'init_flg' not in st.session_state:

        st.session_state['init_flg'] = True         # 初期化(済)フラグをオンに設定
        st.session_state['load_flg'] = False        # イメージファイルを読んだか否か
  

    st.header('アプリ「AIで群衆を認識しよう」')
    st.sidebar.subheader('難易度を選んで「認識開始」ボタンを押してください')

    level_list = ["初級", "中級", "上級", "好きな画像をアップロード"]
    level = st.sidebar.radio("難易度を選択してください", level_list, horizontal=True)

    ## 初級～上級が選択されている場合...
    if level_list.index(level) == 0:
        img_pil = Image.open('./assets/lesson/ai00_01/a1-010.jpg')        
    if level_list.index(level) == 1:
        img_pil = Image.open('./assets/lesson/ai00_01/a1-030.jpg')
    if level_list.index(level) == 2:
        img_pil = Image.open('./assets/lesson/ai00_01/a1-040.jpg')

    if level_list.index(level) >=0 and level_list.index(level) <=2:
        st.session_state['load_flg'] = True

    ## アップロードが選択されている場合...
    if level_list.index(level) == 3:

        # ファイルアップローダー
        uploaded_file = st.sidebar.file_uploader('ファイルをドラッグ＆ドロップしましょう', type=['png', 'jpeg', 'jpg'])

        if uploaded_file is not None:
            # 画像ファイルの読み込み
            img_pil = Image.open(uploaded_file)
            st.session_state['load_flg'] = True
        else:
            st.session_state['load_flg'] = False

    ## ファイルが読み込まれている場合の処理...
    if st.session_state['load_flg'] == True:

        # ボタンを押したら認識開始
        if st.sidebar.button('認識開始（ここをクリック）') == False:
            
            st.image(img_pil, caption='群衆の画像', use_column_width=True)  # 物体認識前の画像を表示
        else:
            # ファイルの横px、縦pxを取得
            img_w = img_pil.size[0]
            img_h = img_pil.size[1]

            if img_w > 3000 or img_h > 3000:
                pass
                st.warning('ファイルのサイズが大きすぎます（縦横ともに3000ピクセル以内の画像をご利用ください）')
            else:

                # 画像ファイルの読み込み
                # img_pil = Image.open("./temp/temp" + str(temp_no) + ".png")

                # PIL型 -> OpenCV型
                img_ocv = func_opencv.pil2cv(img_pil) 

                # ret, body = cv2.imencode('.bmp', img_ocv, [])

                img_bytes = io.BytesIO()
                img_pil.save(img_bytes, format='PNG')
                img_bytes = img_bytes.getvalue()  # これが bytes形式
                # Pillow Image を bytes に変換する方法
                # https://zenn.dev/tamanobi/articles/88dacd450f8405c9a5a9

                # スピナーを表示
                with st.spinner('認識中…'):

                    try:
                        # Custom Vision APIにデータをPOSTする
                        url="https://cheerycvproduct-prediction.cognitiveservices.azure.com/customvision/v3.0/Prediction/054ad3ac-572d-4b3a-b7f6-5738f9daae7b/detect/iterations/Iteration4/image"
                        headers={'content-type':'application/octet-stream','Prediction-Key':'3165ab7e182349d38aa423f2f4f1fdb9'}

                        response =requests.post(url, data=img_bytes, headers=headers)            
                        response.raise_for_status()
                        # Custom Vision APIをPythonから呼び出して、分類してみる - Qiita
                        # https://qiita.com/mine820/items/257da3d0f38f4c4e2625
                                    
                    # except:
                    except Exception as e:
                        print(f'エラー : {e}')
                        st.exception('エラーが発生しました。もう一度、最初からやり直してください。')
                        st.stop()   # 処理を中断

                ## APIからのレスポンス(JSON)を解析するループ...
                count_body = 0
                count_face = 0
                count_head = 0
                ret_dict = response.json()
                for ret in ret_dict['predictions']:

                    # print(ret['tagName'])
                    # line_color = (255, 255, 255)
                    # line_thick = 1

                    # タグ'Human'の処理
                    if ret['tagName'] == 'Body':
                        # 認識の信頼度が閾値を超えなかった場合...
                        if float(ret['probability']) < PROBABILITY_THRESHOLD_BODY:
                            break
                        count_body = count_body + 1
                        line_color = (0, 0, 255)

                    # タグ'Face'の処理
                    if ret['tagName'] == 'Face':
                        # 認識の信頼度が閾値を超えなかった場合...
                        if float(ret['probability']) < PROBABILITY_THRESHOLD_FACE:
                            break
                        count_face = count_face + 1
                        line_color = (0, 0, 255)

                    # タグ'Face'の処理
                    if ret['tagName'] == 'Head':
                        # 認識の信頼度が閾値を超えなかった場合...
                        if float(ret['probability']) < PROBABILITY_THRESHOLD_HEAD:
                            break
                        count_head = count_head + 1
                        line_color = (255, 255, 0)

                    # バウンディングボックスの座標を取得
                    bb = ret['boundingBox']
                    x1 = int(bb['left'] * img_w)
                    y1 = int(bb['top'] * img_h)
                    x2 = int((bb['left'] + bb['width']) * img_w)
                    y2 = int((bb['top'] + bb['height']) * img_h)
                    line_thick = 2

                    # 矩形を描画（BGR形式）
                    cv2.rectangle(img_ocv, (x1, y1), (x2, y2), color=line_color, lineType=cv2.LINE_4, thickness=line_thick)

                # OpenCV形式からPillow形式に戻して（BGRをRGBに変換）表示
                img_pil = img_ocv[:,:,::-1]
                st.image(img_pil, use_column_width = None)

                # バルーンの表示
                st.balloons()

                # st.success(f'AIが 写真の中から 【{str(count_face)}人の顔】【{str(count_head)}人の後頭部】【{str(count_human)}人の身体】を 認識しました', icon="✅")        
                st.success(f'AIが 写真の中から 【{str(count_body)}人】を 認識しました', icon="✅")        

