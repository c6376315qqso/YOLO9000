"""YOLO_v2 Model Defined in Keras."""
import numpy as np
import tensorflow as tf
from keras import backend as K


def yolo_head(feats, anchors, num_classes, tree_):
    """Convert final layer features to bounding box parameters.

    Parameters
    ----------
    feats : tensor
        Final convolutional layer features.
    anchors : array-like
        Anchor box widths and heights.
    num_classes : int
        Number of target classes.

    Returns
    -------
    box_xy : tensor
        x, y box predictions adjusted by spatial location in conv layer.
    box_wh : tensor
        w, h box predictions adjusted by anchors and conv spatial resolution.
    box_conf : tensor
        Probability estimate for whether each box contains any object.
    box_class_pred : tensor
        Probability distribution estimate for each box over class labels.
    """
    num_anchors = len(anchors)
    # Reshape to batch, height, width, num_anchors, box_params.
    anchors_tensor = K.reshape(K.constant(anchors, name='anchor'), [1, 1, 1, num_anchors, 2])

    # Static implementation for fixed models.
    # TODO: Remove or add option for static implementation.
    # _, conv_height, conv_width, _ = K.int_shape(feats)
    # conv_dims = K.variable([conv_width, conv_height])

    # Dynamic implementation of conv dims for fully convolutional model.
    conv_dims = K.shape(feats)[1:3]  # assuming channels last
    # In YOLO the height index is the inner most iteration.
    conv_height_index = K.arange(0, stop=conv_dims[0])
    conv_width_index = K.arange(0, stop=conv_dims[1])
    conv_height_index = K.tile(conv_height_index, [conv_dims[1]])
    # conv_height_index是某一feats的左上角格子高度坐标

    # TODO: Repeat_elements and tf.split doesn't support dynamic splits.
    # conv_width_index = K.repeat_elements(conv_width_index, conv_dims[1], axis=0)

    conv_width_index = K.tile(
        K.expand_dims(conv_width_index, 0), [conv_dims[0], 1])
    conv_width_index = K.flatten(K.transpose(conv_width_index))
    # conv_width_index = K.tile(conv_width_index, [conv_dims[0]])

    conv_index = K.transpose(K.stack([conv_height_index, conv_width_index]))
    conv_index = K.reshape(conv_index, [1, conv_dims[0], conv_dims[1], 1, 2])
    conv_index = K.cast(conv_index, K.dtype(feats))
    feats = K.reshape(
        feats, [-1, conv_dims[0], conv_dims[1], num_anchors, num_classes + 5])

    conv_dims = K.cast(K.reshape(conv_dims, [1, 1, 1, 1, 2]), K.dtype(feats))

    box_xy = K.sigmoid(feats[..., :2])
    box_wh = K.exp(feats[..., 2:4])
    box_confidence = K.sigmoid(feats[..., 4:5])
    box_class_probs = K.concatenate([K.softmax(feats[..., 5 + tree_.group_offset[i]:
                                    5 + tree_.group_offset[i] + tree_.group_size[i]])
                                    for i in range(tree_.group_num)], axis=-1)

    # Adjust preditions to each spatial grid point and anchor size.
    # Note: YOLO iterates over height index before width index.
    # 在整张图的相对位置
    box_xy = (box_xy + conv_index) / conv_dims
    box_wh = box_wh * anchors_tensor / conv_dims

    return box_xy, box_wh, box_confidence, box_class_probs


def yolo_boxes_to_corners(box_xy, box_wh):
    """Convert YOLO box predictions to bounding box corners."""
    box_mins = box_xy - (box_wh / 2.)
    box_maxes = box_xy + (box_wh / 2.)

    return np.concatenate([
        box_mins[..., 1:2],  # y_min
        box_mins[..., 0:1],  # x_min
        box_maxes[..., 1:2],  # y_max
        box_maxes[..., 0:1]  # x_max
    ], axis=-1)


def yolo_filter_boxes(boxes, box_confidence, box_class_probs,
                      tree_, threshold=.3):
    box_scores = box_class_probs * box_confidence
    shap = box_scores.shape
    box_classes = np.random.rand(shap[0], shap[1], shap[2], shap[3])

    box_class_scores = np.random.rand(shap[0], shap[1], shap[2], shap[3])

    for i in range(shap[0]):
        for j in range(shap[1]):
            for k in range(shap[2]):
                for l in range(shap[3]):
                    box_classes[i][j][k][l], box_class_scores[i][j][k][l] = \
                        tree_.predict(box_scores[i][j][k][l], threshold)

    prediction_mask = box_class_scores >= 0

    # TODO: Expose tf.boolean_mask to Keras backend?
    boxes = boxes[prediction_mask]
    scores = box_class_scores[prediction_mask]
    classes = box_classes[prediction_mask]
    return boxes, scores, classes


def yolo_eval(yolo_outputs,
              image_shape,
              tree_,
              score_threshold=.3,
              ):
    box_xy, box_wh, box_confidence, box_class_probs = yolo_outputs
    boxes = yolo_boxes_to_corners(box_xy, box_wh)
    shap = box_class_probs.shape
    for i in range(shap[0]):
        for j in range(shap[1]):
            for k in range(shap[2]):
                for l in range(shap[3]):
                    tree_.process_true_prob(box_class_probs[i][j][k][l])

    boxes, scores, classes = yolo_filter_boxes(
        boxes, box_confidence, box_class_probs, threshold=score_threshold, tree_=tree_)

    height = image_shape[0]
    width = image_shape[1]
    image_dims = [height, width, height, width]
    image_dims = np.reshape(image_dims, [1, 4])
    boxes = boxes * image_dims
    return boxes, scores, classes


def yolo_final_val(boxes_tensor,
                   scores_tensor,
                   classes_tensor,
                   max_boxes=10,
                   score_threshold=.3,
                   iou_threshold=.5
                   ):
    max_boxes_tensor = K.constant(max_boxes, dtype='int32')
    print(iou_threshold, score_threshold)
    nms_index = tf.image.non_max_suppression(
        boxes_tensor, scores_tensor, max_boxes_tensor,
        iou_threshold=iou_threshold, score_threshold=score_threshold)
    boxes_tensor = K.gather(boxes_tensor, nms_index)
    scores_tensor = K.gather(scores_tensor, nms_index)
    classes_tensor = K.gather(classes_tensor, nms_index)
    return boxes_tensor, scores_tensor, classes_tensor


