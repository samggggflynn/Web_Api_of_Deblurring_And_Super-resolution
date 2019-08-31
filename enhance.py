# -*- coding: utf-8 -*-
'''
利用对比度进行暗光增强
分离BGR通道，对每个通道做“限制对比度自适应直方图均衡化”
date:2019年7月16日
备注:
'''
import cv2

def enhance(src):
    # src = cv2.imread("test.jpg")  # 读入图像数组
    # 分离BGR通道
    src_B, src_G, src_R  = cv2.split(src)
    # 创建CLAHE对象（对每个通道）
    clahe_B = cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8))
    clahe_G = cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8))
    clahe_R = cv2.createCLAHE(clipLimit=2.0,tileGridSize=(8,8))
    # 限制对比度的自适应阈值均衡化（对每个通道）
    dst_B = clahe_B.apply(src_B)
    dst_G = clahe_G.apply(src_G)
    dst_R = clahe_R.apply(src_R)
    # 通道合并
    dst = cv2.merge([dst_B, dst_G, dst_R])
    return dst
    # 显示
    # cv2.imshow("src",src)
    # cv2.imshow("dst",dst)
    #
    # cv2.imwrite("dst1.jpg",dst)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()