#include "tensorflow/core/framework/op.h"
#include "tensorflow/core/framework/shape_inference.h"

using namespace tensorflow;

REGISTER_OP("DeepDot")
    .Input("origin: float")
    .Input("kernel: float")
    .Output("composed: float")
    .Attr("kernel_size: int")
    .SetShapeFn([](::tensorflow::shape_inference::InferenceContext* c) {
        c->set_output(0, c->input(0));
        return Status::OK();
    });

REGISTER_OP("GradDeepDot")
    .Input("grad_composed: float")
    .Input("origin: float")
    .Input("kernel: float")
    .Output("grad_origin: float")
    .Output("grad_kernel: float")
    .Attr("kernel_size: int")
    .SetShapeFn([](::tensorflow::shape_inference::InferenceContext* c) {
        c->set_output(0, c->input(1));
        c->set_output(1, c->input(2));
        return Status::OK();
    });