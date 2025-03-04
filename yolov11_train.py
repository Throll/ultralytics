import warnings
warnings.filterwarnings('ignore')
from ultralytics import YOLO
# import os

# os.environ["CUDA_VISIBLE_DEVICES"] = "1"
           
if __name__ == '__main__':
	model = YOLO('ultralytics/cfg/models/11/yolo11m.yaml')   # 修改yaml
	model.load('yolo11m.pt')  #加载预训练权重
	model.train(data='data.yaml',   #数据集yaml文件
	            imgsz=640,
	            epochs=300,
	            batch=8,
	            workers=16,
	            device="cuda:1",   #没显卡则将0修改为'cpu'
	            optimizer='SGD',
                amp = False,
	            cache=False,   #服务器可设置为True，训练速度变快
                patience=50,
                conf=0.5,
				lr0=0.001
	)