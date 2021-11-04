#include "tensorflow/core/framework/op.h"


REGISTER_OP("DeepDot")
    .Input(": int32")
    .Input(": int32")
    .Output("custom_output: int32");
