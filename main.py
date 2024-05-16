import argparse
import cv2
from paddleocr import PaddleOCR


def get_text(ocr, frame, top, bottom, width):
    cropped_frame = frame[top:bottom, 0:width]
    result = ocr.ocr(cropped_frame, cls=False)
    text_arr = []
    for item in result:
        if item:
            for part in item:
                if part:
                    text_arr.append(part[1][0])
    return " ".join(text_arr)


def extract(ocr, path, top, bottom):
    cap = cv2.VideoCapture(path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    num = 1
    interval = int(fps / 3)

    info = {
        "fps": fps,
        "total_frame": total_frames,
        "list": [],
    }

    while num < total_frames:
        ret, frame = cap.read()
        if not ret:
            break

        cur_text = get_text(ocr=ocr, frame=frame, top=top, bottom=bottom, width=width)
        if num > 1:
            pre = info["list"][-1]
            if pre["result"] != cur_text:
                if pre["result"]:
                    for i in range(interval - 1):
                        find_last = num - interval + i + 1
                        cap.set(cv2.CAP_PROP_POS_FRAMES, find_last)
                        ret, frame = cap.read()
                        temp_text = get_text(
                            ocr=ocr, frame=frame, top=top, bottom=bottom, width=width
                        )
                        if temp_text == pre["result"]:
                            pre["end"] = find_last
                        else:
                            break
                if cur_text:
                    pre_index = num
                    for j in range(interval - 1):
                        find_pre = num - j - 1
                        cap.set(cv2.CAP_PROP_POS_FRAMES, find_pre)
                        ret, frame = cap.read()
                        temp_text = get_text(
                            ocr=ocr, frame=frame, top=top, bottom=bottom, width=width
                        )
                        if temp_text == cur_text:
                            pre_index = find_pre
                        else:
                            break
                    info["list"].append(
                        {"start": pre_index, "end": num, "result": cur_text}
                    )
                else:
                    info["list"].append({"start": num, "end": num, "result": cur_text})
            else:
                pre["end"] = num
        else:
            info["list"].append({"start": num, "end": num, "result": cur_text})

        num += interval
        cap.set(cv2.CAP_PROP_POS_FRAMES, num)

    cap.release()
    return info


def generate_srt(subtitle_list, fps):
    srt_lines = []
    current_index = 1

    for subtitle in subtitle_list:
        start_frame = subtitle.get("start", 0)
        end_frame = subtitle.get("end", 0)
        subtitle_text = subtitle.get("result", "")

        if subtitle_text == "":
            continue

        start_time = round(start_frame / fps, 3)
        end_time = round(end_frame / fps, 3)

        start_time_srt = time_to_srt(start_time)
        end_time_srt = time_to_srt(end_time)

        srt_lines.append(f"{current_index}\n")
        srt_lines.append(f"{start_time_srt} --> {end_time_srt}\n")
        srt_lines.append(f"{subtitle_text}\n")
        srt_lines.append("\n")
        current_index += 1

    srt_content = "".join(srt_lines)
    return srt_content


def time_to_srt(time_seconds):
    milliseconds = int(round(time_seconds * 1000) % 1000)
    time_seconds = int(time_seconds)
    minutes, seconds = divmod(time_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def main():
    parser = argparse.ArgumentParser(description="subtitle extract")

    parser.add_argument("-p", "--path", required=True, help="视频文件路径")
    parser.add_argument("-t", "--top", required=True, type=int, help="字幕区域的顶部")
    parser.add_argument(
        "-b", "--bottom", required=True, type=int, help="字幕区域的底部"
    )

    args = parser.parse_args()

    ocr = PaddleOCR(
        use_angle_cls=False,
        lang="ch",
        rec_model_dir="https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/ch_PP-OCRv4_rec_server_infer.tar",
    )

    data = extract(ocr=ocr, path=args.path, top=args.top, bottom=args.bottom)
    srt = generate_srt(data["list"], data["fps"])

    with open("res.srt", "w", encoding="utf-8") as file:
        file.write(srt)


if __name__ == "__main__":
    main()
