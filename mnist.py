import os
from flask import Flask, request, redirect, render_template, flash, session
from werkzeug.utils import secure_filename
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.preprocessing import image

import numpy as np


classes = ["0","1","2","3","4","5","6","7","8","9"]
image_size = 28

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.secret_key = 'hogehoge' #session

def allowed_file(filename):
    #次の2つの条件をand確認
    #1. filenameの中に.が含まれているかどうか
    #2. 拡張子の確認。filenameを文字列の最後から「.で１回」区切り、
    #取り出した1番目の要素を小文字に変換し、ALLOWED_EXTENSIONSのどれかに該当するかどうか
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

model = load_model('./model.h5')#学習済みモデルをロード


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' in request.files:
            flash('ファイルがありません')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('ファイルがありません')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            #flash(request.url) #flashの確認のため故意にrequest.urlを表示

            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            #受け取った画像を読み込み、np形式に変換
            img = image.load_img(filepath, grayscale=True, target_size=(image_size,image_size))
            img = image.img_to_array(img) #引数に与えられた画像をNumpy配列に変換
            data = np.array([img]) #Numpy配列のリストに変換
            #変換したデータ(Numpy配列のリスト)をモデルに渡して予測する
            result = model.predict(data)[0]
            predicted = result.argmax()
            pred_answer = "これは " + classes[predicted] + " です"

            return render_template("index.html",answer=pred_answer)

    #POSTリクエストがなされないとき（単にURLにアクセスしたとき）
    return render_template("index.html",answer="")

if __name__ == "__main__":
    #app.run()
    #外部公開
    port = int(os.environ.get('PORT', 8080))
    app.run(host ='0.0.0.0',port = port)
