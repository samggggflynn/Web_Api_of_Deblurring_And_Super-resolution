#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, request
import paramiko
import json
import zipfile
import os
import shutil
import time
from ESRGAN import test
from SRN import run_model


# 设置允许的文件格式
ALLOWED_EXTENSIONS = set(['jpg', 'JPG', 'png', 'PNG', 'jpeg' 'bmp'])


# 查看上传文件是否是zip文件
def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[-1] == 'zip'


# 查看上传图片是否是对应的图片
def allowed_pic(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1] in ALLOWED_EXTENSIONS


# 服务器上传单张图片
def upload_pic(localfile, remotefile):
    # 远程连接服务器的ip，端口号
    client = paramiko.Transport(("88.88.88.88", 88))
    # 服务器的 账户名 ，密码
    client.connect(username="root", password="123456")
    sftp = paramiko.SFTPClient.from_transport(client)
    try:
        sftp.put(localfile, remotefile)
        print('服务器上传成功!')
        client.close()
        return 1
    except Exception:
        print("服务器上传失败")
        client.close()
        return 0


# 将压缩包batch解压缩到folder_path
def un_zip(batch, folder_path):
    zip_file = zipfile.ZipFile(batch)
    # folder_path是图片解压后存放的文件夹名
    if os.path.isdir(folder_path):
        pass
    else:
        os.mkdir(folder_path)

    # 遍历压缩包中的每个图片文件，检查格式，并且解压文件到解压文件夹
    for names in zip_file.namelist():
        if names.rsplit('.', 1)[-1] in ALLOWED_EXTENSIONS:
            zip_file.extract(names, folder_path)
    zip_file.close()


# 将结果压缩
def go_zip(target_path, target):
    enhance_pics = list(os.walk(target))[0][2]
    with zipfile.ZipFile(target_path, 'w', zipfile.ZIP_DEFLATED) as zipping:
        '''
        zipfile.ZipFile(fileName [,mode [, compression[, allowZip64]]])
        model和一般的文件操作一样，’r'表示打开一个存在的只读ZIP文件，‘w'表示清空并打开一个只写的ZIP文件，或创建一个只写的ZIP文件；
        ’a'表示打开一个ZIP文件，并添加内容。
        compression表示压缩格式，可选的压缩格式只有2个：ZIP_STORE; ZIP_DEFLATED。ZIP_STORE是默认的，表示不压缩，ZIP_DEFLATED表示压缩。
        allowZip64 为True时，表示支持64位的压缩，一般而言，在所压缩的文件大于2G时，会用到这个选项；默认情况下，该值为Flase，因为Unix系统不支持。
        '''
        for m in enhance_pics:
            zipping.write(target+'/'+m, '/result/'+m)

    print('压缩完毕')
    return target_path


# 将结果压缩包上传到服务器（与单张上传完全一样，可以只写一个上传函数）
def upload_batch(localfile, remotefile):
    # 远程连接服务器的ip，端口号
    client = paramiko.Transport(("88.88.88.88", 88))
    # 服务器的 账户名 ，密码
    client.connect(username="root", password="123456")
    sftp = paramiko.SFTPClient.from_transport(client)
    try:
        sftp.put(localfile, remotefile)
        print('批量处理结果上传服务器成功!')
    except Exception:
        print("批量处理结果上传服务器失败!")
    client.close()


app = Flask(__name__)


# 添加*单张*超清还原接口的路由
@app.route('/image_enhance/solo_pic', methods=['POST', 'GET'])  # 添加路由
def image_enhance_solo():
    if request.method == 'POST':
        start = time.time()
        solo_pic = request.files['solo_pic']

        if not (solo_pic and allowed_file(solo_pic.filename)):
            # return jsonify({"error": 1001, "error_msg": "format error：请检查上传的图片类型，仅限于png、PNG、jpg、JPG、bmp"})
            RuntimeError("Please check the uploaded file!")
        basepath = os.path.dirname(__file__)  # 当前文件所在路径
        # 打印输出当前路径
        # print(basepath)
        # 修改上传的文件名
        unix_time = int(time.time())
        new_p_name = str(unix_time) + '.png'
        # 上传文件保存路径
        upload_path = os.path.join(basepath, 'ESRGAN/LR')
        upload_dir = os.path.join(basepath + '/ESRGAN/LR/%s' % new_p_name)
        # 清除历史文件
        if os.path.isdir(upload_path):
            shutil.rmtree(upload_path)
        os.makedirs(upload_path)
        # 将待处理的图片存为临时文件
        solo_pic.save(upload_dir)
        # 使用一个字典封装返回结果
        solo_rlt = {}
        solo_rlt['method'] = 'Super-resolution'
        # 图像处理
        test.esr()
        # 本地保存位置
        local_pic = basepath + '/ESRGAN/results/%s' % new_p_name
        print(local_pic)
        remote_pic = '/home/XYZ/images/%s' % new_p_name
        # 上传到服务器
        upload_status = upload_pic(local_pic, remote_pic)
        # 将图片服务器对应的地址放入结果中返回
        if upload_status == 1:
            solo_rlt['solo_path'] = '/ESRGAN/results/%s' % new_p_name
        elif upload_status == 0:
            solo_rlt['solo_path'] = 'None'
        end = time.time()
        print("处理耗时: %s" % (end - start))
        solo_rlt['cost time'] = (end - start)
        return json.dumps(solo_rlt, ensure_ascii=False)
    else:
        return RuntimeError("Only Accept POST Request!")


# 添加去模糊的批处理图片的路由
@app.route('/image_enhance/batch', methods=['POST', 'GET'])
def image_enhance_batch():
    if request.method == 'POST':
        start = time.time()
        # 接收前端传过来的一个压缩文件
        try:
            batch = request.files.get("batch")
            print("接收到上传压缩文件：", batch.filename)
        except Exception:
            raise RuntimeError("Please check the uploaded file!")
            # return '<h1>请正确上传文件</h1>'
        if not allowed_file(batch.filename):
            raise RuntimeError("请上传zip格式的压缩文件!")
            # return '<h1>请检查zip格式的压缩包</h1>'

        # 当前服务文件所在的路径
        base_path = os.path.dirname(__file__)
        print("当前运行的目录路径为： ", base_path)

        # 将接收到的压缩包*解压*到指定目录folder_path下(floder_path为 /ESRGAN/LR）
        folder_path = os.path.join(base_path + '/ESRGAN/LR')
        un_zip(batch, folder_path)

        # 运行处理程序（从LR中批量处理，结果保存到results中）
        res_path = os.path.join(base_path + '/ESRGAN/results')
        # 运行前把上次的结果清空
        if os.path.isdir(res_path):
            shutil.rmtree(res_path)
            # pass
        os.makedirs(res_path)

        test.esr()

        print('批量去模糊完毕，开始打包进行上传！')
        # 将结果文件夹压缩成zip包，命名为 "时间戳.zip"
        batch_name = int(time.time())
        zipped_file = go_zip(base_path + '/tmp/%d.zip' % batch_name, res_path)
        end = time.time()
        print("处理耗时: %s" % (end - start))

        # 将图片上传到FTP服务器上
        print("分类结果的本地文件在：", zipped_file)
        remote_file = '/home/XYZ/images/%d.zip' % batch_name
        print('将文件传送到服务器上：%d.zip' % batch_name)
        upload_batch(zipped_file, remote_file)
        # 将原文件夹及当中的文件删除
        try:
            shutil.rmtree(folder_path)
            print('解压文件夹%s删除成功！' % folder_path)
        except Exception:
            print('解压文件夹%s删除失败！' % folder_path)

        # 使用一个字典封装返回结果
        batch_rlt = {}
        # method字段
        batch_rlt['method'] = 'Super-resolution'
        # 处理用时放入结果返回
        batch_rlt['cost time'] = (end - start)
        # 将图片服务器对应的地址放入结果中返回
        batch_rlt['batch_path'] = '/tmp/%d.zip' % batch_name
        return json.dumps(batch_rlt, ensure_ascii=False)
    else:
        raise RuntimeError("Only Accept POST Request!")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7777, debug=True, threaded=True)
