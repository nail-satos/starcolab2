### 必要な外部ライブラリをインポートする

### テンプレートメッセージを変換する関数
def conv_message(input_text):

    output_text = input_text

    if input_text == 'topinfo_01':
        output_text = 'プログラミングエリアに記述されているPythonのプログラムを確認します。先生のセリフと下段の「説明」をよく読んでから、左側の《プログラムの実行》ボタンを押しましょう。'

    if input_text == 'topinfo_02':
        output_text = 'お手本を見ながら、プログラミングエリアにPythonのプログラムを修正します。修正が完了したら、左側の《プログラムの実行》ボタンを押して、実行結果エリアを確認しましょう。'

    if input_text == 'topinfo_03':
        output_text = 'お手本を見ながら、プログラミングエリアにPythonのプログラムを入力します。入力が完了したら、左側の《プログラムの実行》ボタンを押して、実行結果エリアを確認しましょう。'

    if input_text == 'error_01':
        output_text = 'エラー（プログラムの誤り）が発生したようです<C>プログラミングエリアの内容に誤りがないか確認してください'

    if input_text == 'error_02':
        output_text = '困ったら<P>《お手本のプログラム》</>を確認して、入力したプログラムと比べましょう。<C>誤りを修正したら、もう一度<P>《プログラムの実行》</>ボタンを押して実行してください。'

    if input_text == 'error_03':
        output_text = 'この手順ではプログラムの「エラー（誤り）」を体験します<C>お手本のプログラムの通りに入力して もう一度 実行してください'

    if input_text == 'warning_01':
        output_text = 'この演習を行うには 前の演習を完了させる必要があります<C>順番に演習を進めていきましょう'

    if input_text == 'frameinfo_01':
        output_text = 'STAR Colabはスタ塾が独自に開発したPython実行環境です。一部のPythonの命令は、STAR Colab上では動作が制限（例．画像を表示する、音楽を鳴らす等）されます。'

    return output_text