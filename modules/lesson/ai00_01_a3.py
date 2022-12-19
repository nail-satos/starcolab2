### 必要な標準ライブラリをインポートする
import requests         # APIコール用
import json             # APIからの戻り値の処理用
import time             # ダミーのsleep用

### 必要な外部ライブラリをインポートする
import streamlit as st
import streamlit.components.v1 as stc
import numpy as np
import pandas as pd

### 自作のモジュールをインポートする
from modules.generic import func_html
from modules.generic import const     # 同一フォルダ内のconst

### 定数の設定
DELAY_TIME = 1.5

# meboAPIにユーザーが入力した文字列をpost
def post_mebo(message):
    url = "https://api-mebo.dev/api"
    headers = {
        # Already added when you pass json=
        # 'Content-Type': 'application/json',
    }
    payload = {
        "api_key": "c0dbf4fb-daa8-4f39-b46d-67eb830aa66c1839d878c4219f",
        "agent_id": "199a5291-0406-49bf-bf73-e1755835153d1839ceb44d6357",
        "utterance": message,
        }
    r = requests.post(url,headers=headers,json=payload)
    content = r.text
    content = json.loads(content)
    best_responce = content['bestResponse']
    print(best_responce['utterance'])
    return best_responce['utterance']


def view_single():

    # タイトル
    st.header('AIとおしゃべりしよう')

    # メッセージを入力するテキストエリア
    you_message= st.text_area(label='メッセージを入力して「送信」ボタンを押してください')
    st.caption('例）元気ですか　おはなししよう　昨日は何を食べた？　どんなゲームが好き？　など自由に入力してください')

    col = st.columns([9, 1])
    send_button = col[1].button('送信')

    # プレースホルダを作成
    placeholder_main = st.empty()

    # ボタンを押したら、post_mebo関数が呼び出される
    if send_button:

        # プレースホルダにスピナーを出力
        with st.spinner('考え中…'):
            ai_message = post_mebo(message=you_message)
            time.sleep(DELAY_TIME)    # ダミーのスリープ

        # プレースホルダに出力
        with placeholder_main.container():
            # st.write('')
            # st.write('～ AIからの応答 ～')
            st.info('AIからのメッセージ')
            text_html = func_html.make_html_balloon('ai101.png', func_html.trans_html_tag(ai_message), 'lavender')
            stc.html(text_html, height=150)


def view_double():

    # セッションステートを初期化する
    if 'chat_log' not in st.session_state:
        st.session_state['chat_list'] = []

    # タイトル
    st.header('AI同士でおしゃべりする')

    # メッセージを入力するテキストエリア
    chat_theme = st.text_input(label='おしゃべりの「テーマ」を設定してください', placeholder='例）休日の過ごし方　今日の晩ごはん　好きな音楽　得意な科目 など自由に入力してください')
    # st.caption('例）休日の過ごし方　今日の晩ごはん　将来の夢　好きな音楽　など自由に入力してください')

    chat_times = st.slider('会話を繰り返す「回数」を設定してください', min_value=2, max_value=10, value=6)

    col = st.columns([9, 1])
    send_button = col[1].button('開始')

    # プレースホルダを作成
    placeholder_top = st.empty()
    placeholder_butom = st.empty()

    # ボタンを押したら、post_mebo関数が呼び出される
    if send_button:

        # スピナーを出力
        with st.spinner('考え中…'):
            time.sleep(DELAY_TIME)    # ダミーのスリープ

            ai_message = post_mebo(message=chat_theme)  # 1回目だけテーマを元に会話を開始する

        for i in range(chat_times):

            # # スピナーを出力
            # with st.spinner('考え中…'):
            #     ai_message = post_mebo(message=chat_theme)
            #     time.sleep(const.DELAY_TIME)    # ダミーのスリープ

            # プレースホルダに出力
            with placeholder_top.container():

                if i % 2 == 0:
                    st.warning(f'AI 1号（会話 {i+1}/{chat_times}回）')
                    text_html = func_html.make_html_balloon('ai102.png', func_html.trans_html_tag(ai_message), 'lavender')
                    st.session_state['chat_list'].append(['AI 1号', ai_message])

                if i % 2 == 1:
                    st.info(f'AI 2号（会話 {i+1}/{chat_times}回）')
                    text_html = func_html.make_html_balloon('ai103.png', func_html.trans_html_tag(ai_message), 'azure')
                    st.session_state['chat_list'].append(['AI 2号', ai_message])

                stc.html(text_html, height=150)

                # 最後のチャットか否かを判断する                
                if i == (chat_times-1):
                    st.success('設定した回数の会話が完了しました。会話の記録は以下の通りです。')
                    log_list = st.session_state['chat_list']
                    df_log = pd.DataFrame(log_list)
                    df_log.columns = ['話者', '会話']
                    df_log.index = np.arange(1, len(df_log)+1)
                    st.dataframe(df_log)

                else:

                    # スピナーを出力
                    with st.spinner('考え中…'):
                        time.sleep(DELAY_TIME)    # ダミーのスリープ

                        # ai_message = ai_message + '。さて、人工知能は？'
                        ai_message = post_mebo(message=ai_message)  # 2回目以降は相手の会話を元に会話する


            # placeholder_butom.empty()

            # # プレースホルダに出力
            # with placeholder_butom.container():

            #     # スピナーを出力
            #     with st.spinner('考え中…'):
            #         time.sleep(const.DELAY_TIME)    # ダミーのスリープ
            #         ai_message = post_mebo(message=ai_message)

            #     # st.info('AIからのメッセージ')
            #     text_html = func_html.make_html_balloon('ai103.png', func_html.trans_html_tag(ai_message), 'azure')
            #     stc.html(text_html, height=150)

    

            # st.info('AIからのメッセージ')
            # text_html = func_html.make_html_balloon('ai103.png', func_html.trans_html_tag(ai_message), 'lavender')
            # stc.html(text_html, height=150)
            # time.sleep(const.DELAY_TIME)    # ダミーのスリープ


def view_lesson():
    
    option_check = st.sidebar.checkbox('AI同士でおしゃべりするモード')
    if option_check == False:
        view_single()
    else:
        view_double()



# 会話のラリーができるAIのAPIを公開した話【個人開発】 - Qiita
# https://qiita.com/maKunugi/items/14f1b82a2c0b6fa5c202