# coding:utf-8

from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify, Response
import json
from werkzeug.utils import secure_filename
import os
import cv2
import time
from datetime import timedelta

from enhance import enhance
# import red_print
# from red_print import draw_rectangle_r
# 设置允许的文件格式

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'JPG', 'PNG', 'bmp'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 设置json显示中文
# 设置静态文件缓存过期时间
app.send_file_max_age_default = timedelta(seconds=1)
@app.route('/')
def up():
    return render_template('upload2.html')

# @app.route('/upload', methods=['POST', 'GET'])
@app.route('/enhance/upload', methods=['POST', 'GET'])  # 添加路由
def upload():
    if request.method == 'POST':
        f = request.files['file']

        if not (f and allowed_file(f.filename)):
            return jsonify({"error": 1001, "error_msg": "format error：请检查上传的图片类型，仅限于png、PNG、jpg、JPG、bmp"})

        # user_input = request.form.get("name")

        basepath = os.path.dirname(__file__)  # 当前文件所在路径

        upload_path = os.path.join(basepath, 'static/images', secure_filename(f.filename))  # 注意：没有的文件夹一定要先创建，不然会提示没有该路径
        # upload_path = os.path.join(basepath, 'static/images','test.jpg')  #注意：没有的文件夹一定要先创建，不然会提示没有该路径
        f.save(upload_path)

        # 使用Opencv转换一下图片格式和名称
        src = cv2.imread(upload_path)
        cv2.imwrite(os.path.join(basepath, 'static/images', 'src.jpg'), src)
        # 调用enhance()处理输出保存
        dst = enhance(src)
        cv2.imwrite(os.path.join(basepath, 'static/images', 'result.jpg'), dst)
        # send_json()

        return render_template('upload_ok.html', val1=time.time())

    return render_template('upload.html')


if __name__ == '__main__':
    # app.debug = True
    # if not os.path.exists(upload_path):
    #     os.makedirs(upload_path)
    app.run(host='0.0.0.0', port=8987, debug=True)