# 수정중인 파일(serial 통신으로 신호받으면 돌리기)
# 영상으로만 할 거니까 나중에 이미지로 처리하는 부분은 가독성을 위해 다 지우는 게 좋을듯

import argparse
import os
import shutil
import time
from pathlib import Path

import cv2
import torch
import torch.backends.cudnn as cudnn
from numpy import random

from models.experimental import attempt_load
from utils.datasets import LoadStreams, LoadImages
from utils.general import (
    check_img_size, non_max_suppression, apply_classifier, scale_coords,
    xyxy2xywh, strip_optimizer, set_logging)
from utils.plots import plot_one_box
from utils.torch_utils import select_device, load_classifier, time_synchronized

import serial

print('serial'+serial.__version__)

# set a port number & baud rate
PORT = 'COM7'  # 아두이노 연결후 몇번 포트로 연결되는지 확인하고 적어야댐
BaudRate = 9600

ARD = serial.Serial(PORT, BaudRate, timeout=0.1)  # 시리얼 통신을 위한 설정, 선언[;;[]]
# timeout 값을 계속 받는 것을 방지하고자 추가함 Serial Buffer에 값을 2가지 중 1개 time out이 없으면 시리얼 값이 들어올때까지 멈춤 그래서 타임아웃 설정해서


def detect(save_img=False):
    out, source, weights, view_img, save_txt, imgsz = \
        opt.save_dir, opt.source, opt.weights, opt.view_img, opt.save_txt, opt.img_size
    webcam = source.isnumeric() or source.startswith(
        ('rtsp://', 'rtmp://', 'http://')) or source.endswith('.txt')

    cnt = 0
    mat = [0, 0, 0, 0, 0]  # can pls gls trsh none

    # Initialize
    set_logging()
    device = select_device(opt.device)
    if os.path.exists(out):  # output dir
        shutil.rmtree(out)  # delete dir
    os.makedirs(out)  # make new dir
    half = device.type != 'cpu'  # half precision only supported on CUDA

    # Load model
    model = attempt_load(weights, map_location=device)  # load FP32 model
    imgsz = check_img_size(imgsz, s=model.stride.max())  # check img_size
    if half:
        model.half()  # to FP16

    # Second-stage classifier
    classify = False
    if classify:
        modelc = load_classifier(name='resnet101', n=2)  # initialize
        modelc.load_state_dict(torch.load(
            'weights/resnet101.pt', map_location=device)['model'])  # load weights
        modelc.to(device).eval()

    # Set Dataloader
    vid_path, vid_writer = None, None
    if webcam:
        view_img = True
        cudnn.benchmark = True  # set True to speed up constant image size inference
        dataset = LoadStreams(source, img_size=imgsz)
    else:
        save_img = True
        dataset = LoadImages(source, img_size=imgsz)

    # Get names and colors
    names = model.module.names if hasattr(model, 'module') else model.names
    colors = [[random.randint(0, 255) for _ in range(3)]
              for _ in range(len(names))]

    # Run inference
    t0 = time.time()
    img = torch.zeros((1, 3, imgsz, imgsz), device=device)  # init img
    # run once
    _ = model(img.half() if half else img) if device.type != 'cpu' else None
    for path, img, im0s, vid_cap in dataset:
        # 값을 받으면
        if ARD.readline().decode().strip() == "1" or cnt != 0:

            cnt += 1

            img = torch.from_numpy(img).to(device)
            img = img.half() if half else img.float()  # uint8 to fp16/32
            img /= 255.0  # 0 - 255 to 0.0 - 1.0
            if img.ndimension() == 3:
                img = img.unsqueeze(0)

            # Inference
            t1 = time_synchronized()
            pred = model(img, augment=opt.augment)[0]

            # Apply NMS
            pred = non_max_suppression(
                pred, opt.conf_thres, opt.iou_thres, classes=opt.classes, agnostic=opt.agnostic_nms)
            t2 = time_synchronized()

            # Apply Classifier
            if classify:
                pred = apply_classifier(pred, modelc, img, im0s)

            # Process detections
            for i, det in enumerate(pred):  # detections per image
                if webcam:  # batch_size >= 1
                    p, s, im0 = path[i], '%g: ' % i, im0s[i].copy()
                else:
                    p, s, im0 = path, '', im0s

                save_path = str(Path(out) / Path(p).name)
                txt_path = str(Path(out) / Path(p).stem) + ('_%g' %
                                                            dataset.frame if dataset.mode == 'video' else '')
                s += '%gx%g ' % img.shape[2:]  # print string
                # normalization gain whwh
                gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]
                if det is not None and len(det):
                    # Rescale boxes from img_size to im0 size
                    det[:, :4] = scale_coords(
                        img.shape[2:], det[:, :4], im0.shape).round()

                    # Print results
                    # det[:, -1]???? 무슨 의미지??
                    # 한 객체가 여러개 판별된 경우 문자로는 한번만 출력하기 위해 unique사용
                    for c in det[:, -1].unique():
                        # detections per class.
                        n = (det[:, -1] == c).sum()
                        # add to string
                        s += '%g %ss, ' % (n, names[int(c)])
                        # 여기서 c에 판별된 클래스가 들어있음
                        # 판별된 객체마다 카운트해줌 0 can 1 pls 2 gls
                        mat[int(c)] += 1
                else:  # det이 None일 때 -> trsh 1 증가
                    mat[4] += 1

                # Write results
                    for *xyxy, conf, cls in reversed(det):
                        if save_txt:  # Write to file
                            xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) /
                                    gn).view(-1).tolist()  # normalized xywh
                            # label format
                            line = (cls, conf, *
                                    xywh) if opt.save_conf else (cls, *xywh)
                            with open(txt_path + '.txt', 'a') as f:
                                f.write(('%g ' * len(line) + '\n') % line)

                        # 프레임에 라벨 씌우기(can 0.7)이런식으로
                        if save_img or view_img:  # Add bbox to image
                            label = '%s %.2f' % (names[int(cls)], conf)
                            plot_one_box(xyxy, im0, label=label,
                                         color=colors[int(cls)], line_thickness=3)

                # Print time (inference + NMS)
                print('%sDone. (%.3fs)' % (s, t2 - t1))

                if cnt == 10:
                    cnt = 0
                    # can, pls, gls, (trsh + none) 중 젤 많이 나온 것을 serial로 보냄
                    # 나중에 값이 같은 경우도 고려해야 할듯
                    max_mat = -1
                    max_value = 0
                    # for i, m in enumerate(mat):
                    #     if m > max_value:
                    #         max_value = m
                    #         max_mat = i
                    for i in range(3):
                        if mat[i] > max_value:
                            max_value = mat[i]
                            max_mat = i
                    if sum(mat[3:5]) > max_value:
                        max_value = sum(mat[3:5])
                        max_mat = 3  # trsh, none은 합쳐서 3으로 취급
                    print(mat)
                    for i in range(5):
                        mat[i] = 0
                    # 여기서 serial로 max_mat 보내면 됨 0을 넘기면 아두이노에서 인식을 못함. 그래서 1을 더해서 넘겨주기로 함
                    ARD.write(str(max_mat+1).encode())
                    print("print", max_mat + 1)

                elif mat[0] >= 4 or mat[1] >= 4 or mat[2] >= 4 or mat[3] >= 4:
                    cnt = 0
                    max_mat = -1
                    max_value = 0
                    for i in range(4):
                        if mat[i] > max_value:
                            max_value = mat[i]
                            max_mat = i

                    for i in range(5):
                        mat[i] = 0

                    ARD.write(str(max_mat+1).encode())
                    print("print", max_mat + 1)

                # Stream results
                if view_img:
                    cv2.imshow("video", im0)
                    if cv2.waitKey(1) == ord('q'):  # q to quit
                        raise StopIteration

                # Save results (image with detections)
                if save_img:
                    if dataset.mode == 'images':
                        cv2.imwrite(save_path, im0)
                    else:
                        if vid_path != save_path:  # new video
                            vid_path = save_path
                            if isinstance(vid_writer, cv2.VideoWriter):
                                vid_writer.release()  # release previous video writer

                            fourcc = 'mp4v'  # output video codec
                            fps = vid_cap.get(cv2.CAP_PROP_FPS)
                            w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            vid_writer = cv2.VideoWriter(
                                save_path, cv2.VideoWriter_fourcc(*fourcc), fps, (w, h))
                        vid_writer.write(im0)
        else:
            if view_img:
                cv2.imshow("video", im0s[0].copy())
                if cv2.waitKey(1) == ord('q'):  # q to quit
                    raise StopIteration

    # if save_txt or save_img:
    #     print('Results saved to %s' % Path(out))

    # print('Done. (%.3fs)' % (time.time() - t0))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str,
                        default='yolov5s.pt', help='model.pt path(s)')
    # file/folder, 0 for webcam
    parser.add_argument('--source', type=str,
                        default='inference/images', help='source')
    parser.add_argument('--img-size', type=int, default=640,
                        help='inference size (pixels)')
    parser.add_argument('--conf-thres', type=float,
                        default=0.25, help='object confidence threshold')
    parser.add_argument('--iou-thres', type=float,
                        default=0.45, help='IOU threshold for NMS')
    parser.add_argument('--device', default='',
                        help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', action='store_true',
                        help='display results')
    parser.add_argument('--save-txt', action='store_true',
                        help='save results to *.txt')
    parser.add_argument('--save-conf', action='store_true',
                        help='save confidences in --save-txt labels')
    parser.add_argument('--save-dir', type=str,
                        default='inference/output', help='directory to save results')
    parser.add_argument('--classes', nargs='+', type=int,
                        help='filter by class: --class 0, or --class 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true',
                        help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true',
                        help='augmented inference')
    parser.add_argument('--update', action='store_true',
                        help='update all models')
    opt = parser.parse_args()
    print(opt)

    with torch.no_grad():
        if opt.update:  # update all models (to fix SourceChangeWarning)
            for opt.weights in ['yolov5s.pt', 'yolov5m.pt', 'yolov5l.pt', 'yolov5x.pt']:
                detect()
                strip_optimizer(opt.weights)
        else:
            detect()
