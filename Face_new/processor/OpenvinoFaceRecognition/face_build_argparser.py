from argparse import ArgumentParser
from pathlib import Path

DEVICE_KINDS = ['CPU', 'GPU']


def resolution(value):
    try:
        result = [int(v) for v in value.split('x')]
        if len(result) != 2:
            raise RuntimeError('correct format of --output_resolution parameter is "width"x"height".')
    except ValueError:
        raise RuntimeError('correct format of --output_resolution parameter is "width"x"height".')
    return result


def build_argparser(stream_url, face_detector_model, face_recognition_model, face_validator_model,
                    trained_images, age_gender_model, device, t_reid):
    parser = ArgumentParser()
    general = parser.add_argument_group('General')
    general.add_argument('-i', '--input', required=False, default=stream_url,
                         help='Required. An input to process. The input must be a single image, '
                              'a folder of images, video file or camera id.')
    general.add_argument('--output_resolution', default=None, type=resolution,
                         help='Optional. Specify the maximum output window resolution '
                              'in (width x height) format. Example: 1280x720. '
                              'Input frame size used by default.')
    general.add_argument('--crop_size', default=(0, 0), type=int, nargs=2,
                         help='Optional. Crop the input stream to this resolution.')
    general.add_argument('--match_algo', default='HUNGARIAN', choices=('HUNGARIAN', 'MIN_DIST'),
                         help='Optional. Algorithm for face matching. Default: HUNGARIAN.')
    general.add_argument('-u', '--utilization_monitors', default='', type=str,
                         help='Optional. List of monitors to show initially.')

    gallery = parser.add_argument_group('Faces database')
    gallery.add_argument('-fg', default=trained_images, help='Optional. Path to the face images directory.')
    gallery.add_argument('--run_detector', action='store_true',
                         help='Optional. Use Face Detection model to find faces '
                              'on the face images, otherwise use full images.')
    models = parser.add_argument_group('Models')
    models.add_argument('-m_fd', type=Path, required=False, default=face_detector_model,
                        help='Required. Path to an .xml file with Face Detection model.')
    models.add_argument('-m_lm', type=Path, required=False, default=face_recognition_model,
                        help='Required. Path to an .xml file with Facial Landmarks Detection model.')
    models.add_argument('-m_reid', type=Path, required=False, default=face_validator_model,
                        help='Required. Path to an .xml file with Face Reidentification model.')
    models.add_argument('-m_ag', type=Path, required=False, default=age_gender_model,
                        help='Required. Path to an .xml file with Age Gender Detection model.')
    models.add_argument('--fd_input_size', default=(720, 1280), type=int, nargs=2,
                        help='Optional. Specify the input size of detection model for '
                             'reshaping. Example: 500 700.')

    infer = parser.add_argument_group('Inference options')
    infer.add_argument('-d_fd', default=device, choices=DEVICE_KINDS,
                       help='Optional. Target device for Face Detection model. '
                            'Default value is CPU.')
    infer.add_argument('-d_lm', default=device, choices=DEVICE_KINDS,
                       help='Optional. Target device for Facial Landmarks Detection '
                            'model. Default value is CPU.')
    infer.add_argument('-d_reid', default=device, choices=DEVICE_KINDS,
                       help='Optional. Target device for Face Reidentification '
                            'model. Default value is CPU.')
    infer.add_argument('-d_ag', default=device, choices=DEVICE_KINDS,
                       help='Optional. Target device for Age Gender Detection model. '
                            'Default value is CPU.')
    infer.add_argument('-l', '--cpu_lib', metavar="PATH", default='',
                       help='Optional. For MKLDNN (CPU)-targeted custom layers, '
                            'if any. Path to a shared library with custom '
                            'layers implementations.')
    infer.add_argument('-t_fd', metavar='[0..1]', type=float, default=0.7,
                       help='Optional. Probability threshold for face detections.')
    infer.add_argument('-t_id', metavar='[0..1]', type=float, default=t_reid,
                       help='Optional. Cosine distance threshold between two vectors '
                            'for face identification.')
    infer.add_argument('-exp_r_fd', metavar='NUMBER', type=float, default=1.35,
                       help='Optional. Scaling ratio for bboxes passed to face recognition.')
    return parser
