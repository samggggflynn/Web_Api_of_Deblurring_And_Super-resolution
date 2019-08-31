import os.path as osp
import glob
import cv2
import numpy as np
import torch
import ESRGAN.RRDBNet_arch as arch
import os
import shutil

def esr():
    model_path = 'ESRGAN/models/RRDB_ESRGAN_x4.pth'  # models/RRDB_ESRGAN_x4.pth OR models/RRDB_PSNR_x4.pth
    # torch.cuda.set_device(0)
    # device = torch.device('cuda')  # if you want to run on CPU, change 'cuda' -> cpu
    device = torch.device('cpu')

    test_img_folder = 'ESRGAN/LR/*'

    model = arch.RRDBNet(3, 3, 64, 23, gc=32)
    model.load_state_dict(torch.load(model_path), strict=True)
    model.eval()
    model = model.to(device)

    idx = 0
    for path in glob.glob(test_img_folder):
        idx += 1
        base = osp.splitext(osp.basename(path))[0]
        # base_1 = osp.splitext(osp.basename(path))[1]
        print(idx, base)
        # read images
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        print(img.shape)
        img = img * 1.0 / 255
        img = torch.from_numpy(np.transpose(img[:, :, [2, 1, 0]], (2, 0, 1))).float()
        img_LR = img.unsqueeze(0)
        img_LR = img_LR.to(device)

        with torch.no_grad():
            output = model(img_LR).data.squeeze().float().cpu().clamp_(0, 1).numpy()
        output = np.transpose(output[[2, 1, 0], :, :], (1, 2, 0))
        output = (output * 255.0).round()

        if os.path.isdir('ESRGAN/results'):
            # shutil.rmtree('ESRGAN/results') 修改：8.30
            pass
        else:
            os.makedirs('ESRGAN/results')
        print("Saving result... ESRGAN/results/%s.png" % base)  # 修改：8.30
        cv2.imwrite('ESRGAN/results/{:s}.png'.format(base), output)
