import tensorflow as tf
import yaml
import os
import dataset_utils


flags = tf.app.flags
flags.DEFINE_string('output_path', '', 'Path to output TFRecord')
FLAGS = flags.FLAGS

LABEL_DICT_14 =  {
    "Green" : 1,
    "Red" : 2,
    "GreenLeft" : 3,
    "GreenRight" : 4,
    "RedLeft" : 5,
    "RedRight" : 6,
    "Yellow" : 7,
    "off" : 8,
    "RedStraight" : 9,
    "GreenStraight" : 10,
    "GreenStraightLeft" : 11,
    "GreenStraightRight" : 12,
    "RedStraightLeft" : 13,
    "RedStraightRight" : 14
    }

LABEL_DICT_4 =  {
    "Green" : 1,
    "Red" : 2,
    "Yellow" : 3,
    "off" : 4,
    }

# create the tensorflow binary training records for retraining of pretrained models
# we are using the object detection API from tensorflow for retraining
# see also following links:
# https://github.com/tensorflow/models/tree/master/research/object_detection
# https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md
# https://towardsdatascience.com/how-to-train-your-own-object-detector-with-tensorflows-object-detector-api-bec72ecfe1d9
def create_tf_example(example):
    
    # Udacity simulation data image format from Unity simulator of term 3 final integration project
    # Files can be downloaded from ??? (Link from @zika)
    height = 600 # Image height
    width = 800 # Image width

    filename = example['path'] # Filename of the image. Empty if image is not from file
    filename = filename.encode()

    with tf.gfile.GFile(example['path'], 'rb') as fid:
        encoded_image = fid.read()

    image_format = 'png'.encode() 

    xmins = [] # List of normalized left x coordinates in bounding box (1 per box)
    xmaxs = [] # List of normalized right x coordinates in bounding box
                # (1 per box)
    ymins = [] # List of normalized top y coordinates in bounding box (1 per box)
    ymaxs = [] # List of normalized bottom y coordinates in bounding box
                # (1 per box)
    classes_text = [] # List of string class name of bounding box (1 per box)
    classes = [] # List of integer class id of bounding box (1 per box)

    for box in example['boxes']:
        #if box['occluded'] is False:
        #print("adding box")
        xmins.append(float(box['x_min'] / width))
        xmaxs.append(float(box['x_max'] / width))
        ymins.append(float(box['y_min'] / height))
        ymaxs.append(float(box['y_max'] / height))
        classes_text.append(box['label'].encode())
        classes.append(int(LABEL_DICT_4[box['label']]))


    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_utils.int64_feature(height),
        'image/width': dataset_utils.int64_feature(width),
        'image/filename': dataset_utils.bytes_feature(filename),
        'image/source_id': dataset_utils.bytes_feature(filename),
        'image/encoded': dataset_utils.bytes_feature(encoded_image),
        'image/format': dataset_utils.bytes_feature(image_format),
        'image/object/bbox/xmin': dataset_utils.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_utils.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_utils.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_utils.float_list_feature(ymaxs),
        'image/object/class/text': dataset_utils.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_utils.int64_list_feature(classes),
    }))

    return tf_example


def main(_):
    print('fff ' ,FLAGS.output_path)
    
    writer = tf.python_io.TFRecordWriter(FLAGS.output_path + os.sep + "tf_train_udacity_simdata.record")
    
    # Udacity simulation labeling file - here hardcoded.....
    # Files can be downloaded from ??? (Link from @zika)
    INPUT_YAML = "udacity_simdata_train.yaml"
    examples = yaml.load(open(INPUT_YAML, 'rb').read())

    #examples = examples[:10]  # for testing
    len_examples = len(examples)
    print("Loaded ", len(examples), "examples")

    for i in range(len(examples)):
        examples[i]['path'] = os.path.abspath(os.path.join(os.path.dirname(INPUT_YAML), examples[i]['path']))
    
    counter = 0
    for example in examples:
        tf_example = create_tf_example(example)
        writer.write(tf_example.SerializeToString())

        if counter % 10 == 0:
            print("Percent done", (counter/len_examples)*100)
        counter += 1

        #print(example['path'])

    writer.close()



if __name__ == '__main__':
    tf.app.run()