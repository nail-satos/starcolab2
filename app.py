### 必要な標準ライブラリをインポートする ###
import streamlit as st                  # Streamlit
import streamlit.components.v1 as stc   # htmlの表示

from PIL import Image   # ロゴ画像の表示
import time             # ダミースリープ
import json             # JSONファイル処理
import sqlite3          # データベース
import hashlib          # ハッシュ関数
import copy             # ディープコピー

### 自作のモジュールをインポートする ###
from modules.generic import func_html
from modules.generic import func_message
from modules.generic import func_recheck

### lessonファイルをインポートする ###
from modules.activity import ai00_01_a1
from modules.activity import ai00_01_a2
from modules.activity import ai00_01_a3

### 定数の設定 ###
DELAY_TIME = 0.5 


# 各種フラグなどを初期化する関数（最初の1回だけ呼ばれる）
def init_parameters():

    ### 各種フラグなどを初期化するセクション ###
    if 'init_flg' not in st.session_state:

        st.session_state['init_flg'] = True             # 初期化(済)フラグをオンに設定
        
        st.session_state['lesson_no'] = -1              # レッスン番号フラグを初期化
        st.session_state['login_flg'] = False           # ログインフラグをオフに設定
        st.session_state['trial_flg'] = False           # 体験版フラグをオフに設定
        st.session_state['trial_flg'] = True            # 体験版フラグをオンに設定

        st.session_state['user_id'] = ''                # ログイン済みユーザID
        st.session_state['user_name'] = ''              # ログイン済みユーザ氏名

        # datasets\generic\titles.jsonから取得する情報
        st.session_state['lesson_id'] = ''              # レッスンID　例.ai00_00
        st.session_state['activity_id'] = ''            # アクティビティID 例. a1
        st.session_state['activity_name'] = ''          # アクティビティ名 例. Pythonを動かそう
        st.session_state['activity_steps'] = 0          # アクティビティの総step数 例. 6

        st.session_state['activity_state'] = 'before'   # アクティビティの状態(before → success or error)


### データベース関連の関数群 ####

# ハッシュ値を生成する関数（Passのハッシュ化）
def make_hashes(psword):
	return hashlib.sha256(str.encode(psword)).hexdigest()


# ハッシュ値を検査する関数（Passのハッシュ化）
def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False



###************************************************************************###
# 管理用/個人用データベース（manage.db）共通の関数群 ###
###************************************************************************###

# 管理用データベース（manage.db）に接続する関数
def connect_db(filename):
    # データベースの接続
    conn = sqlite3.connect(filename)
    csor = conn.cursor()

    return conn, csor


###************************************************************************###
# 管理用データベース（manage.db）に関する関数群 ###
###************************************************************************###

# usersテーブルを作成する関数（IF NOT EXISTS : テーブルが存在しない場合）
def create_table_users(csor):
    """
    id     : ユーザID
    psword : パス（ハッシュ値）
    name   : ユーザの氏名
    """
    csor.execute('CREATE TABLE IF NOT EXISTS users(id TEXT, psword TEXT, name TEXT)')


# def check_regist_user():
#     pass


# ユーザ情報をテーブルに登録する関数
# 同じユーザがいた場合はエラーにする（未作成）
def add_user(conn, csor, id, psword, name):

    data = []
    # タプル()で渡す値が1つのときは , を付けないとエラーになる
    csor.execute('SELECT * FROM users WHERE id =?',(id,))   
    data = csor.fetchall()
    
    try:

        if len(data) == 0:
            csor.execute('INSERT INTO users(id, psword, name) VALUES (?,?,?)',(id, psword, name))
            conn.commit()
            return True, '正常終了'
        else:
            return False, 'すでに使われているユーザー名です'

    # except:
    except Exception as e:
        print(f'エラー : {e}')
        return False, 'データベースに予期せぬエラーが発生しました'


# 指定したユーザ情報が存在するかを確認する関数（存在する場合は、ユーザ名と氏名を取得）
def exists_user(csor, id, psword):

    data = []
    csor.execute('SELECT * FROM users WHERE id =? AND psword = ?',(id, psword))
    data = csor.fetchall()

    if len(data) == 0:
        ret_dict = {}
    else:
        ret_dict = { 'id': data[0][0], 'name': data[0][2] }

    return ret_dict


###************************************************************************###
# 個人用データベース（全角ニックネーム.db）に関する関数群 ###
###************************************************************************###

# 個人用のactivitysテーブルを作成する関数（IF NOT EXISTS : テーブルが存在しない場合）
def create_table_activitys(csor):

    # 個人用データベースにactivitysテーブルを作成（初回のみ作成される）
    csor.execute('CREATE TABLE IF NOT EXISTS activitys(lesson_id TEXT, activity_id TEXT, step_id TEXT, passflg TEXT, code TEXT)')


# 個人用のactivityテーブルに lesson_id, activity_id, step_id, passflg, code をステップの行数だけ追加する関数
def add_user_activitys(conn, csor, lesson_id, lesson_activity_list):

    # lesson_idの存在確認（すでに追加済みであれば、再度追加してしまわないように）
    csor.execute('SELECT * FROM activitys WHERE lesson_id =?',(lesson_id, ))
    data = csor.fetchall()

    if len(data) == 0:

        for act_dict in lesson_activity_list:
            activity_id = act_dict['Activity_ID']   # アクティビティID（例. a1, a2）を取得
            
            # ステップの回数だけ行の挿入を繰り返す
            for i in range(act_dict['Steps']):
                # これ以前に、SELECTで存在検査をしているため、Try～は不要        
                csor.execute('INSERT INTO activitys(lesson_id, activity_id, step_id, passflg, code) VALUES (?,?,?,?,?)',(lesson_id, activity_id, i+1, 'INIT', 'no code',))
                conn.commit()


# 個人用のactivityテーブルから（解放されている）レッスンIDを取得する関数
def get_user_lessons(csor):

    datas = csor.execute('SELECT DISTINCT(lesson_id) FROM activitys ORDER BY lesson_id ASC').fetchall()    
    return datas


# 個人用のactivityテーブルから（合格している）ステップID（の最大値）を取得する関数
def get_pass_activity_step(csor, lesson_id, activity_id):

    datas = csor.execute('SELECT max(step_id) FROM activitys WHERE lesson_id=? AND activity_id=? AND passflg = "OK"',(lesson_id, activity_id)).fetchall()    
    return datas


# 個人用のactivityテーブルからcodeを取得する関数（passflgがINIT以外）
def get_activity_code(csor, lesson_id, activity_id, step_id):

    datas = csor.execute('SELECT code FROM activitys WHERE lesson_id=? AND activity_id=? AND step_id=? AND passflg <> "INIT"',(lesson_id, activity_id, step_id)).fetchall()    
    return datas


# 個人用のactivityテーブルのpassflgを設定する関数（passflgがOK以外）
def set_activity_passflg(conn, csor, lesson_id, activity_id, step_id, value):

    try:
        csor.execute('UPDATE activitys SET passflg=? WHERE lesson_id=? AND activity_id=? AND step_id=? AND passflg <> "OK"',(value, lesson_id, activity_id, step_id))
        conn.commit() 

    # except:
    except Exception as e:
        print(f'エラー : {e}')
        return False, 'データベースに予期せぬエラーが発生しました'


# 個人用のactivityテーブルのcodeを設定する関数
def set_activity_code(conn, csor, lesson_id, activity_id, step_id, value):

    try:
        csor.execute('UPDATE activitys SET code=? WHERE lesson_id=? AND activity_id=? AND step_id=?',(value, lesson_id, activity_id, step_id))
        conn.commit() 

    # except:
    except Exception as e:
        print(f'エラー : {e}')
        return False, 'データベースに予期せぬエラーが発生しました'


###************************************************************************###
# コールバックに関する関数群 ###
###************************************************************************###

# 'STAR Colab に移動しますか？' → 「はい」のコールバック
def call_login():
    st.session_state['login_flg'] = True

# 'STAR Colab に移動しますか？' → 「いいえ」のコールバック
def clear_widgets():
    pass


# レッスン用のセッションステートを初期化する関数
def init_lesson():

    st.session_state['lesson_id'] = ''              # レッスンID　例.ai00_00
    st.session_state['activity_id'] = ''            # アクティビティID 例. a1
    st.session_state['activity_name'] = ''          # アクティビティ名 例. Pythonを動かそう
    st.session_state['activity_steps'] = 0          # アクティビティの総step数 例. 6
    st.session_state['activity_state'] = 'before'   # アクティビティの状態（before、success、error）


# アクティビティの状態を初期化する関数（メニューが変更された場合など）　※未使用
def init_activity():

    # アクティビティの状態を初期状態に戻す
    st.session_state['activity_state'] = 'before'


###************************************************************************###
# ポータル画面用の関数
###************************************************************************###
def view_portal():

    # データベース接続用の関数を呼び出し
    conn, csor = connect_db('./database/manage.db')

    # usersテーブルの作成（最初の一回だけ実行される）
    create_table_users(csor)

    ## サイドバーのレイアウト ##

    # ロゴマーク
    st.sidebar.image(Image.open('./assets/generic/image/logo_01.png'))

    # セレクトボックス（メインメニュー）
    menu = ['ログイン', 'ユーザー登録', 'AIを体験する']
    choice = st.sidebar.selectbox('メニュー', menu)

    # 「AIを体験する」のサブメニュー
    if menu.index(choice) == 2:

        submenu = ['【選択してください】', '群衆の認識に挑戦だ！', 'AIで群衆を認識しよう', 'AIとおしゃべりしよう']
        subchoice = st.sidebar.selectbox('コンテンツ', submenu)

        # 「群衆の認識に挑戦だ！」の起動
        if submenu.index(subchoice) == 1:
            ai00_01_a1.view_activity()

        # 「AIで群衆を認識しよう」の起動
        if submenu.index(subchoice) == 2:
            ai00_01_a2.view_activity()

        # 「AIとおしゃべりしよう」の起動
        if submenu.index(subchoice) == 3:
            ai00_01_a3.view_activity()


    ###************************************************************************###
    ## 「ログイン」画面のレイアウト ##
    ###************************************************************************###
    if menu.index(choice) == 0:

        # プレースホルダの設定
        layout_10 = st.empty()      # フォームを配置
        layout_20 = st.empty()      # メッセージを配置
        col = st.columns([7, 1, 2]) # カラムを作成
        layout_31 = col[0].empty()  # メッセージを配置 
        layout_32 = col[1].empty()  # 「はい」ボタンを配置
        layout_33 = col[2].empty()  # 「いいえ」ボタンを配置


        # フォームのレイアウト
        with layout_10.form('portal_form', clear_on_submit=True):

            st.subheader('スタ塾 AI活用編 アクティビティポータル')                   

            userid = st.text_input("ユーザー名（ニックネーム）", disabled=False)
            psword = st.text_input("パスワード", type='password', disabled=False)
            submitted = st.form_submit_button("ログイン")

        # フォームのサブミット（ログインボタン）が押された場合
        if submitted:

            # ダミースピナーを表示
            with st.spinner('処理中...'):
                time.sleep(DELAY_TIME)

            # パスワードをハッシュ化
            hashed_pswd = make_hashes(psword)

            # ユーザの存在を検査する
            result = exists_user(csor, userid, check_hashes(psword, hashed_pswd))

            if len(result) == 0:
                layout_20.warning("ユーザー名、またはパスワードが間違っています")
            else:
                layout_20.success("{} さんでログインしました".format(result['name']))

                # ユーザ情報をセッションステートに保存
                st.session_state['user_id'] = result['id']
                st.session_state['user_name'] = result['name']

                # データベースを切断（manage.db）
                conn.close()

                # アクティビティの確認メッセージ
                layout_31.write('STAR Colab に移動しますか？')

                # 確認用のボタンを表示
                layout_32.button('はい'  , on_click = call_login)     # はい
                layout_33.button('いいえ', on_click = clear_widgets)  # いいえ


    ###************************************************************************###
    ## 「ユーザー登録」画面のレイアウト ##
    ###************************************************************************###
    if choice == "ユーザー登録":

        with st.form('resist_form', clear_on_submit=False):
            st.subheader("ユーザー登録")
            keyword = st.text_input(label='アクティビティの手順書に書かれているユーザー登録用の「キーワード」を入力してください', value='aistar')
            new_id = st.text_input("希望のユーザー名を入力してください（全角10文字以内でニックネームを入力しましょう）", placeholder='例. エーアイスター')
            new_psword = st.text_input("パスワードを入力してください（24文字以内で半角の英数字が使用できます）", type='password')
            new_name = st.text_input("あなたの氏名を入力してください（全角10文字以内でフルネームを入力しましょう）", placeholder='例. 星塾一郎')
            submitted = st.form_submit_button("ユーザー登録")

        if submitted:

            error_text = ''

            # 入力された内容のチェック
            if keyword != 'aistar':
                error_text = error_text + 'キーワードが違います。アクティビティの手順書を確認してください\n\n'

            if len(new_id) == 0 or len(new_id) > 10 or func_recheck.isFull(new_id) == False:
                error_text = error_text + 'ユーザー名（ニックネーム）は全角10文字以内で入力してください\n\n'

            if len(new_psword) == 0 or len(new_psword) > 24 or func_recheck.isalnum_ascii(new_psword) == False:
                error_text = error_text + 'パスワードは半角の英数字24文字以内で入力してください\n\n'

            if len(new_name) == 0 or len(new_name) > 10 or func_recheck.isFull(new_name) == False:
                error_text = error_text + '氏名（フルネーム）は全角10文字以内で入力してください\n\n'

            if len(error_text) >= 1:
                st.warning(error_text)
                st.info("入力した内容を確認してください")
            else:
                # ユーザ登録の関数を呼び出す
                ret_code, ret_text = add_user(conn, csor, new_id, make_hashes(new_psword), new_name)

                if ret_code == True:
                    st.success("ユーザー登録に成功しました。ユーザー名とパスワードは忘れないようにしましょう")
                    st.info("メニューから「ログイン」を選択して、作成したユーザー名でログインしてください")
                else:
                    st.warning(ret_text)
                    st.info("ユーザー名とパスワードを確認してください")


###************************************************************************###
## アクティビティ画面用の関数
###************************************************************************###
def view_activity():
    
    # activitys.jsonファイルを辞書型で読み込む
    json_file = open('./datasets/generic/titles.json', 'r', encoding="utf-8")
    title_dict = json.load(json_file)

    # keyword.jsonファイルを辞書型で読み込む
    json_file = open('./datasets/generic/keyword.json', 'r', encoding="utf-8")
    keyword_dict = json.load(json_file)

    if st.session_state['trial_flg'] == True:

        ###************************************************************************###
        ### 体験版の前処理 ###
        ###************************************************************************###

        ## サイドバーのレイアウト ##
        chapters = ['体験版',]
        lessons = ['【選択してください】', 'AIの知的な機能を体験する', 'AIのプログラムを作るには', '自由にPythonを記述しよう' ]

        st.sidebar.image(Image.open('./assets/generic/image/logo_01.png'))
        chapter_name = st.sidebar.selectbox("メニューを選択してください",(chapters), on_change = init_lesson)
        lesson_name = st.sidebar.selectbox("レッスンを選択してください",(lessons), on_change = init_lesson)

        if lessons.index(lesson_name) != 0: # レッスンが無選択のときはアクティビティ選択は非表示にする

            if lessons.index(lesson_name) == 1:
                activitys = ['【選択してください】', '群衆の認識に挑戦だ！', 'AIで群衆を認識しよう', 'AIとおしゃべりしよう']
            
            if lessons.index(lesson_name) == 2:
                activitys = ['【選択してください】', 'STAR ColabでPythonを動かそう', 'いろいろなエラーを体験しよう']

            if lessons.index(lesson_name) == 3:
                activitys = ['【選択してください】', 'Pythonプログラミング練習場']

            activity_name = st.sidebar.selectbox("アクティビティを選択してください",(activitys), on_change = init_lesson)

        # データベースの接続（キャラバン用db）
        db_name = './database/trial.db'
        conn, csor = connect_db(db_name)

    else:
        ###************************************************************************###
        ### 正式版の前処理 ###
        ###************************************************************************###

        # データベースの接続（個人用db）
        db_name = './database/' + st.session_state['user_id'] + '.db'
        conn, csor = connect_db(db_name)

        # 個人用データベースにactivitysテーブルを作成（初回のみ作成される）
        create_table_activitys(csor)

        # activityテーブルからレッスンIDを取得
        datas = get_user_lessons(csor)

        # リスト内の(タプル)からリストに変換するループ
        # 例. datas = [('ai00_02',), ('ai01_01',)]
        # 例. user_lesson_ids = ['ai00_02', 'ai01_01']
        user_lesson_ids = []
        for data in datas:
            user_lesson_ids.append(data[0])

        # メニューの設定
        chapters = ['追加登録',]               # メニュー
        lessons = ['【選択してください】']      # レッスン
        activitys = ['【選択してください】']    # アクティビティ

        # 解放済みのレッスンIDからチャプター名（例：'準備編', '認識編'）を取得するループ
        for lesson_id in user_lesson_ids:
            # lesson_id = data[0]     # 例：'ai00_02'、'ai01_01'
            chapters_list = title_dict[lesson_id]   # レッスンIDをキーにJSONからチャプター・レッスン・アクティビティの一覧を取得
            chapters.append(chapters_list[0]['Chapter'])    # 一覧から、チャプター名（例：'準備編', '認識編'）を取得

        ## サイドバーのレイアウト ##
        st.sidebar.image(Image.open('./assets/generic/image/logo_01.png'))

        # 「メニュー（チャプター）」の選択
        chapter_name = st.sidebar.selectbox("メニューを選択してください",(chapters), on_change = init_lesson)

        # チャプターから「追加登録」以外が選ばれた場合の処理
        if chapters.index(chapter_name) != 0:

            # activitys.jsonを参照してメニューにレッスンを追加する
            for key,value in title_dict.items():

                # 選択されているチャプター名と同じ場合...
                if value[0]['Chapter'] == chapter_name:

                    # なおかつ、解放されたレッスン番号と同じである場合...
                    if key in user_lesson_ids:
                        lessons.append(value[0]['Lesson'])  # レッスンの選択メニューに追加する

        # 「レッスン」の選択
        lesson_name = st.sidebar.selectbox("レッスンを選択してください",(lessons), on_change = init_lesson)

        # レッスンから「選択してください」以外が選ばれた場合の処理
        if lessons.index(lesson_name) != 0:

            # アクティビティの追加
            for k,v in title_dict.items():
                if v[0]["Lesson"] == lesson_name:
                    for vv in v[1:]:
                        activitys.append(vv['Activity'])

        # 参考：activity_name = st.sidebar.selectbox("アクティビティを選択してください",(activitys), on_change = init_activity, args=(chapter_name, lesson_name, activity_name,))
        activity_name = st.sidebar.selectbox("アクティビティを選択してください",(activitys), on_change = init_activity)

        
    # ### メニューからアクティビティを特定する処理 ###
    if chapter_name != '追加登録':

        # 選択されているアクティビティを特定する（アクティビティの名前で特定）
        for k,v in title_dict.items():
            if v[0]['Lesson'] == lesson_name:
                for vv in v[1:]:
                    if vv['Activity'] == activity_name:
                        # Activityの情報を格納（JSONファイルの読み込み用）
                        st.session_state['lesson_id'] = k
                        st.session_state['activity_id'] = vv['Activity_ID']
                        st.session_state['activity_name'] = vv['Activity']
                        st.session_state['activity_steps'] = vv['Steps']


    ###************************************************************************###
    ### アクティビティのメイン画面（体験版・正式版共通） ###
    ###************************************************************************###
    if st.session_state['activity_steps'] == 0:
        # レッスン・アクティビティが選択されていない場合...

        # アクティビティ無選択状態でのメインのレイアウト #
        if  st.session_state['trial_flg'] == True:
            st.subheader('スタ塾 AI活用編 アクティビティポータル（体験版）')
        else:
            st.subheader('スタ塾 AI活用編 アクティビティポータル')

        # レッスンが無選択状態の場合
        if lessons.index(lesson_name) == 0 and chapter_name != '追加登録':
            st.info('左側のメニューから「レッスン」を選択してください')
        else:
            # レッスンが無選択状態の場合
            if activitys.index(activity_name) == 0 and chapter_name != '追加登録':
                st.info('左側のメニューから「アクティビティ」を選択してください')

    else:

        # ActivityのJSONファイルを辞書型で読み込む
        file_path = './datasets/activity/' + st.session_state['lesson_id'] + '_' + st.session_state['activity_id'] + '.json'
        json_file = open(file_path, 'r', encoding="utf-8")
        activity_dict = json.load(json_file)

        ###************************************************************************###
        ## アクティビティのサイドバーレイアウト（下段に追加） ##
        ###************************************************************************###
        step_list = []

        # 個人用のactivityテーブルから（合格している）ステップID（の最大値）を取得する
        datas = get_pass_activity_step(csor, st.session_state['lesson_id'], st.session_state['activity_id'])

        if datas[0][0] is None:            
            pass_step_id = 1
        else:
            pass_step_id = int(datas[0][0]) + 1


        for i in range(st.session_state['activity_steps']):
            step_list.append('演習' + str(i+1))

        # ミニタイトル「STAR Colab」
        # st.sidebar.markdown('# STAR Colab')

        # 演習ステップが1つだけの場合は、ラジオボタンを非表示にする
        if len(step_list) == 1:
            step_name = '演習1'
        else:
            step_name = st.sidebar.radio("演習を選択してください", step_list, horizontal=True, on_change = init_activity)


        # 選択されている演習xのJSONを取得する
        step_dict = activity_dict[step_name][0]


        # 直前の演習を合格しているかどうかで分岐する（合格していなければ警告メッセージを表示）
        step_id = int(step_dict['step'])    # 現在、選択中の演習番号
        if step_id <= pass_step_id:

            ###************************************************************************###
            # 前の演習を合格していてアクセル権が認められる場合の処理群
            ###************************************************************************###

            # サブタイトルエリア（key == 'subtitle'）
            if 'subtitle' in step_dict.keys():
                st.sidebar.caption('演習名')
                st.sidebar.success(step_dict['subtitle'])

            # プログラムの実行ボタン（key == 'result'）
            if 'result' in step_dict.keys():

                col = st.sidebar.columns([4, 6])
                # col[0].caption('Click here ->')
                # ret_help_button = col[0].button('最初に戻す')
                ret_exec_button = col[1].button('プログラムの実行')


            ###************************************************************************###
            ## アクティビティのメインエリアレイアウト ##
            ###************************************************************************###

            ###************************************************************************###
            # インフォメーションエリア（key == 'topinfo'）
            ###************************************************************************###
            if 'topinfo' in step_dict.keys():
                # pass
                # メッセージテンプレートを使って変換
                output_text = func_message.conv_message(step_dict['topinfo'])
                st.info(output_text)

            ###************************************************************************###
            # お手本エリア（key == 'hint'）
            ###************************************************************************###
            if 'hint' in step_dict.keys() and 'expand' in step_dict.keys():
                if step_dict['expand'] == 'True':
                    with st.expander("お手本のプログラムを見る",expanded=True):
                        st.code(step_dict['hint'])
                else:
                    with st.expander("お手本のプログラムを見る",expanded=False):
                        st.code(step_dict['hint'])


            ###************************************************************************###
            # プログラミングエリア（key == 'code' and key == 'height'）
            ###************************************************************************###
            if 'code' in step_dict.keys() and 'height' in step_dict.keys() :
                # プログラミングエリアのフォントサイズを指定（フォントファミリーは指定できなかった）
                st.markdown(
                    """
                    <style>
                    textarea {
                        font-size: 1.0rem !important;
                        font-family:  serif;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
                # 参考
                # https://discuss.streamlit.io/t/change-input-text-font-size/29959/3


                # 個人用のactivityテーブルからcodeを取得する（passflgがINIT以外）
                datas = get_activity_code(csor, st.session_state['lesson_id'], st.session_state['activity_id'], step_id)

                if len(datas) == 0 or st.session_state['trial_flg'] == True:    # 体験版の場合は強制的にJSONのコードを表示
                    # JSONから初期コードを設定
                    txt_input = st.text_area('プログラミングエリア', value=step_dict['code'] ,max_chars=500, height=step_dict['height'])
                else:
                    # データベースから保存済みコードを設定
                    txt_input = st.text_area('プログラミングエリア', value=datas[0][0]       ,max_chars=500, height=step_dict['height'])


            ###************************************************************************###
            # 実行結果エリア（key == 'result'）
            ###************************************************************************###
            if 'result' in step_dict.keys():
            
                st.markdown('実行結果エリア')

                # 実行ボタン
                if ret_exec_button == False:
                    st.warning('まだ実行されていません')

                else:
                    ### プログラミングエリアの内容をデータベースに保存 ###
                    if st.session_state['trial_flg'] == False:  # 体験版は保存しない
                        set_activity_code(conn, csor, st.session_state['lesson_id'], st.session_state['activity_id'], step_id, txt_input)

                    ### プログラミングエリアの置換処理群 ###

                    # 出力の有無フラグ
                    output_flg = False

                    # プログラミングエリアの内容をディープコピー
                    txt_exec = copy.deepcopy(txt_input)

                    # print文をst.infoに置換
                    if 'print' in txt_exec:
                        txt_exec = txt_exec.replace('print', 'st.success')
                        output_flg = True

                    # プログラミングエリアに書かれた「import ijin」 を 実際のモジュール名に置換
                    module_path = st.session_state['lesson_id'] + '_' + st.session_state['activity_id']
                    import_text =  'from modules.activity import ' + module_path
                    txt_exec = txt_exec.replace('import ijin', import_text)

                    # モジュール名を架空（starai.）から実際（例:ai01_01_a2）の名称に置換
                    txt_exec = txt_exec.replace('ijin.', module_path + '.')


                    try:
                        # 文字列の中身をプログラムとして実行
                        exec(txt_exec)    # 実行

                        # key : 'result' の指定 = image の場合
                        if step_dict['result'] == 'image':

                            # 描画する画像イメージの有無を確認
                            if 'img_exec' in st.session_state:
                                # 生成した画像の描画
                                st.image(st.session_state['img_exec'], use_column_width = None)
                                output_flg = True

                        # マッチングの検査（key == 'matching'）
                        if 'matching' in step_dict.keys():

                            tmp_txt_input = txt_input
                            tmp_txt_input = tmp_txt_input.replace('\n','')
                            tmp_txt_input = tmp_txt_input.replace(' ','')

                            tmp_txt_hint = step_dict['hint']
                            tmp_txt_hint = tmp_txt_hint.replace('\n','')
                            tmp_txt_hint = tmp_txt_hint.replace(' ','')

                            if tmp_txt_input == tmp_txt_hint:
                                st.session_state['activity_state'] = 'success'

                                # key : 'result' の指定 = nothing の場合
                                if step_dict['result'] == 'nothing':
                                    st.success('処理が正常に完了しました')
                                    output_flg = True
                            else:
                                st.session_state['activity_state'] = 'error'
                                print(f'マッチングエラー : {e}')
                                st.error('Error !!')
                                output_flg = True
                        else:
                            st.session_state['activity_state'] = 'success'

                    except Exception as e:

                        print(f'エラー : {e}')
                        st.error('Error !!')
                        output_flg = True

                        st.session_state['activity_state'] = 'error'

                    # 何も出力がなかった場合の表示
                    if output_flg == False:
                        st.success('処理が正常に完了しました')


            ###************************************************************************###
            # 状態によって変化するエリア（key == 'before', 'success', 'error'）
            ###************************************************************************###
            if st.session_state['activity_state'] in  step_dict.keys():

                # 'before', 'success', 'error' から吹き出しとフレームの辞書を取り出す
                status_dict = step_dict[st.session_state['activity_state']][0]

                ###************************************************************************###
                # イメージエリア（image)
                ###************************************************************************###
                if 'image' in status_dict.keys():
                    image_file_path = './assets/lesson/' + st.session_state['lesson_id'] + '/'
                    image_file_path = image_file_path + status_dict['image']
                    st.image(image_file_path, use_column_width='always')

                ###************************************************************************###
                # セル型イメージエリア（cellimage)
                ###************************************************************************###
                if 'cellimage' in status_dict.keys():
                    image_file_path = './assets/lesson/' + st.session_state['lesson_id'] + '/'
                    cell_list = status_dict['cellimage']
                    col1 = st.columns(len(cell_list)) # カラムを作成
                    col2 = st.columns(len(cell_list)) # カラムを作成

                    for idx, cell in enumerate(cell_list):
                        col1[idx].image(image_file_path + cell[0])   # 画像を表示
                        col2[idx].write(cell[1])                     # 説明を表示

                ###************************************************************************###
                # 外部ライブラリエリア
                ###************************************************************************###
                if 'module' in status_dict.keys():
                    module_path = st.session_state['lesson_id'] + '_' + st.session_state['activity_id']
                    exec('from modules.activity import ' + module_path)          # インポート
                    exec(module_path + '.view_activity(step_dict, status_dict)') # 関数を起動

                ###************************************************************************###
                # 吹き出しエリア（before, success, error -> balloon, name, text)        
                ###************************************************************************###
                if 'balloon' in status_dict.keys() and 'name' in status_dict.keys() and 'text' in status_dict.keys():
                    file_name = status_dict['balloon']
                    text = func_message.conv_message(status_dict['text'])                                
                    text_html = func_html.make_html_balloon(file_name, func_html.trans_html_tag(text))
                    stc.html(text_html, height=150)

                ###************************************************************************###
                # フレームエリア（before, success, error -> head, frame, size)
                ###************************************************************************###
                if 'head' in status_dict.keys() and 'frame' in status_dict.keys() and 'size' in status_dict.keys():
                    text = func_message.conv_message(status_dict['frame'])                                
                    ret = func_html.make_html_frame(status_dict['head'], func_html.trans_html_tag(text))
                    stc.html(ret,height=status_dict['size'])

                ###************************************************************************###
                # 末尾コメントエリア（key == 'tail'）
                ###************************************************************************###
                if 'tail' in status_dict.keys():
                    st.caption(status_dict['tail'])


                ###************************************************************************###
                # 合否フラグの編集エリア（key == 'tail'）
                ###************************************************************************###
                if 'passflg' in status_dict.keys():

                    if st.session_state['trial_flg'] == False:  # 体験版は更新しない
                        # 実行後の状態（OK or NG）で個人用データベースのpassflgを更新する
                        set_activity_passflg(conn, csor, st.session_state['lesson_id'], st.session_state['activity_id'], step_id, status_dict['passflg'])


        else:
            ###************************************************************************###
            # まだ合格していないステップの場合の警告メッセージ
            ###************************************************************************###
            text = func_message.conv_message('warning_01')                                
            text_html = func_html.make_html_balloon('ai010.png', func_html.trans_html_tag(text))
            stc.html(text_html, height=150)


    ###************************************************************************###
    ### アクティビティの追加登録処理のレイアウト ###
    ###************************************************************************###
    if chapter_name == '追加登録':

        # プレースホルダの設定
        layout_10 = st.empty()
        layout_20 = st.empty()
        layout_30 = st.empty()
        col = st.columns([8, 2])
        layout_41 = col[0].empty()
        layout_42 = col[1].empty()

        st.session_state['activity_steps'] = 0

        # layout_10.header('Python 演習環境 "STAR Colab" へ ようこそ')

        # フォームのレイアウト
        form = layout_20.form('add_act_form', clear_on_submit=True)
        form.subheader('レッスンの追加登録')
        keyword = form.text_input(label='アクティビティの手順書に書かれている「キーワード」を入力してください', value='')
        submitted = form.form_submit_button("追加登録")

        # 追加登録ボタン（サブミット）が押された場合
        if submitted:

            # ダミースピナーを表示
            with st.spinner('処理中...'):
                time.sleep(DELAY_TIME)

            # 辞書キーの存在チェック
            if keyword in keyword_dict.keys():

                # レッスン番号（例. ai00_00)をJSONから取得
                lesson_id = keyword_dict[keyword]['Lesson_ID']

                # 該当アクティビティの情報を取得
                lesson_dict = title_dict[lesson_id][0]
                lesson_activity_list = title_dict[lesson_id][1:]

                # lessonの確認メッセージ
                message = '「' + lesson_dict['Chapter'] + '」のレッスン『' + lesson_dict['Lesson'] + '』' + 'を追加登録しました'
                layout_41.write(message)

                # 確認用のボタンを表示
                layout_42.button('読み込み')

                # 個人用のactivityテーブルに lesson_id, activity_id, step_id, passflg, code を ステップの行数だけ追加する
                add_user_activitys(conn, csor, lesson_id, lesson_activity_list)

            else:
                message = 'キーワード「' + keyword + '」は存在しません。アクティビティの手順書を確認してください。'
                layout_30.write(message)


    # データベースを切断（個人用db） 
    conn.close()


def main():

    ### 各種フラグなどを初期化する関数をコール ###
    init_parameters()

    # タブに表示されるページ名の変更
    st.set_page_config(page_title="アクティビティ ポータル(C2)", initial_sidebar_state="expanded")

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
