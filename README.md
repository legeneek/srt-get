# srt-get

视频中文硬字幕提取命令行工具，基于[PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)实现，生成 srt 文件

# 使用

## 1.安装

安装 PaddlePaddle 及 PaddleOCR whl 包，[参考文档](https://github.com/PaddlePaddle/PaddleOCR/blob/main/doc/doc_ch/quickstart.md)

安装 opencv_python

```shell
pip install opencv-python
```

## 2.运行

测试运行 python 版本为 3.11，使用 cpu 运行
-p 设置视频文件路径
-t 设置字幕区域的上边界高度，如：视频分辨率高为 1920，上边界高 1400
-b 设置字幕区域的下边界高度

确定字幕区域的上下边界后运行下面指令，结果将保存到 res.srt

```shell
python main.py -p video_path.mp4 -t 1400 -b 1800
```

# 注意

固定使用 ch_PP-OCRv4_rec_server_infer 这个高精度版本，速度较慢但稳定性好，需要替换模型或语言可以调整 PaddleOCR 的参数实现

```python
ocr = PaddleOCR(
        use_angle_cls=False,
        lang="ch",
        rec_model_dir="https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/ch_PP-OCRv4_rec_server_infer.tar",
    )
```

工具尽量保证时间轴的准确，不过模型识别可能有误，得到的 srt 文件仍需要校对
