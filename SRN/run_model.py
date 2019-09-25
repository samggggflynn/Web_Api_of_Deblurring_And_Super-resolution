import os
import argparse
import tensorflow as tf
# import models.model_gray as model
# import models.model_color as model
import SRN.models.model as model

class config():
    datalist = './SRN/datalist_gopro.txt'
    model = 'color'
    batch_size = 16
    epoch = 4000
    learning_rate = 1e-4
    gpu_id = '0'
    height = 720
    width = 1280
    input_path = './SRN/testing_set'
    output_path = './SRN/testing_res'



def main():
    args = config()
    # set gpu/cpu mode
    if int(args.gpu_id) >= 0:
        os.environ['CUDA_VISIBLE_DEVICES'] = args.gpu_id
    else:
        os.environ['CUDA_VISIBLE_DEVICES'] = ''

    # set up deblur models
    deblur = model.DEBLUR(args)
    deblur.test(args.height, args.width, args.input_path, args.output_path)
