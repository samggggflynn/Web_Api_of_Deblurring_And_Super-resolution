# Web_Api_of_Deblurring_And_Super-resolution
	
Python language development,based on flask-python web framework,Front-end back-end separation, only provide the backend interface,use postman's HTTP simulation request for testing.
	
# 图像解模糊和超分辨率还原的Web接口

图像解模糊（deblurring）和图像超分辨率还原（Super-resolution）深度学习框架tensorflow和torch，并实现web后端基于python-Flask框架的接口，python语言。

*可以搭建自己的图像处理网站。*

## 文档说明

最近写的一个`FLask`图像处理接口，因为涉及到需要展示，也尝试加了前端页面，后来为了独立前后端，做了前后端分离，这里只保留了后端接口，结果以`json`字典的形式返回。 因为测试的机器为自己的电脑，只加入了文件上传到远程服务器，测试的机器为cpu版本的深度学习框架，运行速度较慢（平均一张处理时间2-30s…）。

后来新加了批量处理的接口，*上传格式要求为`.zip`的压缩包*。

### 可能需要的包和框架：

`pip install flask paramiko json zipfile os shutil time`

需要修改服务器ip、端口号，登录账号、密码。（如果有需要上传到服务器，不需要可以注释掉上传服务器的代码）
### 文件结构说明

注：ESRGAN为存放解模糊代码文件夹，待处理的文件夹为`ESRGAN/LR`接口py文件运行处理后会创建；`ESRGAN/results`为存放处理后的文件夹

注：SRN为超清晰还原的代码文件夹，待处理的文件夹为`SRN/testing_set`接口py文件运行处理后会创建；`SRN/testing_res`为存放处理后的文件夹

批量处理的结果保存在本地`tmp/`下以时间戳命名的zip压缩包。

`/upload_pictures.py`是一个暗光增强接口（使用`openCV`做限制对比度自适应直方图均衡化，处理过程`/enhance.py`），也是后续接口工作修改的基石，绑定了前后端，做了一个简单的上传页面和展示处理结果页面的跳转，因为页面简单，也没有考虑异步刷新的问题。前端上传页面`templates/upload.html`前端展示返回页面`templates/upload_ok.html`

`/upload_pictures2.py`是将*解模糊*和*超清晰还原*接口套入`/upload_pictures.py`中使用的初始版本，可以使用，因为前端页面使用了其他人的工作，故也没有前端页面，浏览器无法访问…

后续修改版，*解模糊*对应`Debluring_api.py`，分别设计了单张解模糊，和上传zip压缩包批量处理。
*超分辨率还原*对应`Enhance_api.py`分别设计了单张分辨率还原，和上传zip压缩包批量处理。

`Deblurring_Enhance_Api.py`将*解模糊*和*超清晰还原*接口放在一起了。

## 测试说明

测试部分使用了[postman](https://www.getpostman.com/downloads/)，下载安装打开。
比如测试批量*超清晰还原*

![](/static/20190901022846.png)

如果测试单张，或测试解模糊，修改`2`处的`url`和`4`处的KEY值，在`5`处上传单张图片。
