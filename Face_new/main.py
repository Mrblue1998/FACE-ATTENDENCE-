import cv2
import json
from processor.OpenvinoFaceRecognition.face_build_argparser import *
from processor.OpenvinoFaceRecognition.FaceFrameProcessor import *
from face_recognitions import *
from processor.__DatabaseLayer__ import DataAccess
import streamlit as st
from flask import Flask, Response,request
import cv2

app = Flask(__name__)

data_set = r"face_dataset"
reid_path = r"model_files\face-reidentification-retail-0095\FP16\face-reidentification-retail-0095.xml"
detect_face = r"model_files\face-detection-adas-0001\FP16\face-detection-adas-0001.xml"
land_detect = r"model_files\landmarks-regression-retail-0009\FP16\landmarks-regression-retail-0009.xml"
openvino_process_device = 'CPU'
face_reid_threshold = 0.18
face_args = build_argparser(None, detect_face, land_detect, reid_path, data_set, None, openvino_process_device,
                            face_reid_threshold).parse_args()
face_frame_processor = FrameProcessor(face_args)
face_frame_num = 0
face_presenter = None
face_output_transform = None
person_history = {}
cam_name = 'feed1'
face_path = r'C:\Users\91984\Downloads\Face_new\Output_faces'

# define a video capture object

DataAccess.db_details()


def face_attendence(video_path):
    vid = cv2.VideoCapture(video_path)
    while (True):
        stframe = st.empty()
        ret, frame = vid.read()
        img_h, img_w, _ = frame.shape
        frame, presenter, output_transform, face_detect_flag, face_image_original_path = attendance_face_identifier_main(
            frame, face_frame_num,
            face_frame_processor, face_presenter,
            face_output_transform, face_args, cam_name, img_h, img_w, face_path)
        for face_crop, name, file_name in face_image_original_path:
            if name != "Unknown":
                cur_date = datetime.datetime.now()
                attendance_db_data = DataAccess.get_attendance_data_by_date(cur_date)
                if attendance_db_data:
                    attendance_blob = attendance_db_data["person_details"]
                else:
                    DataAccess.insert_attendance(cur_date)
                    attendance_blob = None
                time_data = json.loads(attendance_blob) if attendance_blob else {}
                if name not in time_data.keys():
                    time_data[name] = [[datetime.datetime.now().strftime("%H:%M:%S"), file_name]]
                    time_data_blob = json.dumps(time_data)
                    DataAccess.update_attendance(cur_date, time_data_blob)
                today_date = datetime.datetime.now().date()
                last_seen = datetime.datetime.combine(today_date,
                                                      datetime.datetime.strptime(
                                                          time_data[name][-1][0],
                                                          "%H:%M:%S").time())
                if (datetime.datetime.now() - last_seen).seconds > 30:
                    time_data[name].append(
                        [datetime.datetime.now().strftime("%H:%M:%S"), file_name])
                    time_data_blob = json.dumps(time_data)
                    DataAccess.update_attendance(cur_date, time_data_blob)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        # Yield frame to be displayed as part of an HTTP response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    # Get the video source from the query string (default to 0 if not provided)
    video_source = request.args.get('source', default=0, type=str)

    if video_source.isdigit():
        video_source = int(video_source)  # Convert to integer if it's a webcam index

    return Response(face_attendence(video_source), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)
