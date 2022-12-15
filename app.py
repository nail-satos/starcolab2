# 必要な標準ライブラリをインポートする
import streamlit as st
import streamlit.components.v1 as stc

from PIL import Image   # ロゴ画像の表示用
import time             # ダミーのsleep用
import json             # JSONファイル処理用
import sqlite3          # データベース用
import hashlib          # ハッシュ関数用

# 自作のモジュールをインポートする
from modules.generic import const     # 同一フォルダ内のconst
from modules.generic import func_html

# lessonファイルをインポートする
from modules.lesson import ai00_01_a1
from modules.lesson import ai00_01_a2
from modules.lesson import ai00_01_a3


### データベース関連（ここから） ####

# ハッシュ値を生成する関数
def make_hashes(psword):
	return hashlib.sha256(str.encode(psword)).hexdigest()


# ハッシュ値を検査する関数
def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False


# usersテーブルを作成する関数（IF NOT EXISTS : テーブルが存在しない場合）
# id：ユーザID
# psword: パス（ハッシュ値）
# name: ユーザの氏名
def create_table_users(csor):
    csor.execute('CREATE TABLE IF NOT EXISTS users(id TEXT, psword TEXT, name TEXT)')


# ユーザ情報を登録する関数
def add_user(conn, csor, id, psword, name):

    try:
        csor.execute('INSERT INTO users(id, psword, name) VALUES (?,?,?)',(id, psword, name))
        conn.commit()
        return True

    # except:
    except Exception as e:
        print(f'エラー : {e}')
        return False


# ユーザ情報を取得する関数
def check_user(csor, id, psword):

    data = []
    csor.execute('SELECT * FROM users WHERE id =? AND psword = ?',(id, psword))
    data = csor.fetchall()

    if len(data) == 0:
        ret_dict = {}
    else:
        ret_dict = { 'id': data[0][0], 'name': data[0][2] }
        print(ret_dict)

    return ret_dict


	# csor.execute('SELECT * FROM users WHERE id =? AND psword = ?',(id, psword))
	# data = csor.fetchall()
    # return data

    # if len(data) == 0:
    #     ret_dict = {}
    # else:
    #     ret_dict = { 'id': data[0], 'name': data[1] }



### データベース関連（ここまで） ####


### 各種フラグなどを初期化する関数（最初の1回だけ呼ばれる） ###
def init_parameters():

    ### 各種フラグなどを初期化するセクション ###
    if 'init_flg' not in st.session_state:

        st.session_state['init_flg'] = True         # 初期化(済)フラグをオンに設定
        st.session_state['lesson_no'] = -1          # レッスン番号フラグを初期化
        # st.session_state['portal_flg'] = False      # ポータルフラグをオフに設定
        st.session_state['login_flg'] = False       # ログインフラグをオフに設定
        st.session_state['add_act_flg'] = False     # ログインフラグをオフに設定
        # st.session_state['login_need'] = '必要' # ログインの要否をオンに設定
        st.session_state['trial_flg'] = True         # 体験版フラグをオンに設定

        st.session_state['user_id'] = ''        # ユーザID
        st.session_state['user_name'] = ''      # ユーザ名

        st.session_state['lesson_id'] = ''    # レッスンID　例.ai00_00
        st.session_state['activity_id'] = ''    # アクティビティID 例. a1
        st.session_state['activity_name'] = ''    # アクティビティ名 例. Pythonを動かそう
        st.session_state['activity_steps'] = 0    # アクティビティstep 例. 6
        st.session_state['activity_state'] = 'before'    # アクティビティstep 例. 6
        # st.session_state['lessons'] = []    # メニューのレッスン一覧
 


### 「はい」のコールバック -> アクティビティ画面を表示する
def call_login():
    # st.session_state['portal_flg'] = True
    st.session_state['login_flg'] = True

### 「いいえ」のコールバック -> （何もしなくてもウィジェットはクリアされる）
def clear_widgets():
    pass


### ポータル画面用の関数
def view_portal():

    # データベースの接続
    conn = sqlite3.connect('./database/manage.db')
    csor = conn.cursor()

    # usersテーブルの作成
    create_table_users(csor)


    ### サイドバーのレイアウト ###

    # ロゴ
    st.sidebar.image(Image.open('./assets/generic/image/logo_01.png'))

    # セレクトボックス
    menu = ['ログイン', 'ユーザー登録', 'AIを体験する']
    choice = st.sidebar.selectbox('メニュー', menu)

    if menu.index(choice) == 2:
        submenu = ['【選択してください】', '群衆の認識に挑戦だ！', 'AIで群衆を認識しよう', 'AIとおしゃべりしよう']
        subchoice = st.sidebar.selectbox('コンテンツ', submenu)

        # 「群衆の認識に挑戦だ！」の起動
        if submenu.index(subchoice) == 1:
            ai00_01_a1.view_lesson()

        # 「AIで群衆を認識しよう」の起動
        if submenu.index(subchoice) == 2:
            ai00_01_a2.view_lesson()

        # 「AIとおしゃべりしよう」の起動
        if submenu.index(subchoice) == 3:
            ai00_01_a2.view_lesson()


    ### 「ログイン」のレイアウト（ここから） ###
    if choice == "ログイン":

        # フォームのレイアウト
        with st.form('portal_form', clear_on_submit=True):

            # ヘッダ
            st.subheader('アクティビティ ポータル')                   

            userid = st.text_input("ユーザーID", disabled=False)
            psword = st.text_input("パスワード", type='password', disabled=False)
            # keyword = st.text_input(label='アクティビティのキーワード', value='e9g6')
            submitted = st.form_submit_button("ログイン")

        # プレースホルダの設定
        ph_111 = st.empty()
        col = st.columns([7, 1, 2])
        ph_211 = col[0].empty()
        ph_221 = col[1].empty()
        ph_222 = col[2].empty()

        # サブミットボタンが押された場合
        if submitted:

            # ダミースピナーを表示
            with st.spinner(const.MASSAGE_101):
                time.sleep(const.DELAY_TIME)

            # パスワードをハッシュ化
            hashed_pswd = make_hashes(psword)

            # ユーザの存在を検査する
            result = check_user(csor, userid, check_hashes(psword, hashed_pswd))
            print(result)

            if len(result) == 0:
                ph_111.warning("ユーザーID、またはパスワードが間違っています")
            else:
                ph_111.success("{} さんでログインしました".format(result['name']))

                # ユーザ情報をセッションステートに保存
                st.session_state['user_id'] = result['id']
                st.session_state['user_name'] = result['name']

                # データベースを切断
                conn.close()

                # アクティビティの確認メッセージ
                ph_211.write(const.MASSAGE_113)

                # 確認用のボタンを表示
                # ph_221.button(const.MASSAGE_121, on_click = call_login, args=(module_file_name, ))    # 引数付き
                ph_221.button(const.MASSAGE_121, on_click = call_login)     # はい
                ph_222.button(const.MASSAGE_122, on_click = clear_widgets)  # いいえ
                

    ### 「ログイン」のレイアウト（ここまで） ###


    ### 「ユーザー登録」のレイアウト（ここから） ###
    if choice == "ユーザー登録":

        with st.form('resist_form', clear_on_submit=True):
            st.subheader("ユーザー登録")
            new_id = st.text_input("ユーザーIDを入力してください（12文字以内で半角の英数字が使用できます）", placeholder='例. ai0000000')
            new_psword = st.text_input("パスワードを入力してください（32文字以内で半角の英数字が使用できます）", type='password')
            new_name = st.text_input("あなたの氏名を入力してください（全角でフルネームを入力しましょう）", placeholder='例. 星塾一郎')
            submitted = st.form_submit_button("ユーザー登録")

        if submitted:
            add_user(conn, csor, new_id, make_hashes(new_psword), new_name)
            st.success("ユーザー登録に成功しました。ユーザーIDとパスワードは忘れないようにしましょう")
            st.info("メニューから「ログイン」を選択して、作成したユーザーIDでログインしてください")

    ### 「新規登録」のレイアウト（ここまで） ###

# def init_activity(chapter_name, lesson_name, activity_name):
def init_lesson():

    print('いにっといにっと')
    st.session_state['lesson_id'] = ''    # レッスンID　例.ai00_00
    st.session_state['activity_id'] = ''    # アクティビティID 例. a1
    st.session_state['activity_name'] = ''    # アクティビティ名 例. Pythonを動かそう
    st.session_state['activity_steps'] = 0    # アクティビティstep 例. 6
    st.session_state['activity_state'] = 'before'    # アクティビティstep 例. 6


def init_activity():

    print('いにっと')
    st.session_state['activity_state'] = 'before'


### アクティビティ画面用の関数
def view_activity():
    
    # if st.sidebar.button('データ削除'):

    #     # データベースの接続（個人用）
    #     db_name = './database/' + st.session_state['user_id'] + '.db'
    #     conn = sqlite3.connect(db_name)
    #     csor = conn.cursor()

    #     # デバッグ用
    #     try:
    #         csor.execute('DROP TABLE activitys')
    #     except:
    #         pass

    #     # データベースを切断
    #     conn.close()


    # データベースの接続（個人用）
    db_name = './database/' + st.session_state['user_id'] + '.db'
    conn = sqlite3.connect(db_name)
    csor = conn.cursor()

    # 個人用データベースにactivitysテーブルを作成（初回のみ作成される）
    csor.execute('CREATE TABLE IF NOT EXISTS activitys(lesson_id TEXT, activity_id TEXT, step_id TEXT, passflg TEXT, code TEXT)')

    # activityテーブルを取得
    # csor.execute('SELECT DISTINCT(lesson_id) FROM activitys')
    datas = csor.execute('SELECT DISTINCT(lesson_id) FROM activitys ORDER BY lesson_id ASC').fetchall()    
    print(f'lesson_id = {datas}')


    # JSONファイルを辞書型で読み込む
    json_file = open('./datasets/generic/activitys.json', 'r', encoding="utf-8")
    json_dict = json.load(json_file)

    # 体験版フラグを確認
    if st.session_state['trial_flg'] == True:
        chapters = ['体験版',]
        lessons = ['AIの知的な機能を体験する','AIのプログラムを作るには',]

        ### サイドバーのレイアウト（体験版） ###
        with st.sidebar:
            # ロゴ
            st.image(Image.open('./assets/generic/image/logo_01.png'))
            chapter_name = st.sidebar.selectbox("メニューを選択してください",(chapters), on_change = init_lesson)
            lesson_name = st.sidebar.selectbox("レッスンを選択してください",(lessons), on_change = init_lesson)

            if lessons.index(lesson_name) == 0:
                activitys = ['【選択してください】', '群衆の認識に挑戦だ！', 'AIで群衆を認識しよう', 'AIとおしゃべりしよう']
            
            if lessons.index(lesson_name) == 1:
                activitys = ['【選択してください】', 'STAR ColabでPythonを動かそう', 'いろいろなエラーを体験しよう']


            activity_name = st.sidebar.selectbox("アクティビティを選択してください",(activitys), on_change = init_activity)

    else:
        ### 正式版のレイアウト ###

        # レッスン名の一覧
        chapters = ['追加登録',]
        lessons = ['【選択してください】']
        activitys = ['【選択してください】']

        # メニューの追加
        for data in datas:
            lesson_id = data[0]
            json_list = json_dict[lesson_id]
            chapters.append(json_list[0]['Chapter'])
            # lessons.append(json_list[0]['Lesson'])
            
            # for act in json_list[1:]:
            #     print(act['Activity'])

        ### サイドバーのレイアウト ###
        with st.sidebar:

            # ロゴ
            st.image(Image.open('./assets/generic/image/logo_01.png'))

            chapter_name = st.sidebar.selectbox("メニューを選択してください",(chapters), on_change = init_lesson)

            # メニューから認識編、予測編、言語編、進化編が選ばれた場合の処理
            if chapter_name != '追加登録':

                # JSONファイルを辞書型で読み込む
                json_file = open('./datasets/generic/activitys.json', 'r', encoding="utf-8")
                json_dict = json.load(json_file)

                # レッスンの追加
                for k,v in json_dict.items():
                    # データベースを見て、データがなければ、アペンドをスキップする処理も付ける
                    if v[0]['Chapter'] == chapter_name:
                        print('追加')
                        lessons.append(v[0]['Lesson'])

            lesson_name = st.sidebar.selectbox("レッスンを選択してください",(lessons), on_change = init_lesson)


            if len(lessons) != '【選択してください】':

                # JSONファイルを辞書型で読み込む
                json_file = open('./datasets/generic/activitys.json', 'r', encoding="utf-8")
                json_dict = json.load(json_file)

                # アクティビティの追加
                for k,v in json_dict.items():
                    if v[0]["Lesson"] == lesson_name:
                        for vv in v[1:]:
                            activitys.append(vv['Activity'])

            # activity_name = st.sidebar.selectbox("アクティビティを選択してください",(activitys), on_change = init_activity, args=(chapter_name, lesson_name, activity_name,))
            activity_name = st.sidebar.selectbox("アクティビティを選択してください",(activitys), on_change = init_activity)


    ### メインエリアのレイアウト ###

    # プレースホルダの設定
    ph_001 = st.empty()
    ph_101 = st.empty()
    ph_201 = st.empty()
    col = st.columns([8, 2])
    ph_211 = col[0].empty()
    ph_221 = col[1].empty()
    ph_301 = st.empty()
    ph_401 = st.empty()
    ph_501 = st.empty()


    if chapter_name == '追加登録':

        st.session_state['activity_steps'] = 0

        ph_001.header('Python 演習環境 "STAR Colab" へ ようこそ')

        # フォームのレイアウト
        form = ph_101.form('add_act_form', clear_on_submit=True)
        form.subheader('レッスンの追加登録')
        # keyword = form.text_input(label='アクティビティの手順書に書かれている「キーワード」を入力してください', value='e9g6')
        keyword = form.text_input(label='アクティビティの手順書に書かれている「キーワード」を入力してください', value='')
        submitted = form.form_submit_button("追加登録")

        # サブミットボタンが押された場合
        if submitted:
            # JSONファイルを辞書型で読み込む
            json_file = open('./datasets/generic/keyword.json', 'r', encoding="utf-8")
            json_dict = json.load(json_file)

            # ダミースピナーを表示
            with st.spinner(const.MASSAGE_101):
                time.sleep(const.DELAY_TIME)

            # 辞書キーの存在チェック
            if keyword in json_dict.keys():

                # レッスン番号（例. ai00_00)をJSONから取得
                lesson_id = json_dict[keyword]['Lesson_ID']

                # JSONファイルを辞書型で読み込む
                json_file = open('./datasets/generic/activitys.json', 'r', encoding="utf-8")
                json_dict = json.load(json_file)

                # 該当アクティビティの情報を取得
                lesson_dict = json_dict[lesson_id][0]
                activity_list = json_dict[lesson_id][1:]

                # print(lesson_dict)
                # print(activity_list)

                # lessonの確認メッセージ
                message = '「' + lesson_dict['Chapter'] + '」のレッスン『' + lesson_dict['Lesson'] + '』' + const.MASSAGE_111
                ph_211.write(message)

                # 確認用のボタンを表示
                # ph_221.button(const.MASSAGE_123, on_click = call_login)     # はい
                ph_221.button(const.MASSAGE_123)     # はい

                # lesson_idの存在確認（すでに追加済みであれば、再度追加してしまわないように）
                csor.execute('SELECT * FROM activitys WHERE lesson_id =?',(lesson_id, ))
                data = csor.fetchall()

                code = "print(100)"

                if len(data) == 0:

                    for act_dict in activity_list:
                        activity_id = act_dict['Activity_ID']   # アクティビティID（例. a1, a2）を取得
                        
                        # ステップの回数だけ繰り返す
                        for i in range(act_dict['Steps']):
                            # これ以前に、SELECTで存在検査をしているため、Try～は不要        
                            csor.execute('INSERT INTO activitys(lesson_id, activity_id, step_id, passflg, code) VALUES (?,?,?,?,?)',(lesson_id, activity_id, i+1, 'NG', code,))
                            conn.commit()

            else:
                message = 'キーワード「' + keyword + '」は存在しません。アクティビティの手順書を、確認してください。'
                ph_201.write(message)


    if lesson_name == 'AIの知的な機能を体験する':

        # 「群衆の認識に挑戦だ！」の起動
        if activitys.index(activity_name) == 1:
            ai00_01_a1.view_lesson()

        # 「AIで群衆を認識しよう」の起動
        if activitys.index(activity_name) == 2:
            ai00_01_a2.view_lesson()

        # 「AIとおしゃべりしよう」の起動
        if activitys.index(activity_name) == 3:
            ai00_01_a3.view_lesson()

        # 以降の処理を停止
        st.stop()

    # ### メニューからアクティビティを特定する処理 ###
    if chapter_name != '追加登録':

        # JSONファイルを辞書型で読み込む
        json_file = open('./datasets/generic/activitys.json', 'r', encoding="utf-8")
        json_dict = json.load(json_file)

        # アクティビティの特定
        for k,v in json_dict.items():
            if v[0]["Lesson"] == lesson_name:
                for vv in v[1:]:
                    if vv["Activity"] == activity_name:
                        # レッスンIDとアクティビティIDなどを格納
                        st.session_state['lesson_id'] = k
                        st.session_state['activity_id'] = vv['Activity_ID']
                        st.session_state['activity_name'] = vv['Activity']
                        st.session_state['activity_steps'] = vv['Steps']
                        # print('＃＃＃ アクティビティを初期化 ＃＃＃')



    ### アクティビティのメイン画面 ###
    # if lesson_name == 'AIのプログラムを作るには':
    if st.session_state['activity_steps'] >= 1:
        # print('＃＃＃ デバッグ用 ＃＃＃')
        # print(st.session_state['lesson_id'])
        # print(st.session_state['activity_id'])
        # print(st.session_state['activity_name'])
        # print(st.session_state['activity_steps'])

        # JSONファイルを辞書型で読み込む
        file_path = './datasets/lesson/' + st.session_state['lesson_id'] + '_' + st.session_state['activity_id'] + '.json'
        json_file = open(file_path, 'r', encoding="utf-8")
        json_dict = json.load(json_file)

        ### サイドバーのレイアウト（追加） ###
        with st.sidebar:
            step_list = []
            for i in range(st.session_state['activity_steps']):
                step_list.append('演習' + str(i+1))

            st.markdown('# STAR Colab')

            # 演習ステップ
            step_name = st.radio("演習を選択してください", step_list, horizontal=True, on_change = init_activity)
            step_dict = json_dict[step_name][0]

            # サブタイトルエリア
            st.caption('演習名')
            st.sidebar.info(step_dict['subtitle'])

            col = st.columns([4, 6])
            # col[0].caption('Click here ->')
            # ret_help_button = col[0].button('最初に戻す')
            ret_exec_button = col[1].button('プログラムの実行')


        txt_input = st.text_area('プログラミングエリア', value=step_dict['code'] ,max_chars=500, height=step_dict['height'])

        with st.expander("お手本のプログラムを見る"):
            st.code(step_dict['hint'])

        st.markdown('実行結果エリア')

        # 実行ボタン
        if ret_exec_button == False:
            st.warning('まだ実行されていません')

        else:
            #文字列の中身をプログラムとして実行
            txt_output = txt_input.replace('print', 'st.success')  # print文をst.infoに置換

            try:
                exec(txt_output)    # 実行
                st.session_state['activity_state'] = 'success'

            except Exception as e:

                print(f'エラー : {e}')
                st.error('Error !!')

                st.session_state['activity_state'] = 'error'

        # 吹き出し
        file_name = step_dict[st.session_state['activity_state']][0]['img']
        text = step_dict[st.session_state['activity_state']][0]['text']
        if text != '':
            text_html = func_html.make_html_balloon(file_name, func_html.trans_html_tag(text))
            stc.html(text_html, height=150)

        # 枠（説明）
        frame_head = step_dict[st.session_state['activity_state']][0]['head']
        frame_text = step_dict[st.session_state['activity_state']][0]['frame']
        frame_tail = step_dict[st.session_state['activity_state']][0]['tail']
        frame_size = step_dict[st.session_state['activity_state']][0]['size']
        if frame_text != '':
            ret = func_html.make_html_frame(frame_head, func_html.trans_html_tag(frame_text))
            stc.html(ret,height=frame_size)
            st.caption(frame_tail)

        # # インフォメーションエリア
        # st.sidebar.info(step_dict[st.session_state['activity_state']][0]['info'])

    # データベースを切断
    conn.close()
            

def main():

    ### 各種フラグなどを初期化する関数をコール ###
    init_parameters()

    # タブに表示されるページ名の変更
    st.set_page_config(page_title="アクティビティ ポータル", initial_sidebar_state="expanded")

    ### デバッグ用にフラグ類を改変 ###
    # st.session_state['portal_flg'] = True
    # st.session_state['login_flg'] = True
    # st.session_state['user_id'] = 'ai00'
    # st.session_state['user_name'] = '星塾万次丸'

    # st.session_state['lesson_id'] = 'ai00_01'
    # st.session_state['activity_id'] = 'a1'
    # st.session_state['activity_name'] = ''
    # st.session_state['activity_steps'] = 6
    # st.session_state['activity_state'] = 'before'

    # st.session_state['lesson_id'] = 'ai00_02'
    # st.session_state['activity_id'] = 'a1'
    # st.session_state['activity_name'] = 'STAR ColabでPythonを動かそう'
    # st.session_state['activity_steps'] = 6
    # st.session_state['activity_state'] = 'before'

    # st.session_state['lesson_id'] = 'ai00_02'
    # st.session_state['activity_id'] = 'a2'
    # st.session_state['activity_name'] = 'いろいろなエラーを体験しよう'
    # st.session_state['activity_steps'] = 5
    # st.session_state['activity_state'] = 'before'

    # 体験版フラグを確認
    if st.session_state['trial_flg'] == True:
            view_activity()
    else:
        # ポータル画面の表示
        if st.session_state['login_flg'] == False:
            view_portal()

        # アクティビティ画面の表示
        if st.session_state['login_flg'] == True:
            view_activity()



# デプロイ時に必要になるmain関数
if __name__ == "__main__":
    main()
