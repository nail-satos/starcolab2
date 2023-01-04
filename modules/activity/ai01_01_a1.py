### 必要な標準ライブラリをインポートする
from PIL import Image       # 画像表示
from PIL import ImageDraw   # 図形描画
import requests             # Custom Vison APIコール
import io                   # 画像データのバイナリ変換
import random               # 乱数発生
import time                 # ダミースリープ

### 必要な外部ライブラリをインポートする
import streamlit as st
import numpy as np

# ### 自作のモジュールをインポートする ###
# from modules.generic import func_opencv

### 定数の設定 ###
DELAY_TIME = 2.0 


def view_activity(step_dict, status_dict):

    # レッスンに使用する画像のPATHを生成
    image_file_path = './assets/lesson/' + st.session_state['lesson_id'] + '/'

    # 背景画像
    base_file  = image_file_path + 'background01.png'
    img_pil_base  = Image.open(base_file)

    # 演習3
    if int(step_dict['step']) == 3:

        # 重ねる透過画像
        layer_path = image_file_path + 'taishi.png'
        img_pil_layer = Image.open(layer_path)

        # キャラクター画像の拡大
        scale = 2.0
        w, h  = img_pil_layer.size
        img_pil_layer = img_pil_layer.resize((int(w * scale), int(h * scale))) 

        # 画像の重ね合わせ
        img_pil_base.paste(img_pil_layer, (400, 300), img_pil_layer)
        # img_pil_base.save(out_path)

        # 生成した画像の描画
        st.image(img_pil_base, use_column_width = None)


    # 演習4
    if int(step_dict['step']) == 4:


        characters = ['taishi.png', 'benkei.png', 'eiichi.png', 'hideyoshi.png', 'himiko.png', 'ieyasu.png', 'kenshin.png', 'masamune.png', 'nobunaga.png', 'rikyu.png', 'ryouma.png', 'shingen.png', 'souseki.png', 'takamori.png', 'yukichi.png']

        max_count = 100
        for i in range(max_count+1):

            if i == max_count:
                # 重ねる透過画像（ターゲット）
                rnd  = 0
            else:
                # 重ねる透過画像（ランダム）
                rnd  = random.randint(1, 14)

            layer_path = image_file_path + characters[rnd]
            img_pil_layer = Image.open(layer_path)

            # キャラクター画像の拡大
            scale = 1.0
            w, h  = img_pil_layer.size
            img_pil_layer = img_pil_layer.resize((int(w * scale), int(h * scale))) 

            # 画像の重ね合わせ
            rndx = random.randint(0, 780)  # x座標のmaxは800
            rndy = random.randint(0, 520)  # y座標のmaxは540
            img_pil_base.paste(img_pil_layer, (rndx, rndy), img_pil_layer)

            # ターゲットの位置をセッションステートに保存
            if i == max_count:
                st.session_state['target_x'] = rndx
                st.session_state['target_y'] = rndy
                st.session_state['target_w'] = int(w * scale)
                st.session_state['target_h'] = int(h * scale)

        print(st.session_state['target_x'])

        # 生成した画像の描画
        st.image(img_pil_base, use_column_width = None)

        # 生成した画像をセッションステートに保存
        st.session_state['img_pil_base'] = img_pil_base

        col = st.columns([2,8])
        col[0].button('画像の再作成')
        col[1].write('左のボタンをクリックすると、キャラクターの配置が違う画像を作成します')


    # 演習5
    if int(step_dict['step']) == 5:

        # # ダミースピナーを表示
        # with st.spinner('処理中...'):
        #     time.sleep(DELAY_TIME)

        # 生成した画像をセッションステートから復元
        img_pil_base = st.session_state['img_pil_base']
        x = st.session_state['target_x']
        y = st.session_state['target_y']
        w = st.session_state['target_w']
        h = st.session_state['target_h']


        draw = ImageDraw.Draw(img_pil_base)
        draw.rectangle((x-10, y-10, x+w+10,  y+h+10), fill=None, outline=(255, 0, 0), width=7)

        # 前の手順で保存した画像の描画
        st.image(img_pil_base, use_column_width = None)

