# HTMLの独自短縮タグを標準のタグに変換する関数
def trans_html_tag(str_message):
        
        str_message = str_message.replace('<R>', '<font color=red>')
        str_message = str_message.replace('<G>', '<font color=green>')
        str_message = str_message.replace('<B>', '<font color=blue>')
        str_message = str_message.replace('<P>', '<font color=purple>')
        str_message = str_message.replace('</>', '</font>')
        str_message = str_message.replace('<C>', '<br>')

        return str_message

# HTML文字列を生成する関数（枠）
def make_html_frame(str_title, str_message):

        str1 = """
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>

        /* 枠 */
        .frame {
        position: relative;
        display: inline-block;
        /* margin: 30px 10px; */
        /* padding: 20px 10px 10px 20px; */
        margin: 10px;
        padding: 20px 10px 10px 20px;
        background-color: #EEEEEE;
        border-radius: 10px;
        }

        /* 枠 */
        .frame::before {
        content: '"""

        str2 = """';
        position: absolute;
        top: -15px;
        left: -10px;
        padding: 10px;
        /* background-color: #3232cd; */
        background-color: #8a8afa;
        border-radius: 12px;
        font-size: 16px;
        color: #fff;
        font-weight: bold;
        }

        </style>
        </head>
        <body>

        <!-- フレーム -->
        <div class="frame">
                <p>"""

        str3 = """</p>
        </div>
        </body>
        </html>"""

        ret = str1 + str_title + str2 + str_message + str3
        return ret


# HTML文字列を生成する関数（吹き出し）
def make_html_balloon(file_name, str_message):

        str1 = """
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>

                /* Flexbox */
                .flex {
                display: flex;
                }

                .items-center {
                align-items: center;
                }

                /* 吹き出し（左） */
                .balloon-left {
                position: relative;
                display: inline-block;
                margin: 1.5em 0 1.5em 15px;
                padding: 1em;
                min-width: 120px;
                max-width: 100%;
                color: #555;
                font-size: 16px;
                background: aliceblue;
                border-radius: 15px;
                border: solid 1px #888;
                }

                .balloon-left:before {
                content: "";
                position: absolute;
                top: 50%;
                left: 0;
                width: 10px;
                height: 10px;
                transform: translate(-50%, -50%) rotate(45deg);
                background: aliceblue;
                border-left: solid 1px #888;
                border-bottom: solid 1px #888;
                }

                .balloon-left p {
                margin: 0;
                padding: 0;
                }

                </style>
                </head>
                <body>

                <!-- キャラクターと吹き出し -->
                <div class="flex items-center">
                <div>
                <img src="https://nai-lab.com/poc/starai/ai00-02/static/assets/character/"""

        str2 = """" alt="" style="width: 120px; height:auto;">
                </div>
                <div class="balloon-left">
                <p>"""

        str3 = """</p>
                </div>
                </div>

                </body>
                </html>"""

        ret = str1 + file_name + str2 + str_message + str3

        return ret