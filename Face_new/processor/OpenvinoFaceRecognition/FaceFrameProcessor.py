from openvino.inference_engine import IECore
from processor.OpenvinoFaceRecognition.face_detector import FaceDetector
from processor.OpenvinoFaceRecognition.face_identifier import FaceIdentifier
from processor.OpenvinoFaceRecognition.faces_database import FacesDatabase
from processor.OpenvinoFaceRecognition.landmarks_detector import LandmarksDetector


class FrameProcessor:
    QUEUE_SIZE = 16

    def __init__(self, args):
        ie = IECore()

        if args.cpu_lib and 'CPU' in {args.d_fd, args.d_lm, args.d_reid}:
            ie.add_extension(args.cpu_lib, 'CPU')
        self.face_detector = FaceDetector(ie, args.m_fd,
                                          args.fd_input_size,
                                          confidence_threshold=args.t_fd,
                                          roi_scale_factor=args.exp_r_fd)

        self.landmarks_detector = LandmarksDetector(ie, args.m_lm)
        self.face_identifier = FaceIdentifier(ie, args.m_reid,
                                              match_threshold=args.t_id,
                                              match_algo=args.match_algo)

        self.face_detector.deploy(args.d_fd, self.get_config(args.d_fd))
        self.landmarks_detector.deploy(args.d_lm, self.get_config(args.d_lm), self.QUEUE_SIZE)
        self.face_identifier.deploy(args.d_reid, self.get_config(args.d_reid), self.QUEUE_SIZE)
        # self.agegender_detector.deploy(args.d_ag, self.get_config(args.d_ag))
        self.faces_database = FacesDatabase(args.fg, self.face_identifier,
                                            self.landmarks_detector,
                                            self.face_detector if args.run_detector else None)
        self.face_identifier.set_faces_database(self.faces_database)

    def get_config(self, device):
        config = {}
        return config

    def process(self, frame):
        rois = self.face_detector.infer((frame,))
        if self.QUEUE_SIZE < len(rois):
            rois = rois[:self.QUEUE_SIZE]
        landmarks = self.landmarks_detector.infer((frame, rois))
        face_identities, unknowns = self.face_identifier.infer((frame, rois, landmarks))
        return [rois, landmarks, face_identities]
