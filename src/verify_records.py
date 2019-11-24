import tensorflow as tf

for example in tf.python_io.tf_record_iterator("output/train.record"):
    print(tf.train.Example.FromString(example))
    break
