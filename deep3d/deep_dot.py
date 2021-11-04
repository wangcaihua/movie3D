import tensorflow as tf


decode_param_op_module = tf.load_op_library('deep_dot.so')


def decode_with_param(inputs, sequence_length, beam_width=100,
                   top_paths=1, merge_repeated=True):
    decoded_ixs, decoded_vals, decoded_shapes, log_probabilities = (
        decode_param_op_module.ctc_beam_search_decoder_with_param(
            inputs, sequence_length, beam_width=beam_width,
            top_paths=top_paths, merge_repeated=merge_repeated,
            label_selection_size=40, label_selection_margin=0.99))
    return (
        [tf.SparseTensor(ix, val, shape) for (ix, val, shape)
         in zip(decoded_ixs, decoded_vals, decoded_shapes)],
        log_probabilities)