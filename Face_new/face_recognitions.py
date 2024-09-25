import datetime
import cv2
import numpy as np
# from processor.logger import trace, exc
from common import FolderView
from multiprocessing.pool import ThreadPool
from utils1 import OutputTransform
import monitors

face_pool = ThreadPool(processes=10)
annotation_list = []


def draw_detections(frame, frame_processor, detections, output_transform, img_h, img_w,face_path):
    try:
        global annotation_list
        fra = frame.copy()
        size = frame.shape[:2]
        frame = output_transform.resize(frame)
        face_ids_paths = []
        original_path = face_path + '/Original'
        detected_face_path = face_path + '/Detected_face/'
        unknown_face_path = face_path + '/Unknown_faces/'
        detected_face_date_path = detected_face_path + str(datetime.datetime.now().strftime("%d_%m_%Y"))
        unknown_face_date_path = unknown_face_path + str(datetime.datetime.now().strftime("%d_%m_%Y"))
        face_image_original_path = original_path + "/FaceDetection{}.jpeg".format(
            str(datetime.datetime.now().strftime("%d%m%Y%H%M%S")))
        face_image_path = face_path + "/FaceDetection{}.jpeg".format(
            str(datetime.datetime.now().strftime("%d%m%Y%H%M%S")))
        for roi, landmarks, identity in zip(*detections):
            text = frame_processor.face_identifier.get_identity_label(identity.id)
            name = text.split("_")
            xmin = max(int(roi.position[0]), 0)
            ymin = max(int(roi.position[1]), 0)
            xmax = min(int(roi.position[0] + roi.size[0]), size[1])
            ymax = min(int(roi.position[1] + roi.size[1]), size[0])
            xmin, ymin, xmax, ymax = output_transform.scale([xmin, ymin, xmax, ymax])

            crp = fra[ymin:ymax, xmin:xmax]
            FolderView(face_path).createfolder()
            FolderView(original_path).createfolder()
            FolderView(detected_face_path).createfolder()
            FolderView(detected_face_date_path).createfolder()
            FolderView(unknown_face_path).createfolder()
            FolderView(unknown_face_date_path).createfolder()
            # if elasticsearch_flag:
            #     SearchEngine().engine_data(usr_id, cam_name, "Person", "FaceDetection",
            #                       str(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")), text, age,
            #                       gender,
            #                       face_image_path, person_name_age_gender, "",
            #                       face_image_original_path, "",
            #                       "True",
            #                       str(datetime.datetime.now().strftime("%H:%M:%S")),
            #                       [])

            org_h, org_w, _ = frame.shape

            xmin = int(xmin * img_w / org_w)
            ymin = int(ymin * img_h / org_h)
            xmax = int(xmax * img_w / org_w)
            ymax = int(ymax * img_h / org_h)

            if text != "Unknown":
                person_face_crop_path = detected_face_date_path + '/' + name[0] + "@{}.jpeg".format(
                    str(datetime.datetime.now().strftime("%H%M%S%f")))
                cv2.imwrite(person_face_crop_path, crp, [cv2.IMWRITE_JPEG_QUALITY,90])

                face_ids_paths.append((crp, name[0], person_face_crop_path))
                # annotation_list.append(
                #     (cv2.putText, (name[0], (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1)))
                # annotation_list.append((cv2.rectangle, ((xmin, ymin), (xmax, ymax), (0, 225, 0), 1)))
                cv2.putText(frame,name[0], (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 1)
                cv2.rectangle(frame,(xmin, ymin), (xmax, ymax), (0, 225, 0), 1)

            else:
                person_face_crop_path = unknown_face_date_path + '/' + name[0] + "@{}.jpeg".format(
                    str(datetime.datetime.now().strftime("%H%M%S%f")))
                cv2.imwrite(person_face_crop_path, crp, [cv2.IMWRITE_JPEG_QUALITY,90])
                face_ids_paths.append((crp, name[0], person_face_crop_path))
                # annotation_list.append((cv2.rectangle, ((xmin, ymin), (xmax, ymax), (0, 0, 255), 1)))
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 0, 255), 1)


        return frame, fra, face_ids_paths
    except Exception as ex:
        print(f"Error in draw_detections function in attendance face recognition: {ex}")


def attendance_face_identifier_main(face_rec_queue, frame_num, frame_processor, presenter, output_transform, args, cam_name, img_h, img_w,face_path):
    try:
        global annotation_list
        frame = face_rec_queue
        # annotation_list = []
        face_detect_flag = False
        if frame_num == 0:
            output_transform = OutputTransform(frame.shape[:2], args.output_resolution)
            output_resolution = (frame.shape[1], frame.shape[0])
            presenter = monitors.Presenter(args.utilization_monitors, 55,
                                           (round(output_resolution[0] / 4), round(output_resolution[1] / 8)))
        detections = frame_processor.process(frame)
        if detections[0]:
            face_detect_flag = True
        presenter.drawGraphs(frame)
        face_ret_value = face_pool.apply_async(draw_detections, (frame, frame_processor, detections,
                                                                 output_transform, img_h, img_w,face_path))
        face_ret = face_ret_value.get()
        frame = face_ret[0]
        # face_image_path = face_ret[1]
        face_image_original_path = face_ret[2]
        # face_ids_paths = face_ret[4]
        return frame, presenter, output_transform, face_detect_flag,face_image_original_path
    except Exception as ex:
        print(f'Error Occurred in Face Recognition {ex} in camera name {cam_name}')
