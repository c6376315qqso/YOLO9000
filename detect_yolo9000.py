import argparse
import colorsys
import imghdr
import os
import random
import tensorflow as tf

import numpy as np
from keras import backend as K
from keras.models import load_model
from PIL import Image, ImageDraw, ImageFont

from yad2k.utils.tree import tree
from yad2k.models.keras_yolo9000 import yolo_eval, yolo_head, yolo_final_val

model_path = os.path.expanduser('model_data/yolo9000.h5')
anchors_path = os.path.expanduser('model_data/yolo9000_anchors.txt')
classes_path = os.path.expanduser('yad2k/utils/9k.names')
tree_path = os.path.expanduser('yad2k/utils/9k.tree')
score_threshold = .12
iou_threshold = .4

yolo_model = load_model(model_path)

with open(classes_path) as f:
    class_names = f.readlines()
class_names = [c.strip() for c in class_names]

with open(anchors_path) as f:
    anchors = f.readline()
    anchors = [float(x) for x in anchors.split(',')]
    anchors = np.array(anchors).reshape(-1, 2)

tree_ = tree()
tree_.read_tree(tree_path)
model_image_size = yolo_model.layers[0].input_shape[1:3]
num_classes = len(class_names)
num_anchors = len(anchors)

# TODO: Assumes dim ordering is channel last
model_output_channels = yolo_model.layers[-1].output_shape[-1]
assert model_output_channels == num_anchors * (num_classes + 5), \
    'Mismatch between model and given anchor and class sizes. ' \
    'Specify matching anchors and classes with --anchors_path and ' \
    '--classes_path flags.'

# Check if model is fully convolutional, assuming channel last order.
is_fixed_size = model_image_size != (None, None)

# Generate colors for drawing bounding boxes.
hsv_tuples = [(x / len(class_names), 1., 1.)
              for x in range(len(class_names))]
colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
colors = list(
    map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)),
        colors))
random.seed(10101)  # Fixed seed for consistent colors across runs.
random.shuffle(colors)  # Shuffle colors to decorrelate adjacent classes.
random.seed(None)  # Reset seed to default.

# Generate output tensor targets for filtered bounding boxes.
# TODO: Wrap these backend operations with Keras layers.
yolo_outputs = yolo_head(yolo_model.output, anchors, len(class_names), tree_=tree_)
input_image_shape = K.placeholder(shape=(2,))
boxes_tensor = K.placeholder(dtype='float32')
scores_tensor = K.placeholder(dtype='float32')
classes_tensor = K.placeholder(dtype='int32')
boxes_val, scores_val, classes_val = yolo_final_val(boxes_tensor,
                                                    scores_tensor,
                                                    classes_tensor,
                                                    score_threshold=score_threshold,
                                                    iou_threshold=iou_threshold)


def detect9000(image):
    sess = K.get_session()  # TODO: Remove dependence on Tensorflow session.

    if is_fixed_size:  # TODO: When resizing we can use minibatch input.
        resized_image = image.resize(
            tuple(reversed(model_image_size)), Image.BICUBIC)
        image_data = np.array(resized_image, dtype='float32')
    else:
        # Due to skip connection + max pooling in YOLO_v2, inputs must have
        # width and height as multiples of 32.
        new_image_size = (image.width - (image.width % 32),
                          image.height - (image.height % 32))
        resized_image = image.resize(new_image_size, Image.BICUBIC)
        image_data = np.array(resized_image, dtype='float32')
        print(image_data.shape)
    image_data /= 255.
    image_data = np.expand_dims(image_data, 0)  # Add batch dimension.
    print("图像size:", image.size)

    yolo_outputs_val = sess.run(
        yolo_outputs,
        feed_dict={
            yolo_model.input: image_data
        })

    boxes, scores, classes = yolo_eval(
        yolo_outputs_val,
        (image.size[1], image.size[0]),
        tree_=tree_,
        score_threshold=score_threshold
    )

    out_boxes, out_scores, out_classes = sess.run([boxes_val, scores_val, classes_val],
                                                  feed_dict={
                                                      boxes_tensor: boxes,
                                                      scores_tensor: scores,
                                                      classes_tensor: classes
                                                  })

    font = ImageFont.truetype(
        font='font/FiraMono-Medium.otf',
        size=np.floor(3e-2 * image.size[1] + 0.5).astype('int32'))
    thickness = (image.size[0] + image.size[1]) // 300

    for i, c in reversed(list(enumerate(out_classes))):
        predicted_class = class_names[c]
        box = out_boxes[i]
        score = out_scores[i]

        label = '{} {:.2f}'.format(predicted_class, score)

        draw = ImageDraw.Draw(image)
        label_size = draw.textsize(label, font)

        top, left, bottom, right = box
        top = max(0, np.floor(top + 0.5).astype('int32'))
        left = max(0, np.floor(left + 0.5).astype('int32'))
        bottom = min(image.size[1], np.floor(bottom + 0.5).astype('int32'))
        right = min(image.size[0], np.floor(right + 0.5).astype('int32'))
        print(label, (left, top), (right, bottom))

        if top - label_size[1] >= 0:
            text_origin = np.array([left, top - label_size[1]])
        else:
            text_origin = np.array([left, top + 1])

        for i in range(thickness):
            draw.rectangle(
                [left + i, top + i, right - i, bottom - i],
                outline=colors[c])
        draw.rectangle(
            [tuple(text_origin), tuple(text_origin + label_size)],
            fill=colors[c])
        draw.text(text_origin, label, fill=(0, 0, 0), font=font)
        del draw
    return image

