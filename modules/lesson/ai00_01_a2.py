# 必要なライブラリをインポートする
import streamlit as st
# import cv2
from PIL import Image
import time

def view_lesson():

    st.header('アプリ「AIで群衆を認識しよう」')           # タイトル

    st.sidebar.subheader('難易度を選んで「認識開始」ボタンを押してください')       # サブヘッダ

    # level = st.radio("難易度を選択してください", ("初級の画像", "中級の画像", "上級の画像"), horizontal=True)
    level = st.sidebar.radio("難易度を選択してください",("初級", "中級", "上級"), horizontal=True)

    # st.write('レッスン1')         # キャプション
    if level == '初級':
        image = Image.open('./assets/lesson/ai00_01/a1-010.jpg')
    if level == '中級':
        image = Image.open('./assets/lesson/ai00_01/a1-030.jpg')
    if level == '上級':
        image = Image.open('./assets/lesson/ai00_01/a1-040.jpg')


    if st.sidebar.button('認識開始（ここをクリック）'):

        if level == '初級':
            image = Image.open('./assets/lesson/ai00_01/a1-011.jpg')
            count = 12
        if level == '中級':
            image = Image.open('./assets/lesson/ai00_01/a1-031.jpg')
            count = 65
        if level == '上級':
            image = Image.open('./assets/lesson/ai00_01/a1-041.jpg')
            count = 321

        status_text = st.empty()
        # プログレスバー
        progress_bar = st.progress(0)

        i = 0
        while i < 100:
            # status_text.text(f'Progress: {i}%')
            # for ループ内でプログレスバーの状態を更新する
            i = i + 5
            progress_bar.progress(i)
            time.sleep(0.1)
        
        # バルーンの表示
        st.balloons()

        st.success('AIが 写真の中から 【' + str(count) + '人】の人間を 認識しました', icon="✅")        


    # 画像の表示
    st.image(image, caption='群衆の画像', use_column_width=True)
