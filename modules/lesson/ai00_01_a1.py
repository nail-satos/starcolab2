# 必要なライブラリをインポートする
import streamlit as st

from PIL import Image
import time

def view_lesson():

    st.header('アプリ「群衆の認識に挑戦だ！」')           # タイトル

    st.sidebar.subheader('難易度を選んで「スタート」ボタンを押してください')       # サブヘッダ
    st.write('制限時間内に 写真の中に何人の人がいるかを数えよう！')         # キャプション

    # level = st.radio("難易度を選択してください", ("初級の画像", "中級の画像", "上級の画像"), horizontal=True)
    level = st.sidebar.radio("難易度を選択してください",("初級", "中級", "上級"), horizontal=True)

    image = Image.open('./assets/lesson/ai00_01/a1-001.jpg')

    start_flg = False

    if st.sidebar.button('スタート（ここをクリック）'):

        if level == '初級':
            image = Image.open('./assets/lesson/ai00_01/a1-010.jpg')
        if level == '中級':
            image = Image.open('./assets/lesson/ai00_01/a1-030.jpg')
        if level == '上級':
            image = Image.open('./assets/lesson/ai00_01/a1-040.jpg')

        # 画像の表示
        st.image(image, caption='群衆の画像', use_column_width=True)

        status_text = st.empty()
        # プログレスバー
        progress_bar = st.progress(0)

        i = 0
        while i < 100:
            # status_text.text(f'Progress: {i}%')
            # for ループ内でプログレスバーの状態を更新する
            i = i + 1
            progress_bar.progress(i)
            time.sleep(0.1)
        
        # バルーンの表示
        st.balloons()

        if level == '初級':
            st.success('制限時間内に数えられましたか？　画像に写っていたのは12人でした', icon="✅")        
        if level == '中級':
            st.success('ちょっと難しかったでしょうか？　正解は後ほどAIで確認しましょう', icon="✅")        
        if level == '上級':
            st.success('すごい人数でさすがに無理ですね。正解は後からAIで確認してみよう', icon="✅")        
            