import glob
import numpy as np
from annoy import AnnoyIndex
from keras.utils.data_utils import get_file

FEATURES_NUMBER = 1000
ANNOY_INDEX = AnnoyIndex(FEATURES_NUMBER, metric='euclidean')

lfh = open("labels.ann", "w")

INDOOR_IMAGES_URL = 'https://s3-us-west-2.amazonaws.com/kaggleglm/train_indoor.txt'
INDOOR_IMAGES_PATH = get_file(
    'train_indoor.txt',
    INDOOR_IMAGES_URL,
    cache_subdir='models',
    file_hash='a0ddcbc7d0467ff48bf38000db97368e')
indoor_images = set(open(INDOOR_IMAGES_PATH, 'r').read().splitlines())

files = glob.glob("features/AXception-cs256/*.npy")
i = 0
for file_name in files:
    vectors = np.load(file_name)
    train_id = file_name.split('/')[-1].split('.')[0]
    if len(train_id) == 16:
        continue
    if train_id in indoor_images:
        continue

    label = int(file_name.split('/')[-1].split('.')[0])
    for j in range(len(vectors)):
        lfh.write("%s %s\n" % (i, label))
        ANNOY_INDEX.add_item(i, vectors[j][:FEATURES_NUMBER])
        i = i + 1
        if i % 200000 == 0:
            ANNOY_INDEX.build(1000)
            ANNOY_INDEX.save('index.ann.%s' % int(i/200000))
            ANNOY_INDEX = AnnoyIndex(FEATURES_NUMBER, metric='euclidean')

files = glob.glob("features_retrieval/AXception-cs256/*.npy")
for file_name in files:
    vector = np.load(file_name)
    label = -1
    lfh.write("%s %s\n" % (i, label))
    ANNOY_INDEX.add_item(i, vector[:FEATURES_NUMBER])
    i = i + 1
    if i % 200000 == 0:
        ANNOY_INDEX.build(1000)
        ANNOY_INDEX.save('index.ann.%s' % int(i/200000))                                                                                                             
        ANNOY_INDEX = AnnoyIndex(FEATURES_NUMBER, metric='euclidean')


ANNOY_INDEX.build(1000)
ANNOY_INDEX.save('index.ann.%s' % (int(i/200000)+1))
lfh.close()
