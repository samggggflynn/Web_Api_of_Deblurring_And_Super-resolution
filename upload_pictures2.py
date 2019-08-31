# coding:utf-8

from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify, Response
import paramiko
import zipfile
import json
from werkzeug.utils import secure_filename
import os
import shutil
import cv2
import time
from datetime import timedelta
from SRN import run_model
from ESRGAN import test

from enhance import enhance

# 设置允许的文件格式
# 按需添加格式
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'JPG', 'PNG', 'bmp'])


# 查看上传文件是否是zip文件
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1] == 'zip'


# 看上传图片是否是对应的图片格式
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 设置json显示中文
# 设置静态文件缓存过期时间
app.send_file_max_age_default = timedelta(seconds=1)


@app.route('/image_deblurring', methods=['POST', 'GET'])  # 添加路由

def image_deblurring():
    if request.method == 'POST':
        f = request.files['file']

        if not (f and allowed_file(f.filename)):
            return jsonify({"error": 1001, "error_msg": "format error：请检查上传的图片类型，仅限于png、PNG、jpg、JPG、bmp"})

        basepath = os.path.dirname(__file__)  # 当前文件所在路径

        upload_path = os.path.join(basepath, 'SRN/testing_set', secure_filename(f.filename))  # 注意：没有的文件夹一定要先创建，不然会提示没有该路径
        download_path = os.path.join(basepath, 'SRN/testing_res', secure_filename(f.filename))
        upload_dir = os.path.join(basepath, 'SRN/testing_set')

        # 清除历史文件
        if os.path.isdir(upload_dir):
            shutil.rmtree(upload_dir)
        else:
            os.makedirs(upload_dir)

        f.save(upload_path)

        # 使用Opencv转换一下图片格式和名称
        src = cv2.imread(upload_path)
        cv2.imwrite(os.path.join(basepath, 'static/images/image_deblurring', 'src.jpg'), src)

        run_model.main()

        res = cv2.imread(download_path)
        cv2.imwrite(os.path.join(basepath, 'static/images/image_deblurring', 'res.jpg'), res)


        return render_template('upload_ok2.html', val1=time.time())

    return render_template('upload2.html')

@app.route('/image_enhance', methods=['POST', 'GET'])  # 添加路由

def image_enhance():
    if request.method == 'POST':
        f = request.files['file']

        if not (f and allowed_file(f.filename)):
            return jsonify({"error": 1001, "error_msg": "format error：请检查上传的图片类型，仅限于png、PNG、jpg、JPG、bmp"})

        basepath = os.path.dirname(__file__)  # 当前文件所在路径

        upload_path = os.path.join(basepath, 'ESRGAN/LR', secure_filename(f.filename))  # 注意：没有的文件夹一定要先创建，不然会提示没有该路径
        download_path = os.path.join(basepath, 'ESRGAN/results', f.filename.split('.')[0]+'.png')
        print(download_path)
        upload_dir = os.path.join(basepath, 'ESRGAN/LR')

        # 清除历史文件
        if os.path.isdir(upload_dir):
            shutil.rmtree(upload_dir)
        os.makedirs(upload_dir)

        f.save(upload_path)

        # 使用Opencv转换一下图片格式和名称
        src = cv2.imread(upload_path)
        cv2.imwrite(os.path.join(basepath, 'static/images/image_enhance', 'src.png'), src)

        test.esr()


        res = cv2.imread(download_path)
        cv2.imwrite(os.path.join(basepath, 'static/images/image_enhance', 'res.png'), res)


        return render_template('upload_ok3.html', val1=time.time())

    return render_template('upload3.html')


if __name__ == '__main__':
    # app.debug = True
    # if not os.path.exists(upload_path):
    #     os.makedirs(upload_path)
    app.run(host='0.0.0.0', port=5000, debug=True)