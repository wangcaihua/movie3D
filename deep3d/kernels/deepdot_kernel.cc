#include "tensorflow/core/framework/op_kernel.h"
#include "tensorflow/core/platform/threadpool.h"

using namespace tensorflow;

class DeepDotOp : public OpKernel {
public:
    explicit DeepDotOp(OpKernelConstruction *context) : OpKernel(context) {
        OP_REQUIRES_OK(context, context->GetAttr("kernel_size", &kernel_size_));
    }

    void Compute(OpKernelContext *context) override {
        // Grab the input tensor
        const Tensor &origin_tensor = context->input(0);
        OP_REQUIRES(context, origin_tensor.dims() == 4,
                    errors::InvalidArgument("origin must be 4-dimensional",
                                            origin_tensor.shape().DebugString()));
        auto origin = origin_tensor.tensor<float, 4>();

        const Tensor &kernel_tensor = context->input(1);
        OP_REQUIRES(context, kernel_tensor.dims() == 4,
                    errors::InvalidArgument("kernel must be 4-dimensional",
                                            kernel_tensor.shape().DebugString()));
        auto kernel = kernel_tensor.tensor<float, 4>();

        OP_REQUIRES(context, origin_tensor.dim_size(0) == kernel_tensor.dim_size(0),
                    errors::InvalidArgument("origin and kernel must have identity batch_size",
                                            kernel_tensor.shape().DebugString()));

        OP_REQUIRES(context, kernel_tensor.dim_size(3) == kernel_size_ * kernel_size_,
                    errors::InvalidArgument("kernel_size not match",
                                            kernel_tensor.shape().DebugString()));

        // Create an output tensor
        Tensor *composed_tensor = nullptr;
        OP_REQUIRES_OK(context, context->allocate_output(0, origin_tensor.shape(), &composed_tensor));
        auto composed = composed_tensor->tensor<float, 4>();
        std::memset(composed.data(), 0, composed_tensor->TotalBytes());

        // resize the kernel to fit the origin
        double h_ = origin_tensor.dim_size(1) == kernel_tensor.dim_size(1) ? 1.0 : (
                1.0 * kernel_tensor.dim_size(1) / origin_tensor.dim_size(1));
        double w_ = origin_tensor.dim_size(2) == kernel_tensor.dim_size(2) ? 1.0 : (
                1.0 * kernel_tensor.dim_size(2) / origin_tensor.dim_size(2));
        auto rsh = [&h_](int x) { return (int) (x * h_); };
        auto rsw = [&w_](int x) { return (int) (x * w_); };

        int start = -kernel_size_ / 2;
        int end = kernel_size_ + start;
        int offset = -(kernel_size_ + 1) * start;

        for (int b = 0; b < origin_tensor.dim_size(0); ++b) {
            for (int h = 0; h < origin_tensor.dim_size(1); ++h) {
                for (int w = 0; w < origin_tensor.dim_size(2); ++w) {
                    for (int k = 0; k < origin_tensor.dim_size(3); ++k) {
                        for (int i = start; i < end; ++i) {  // height
                            for (int j = start; j < end; ++j) {  // width
                                if (h + i < 0 || h + i >= origin_tensor.dim_size(1) ||
                                    w + j < 0 || w + j >= origin_tensor.dim_size(2))
                                    continue;
                                int depth = kernel_size_ * i + j + offset;
                                composed(b, h, w, k) += origin(b, h + i, w + j, k) * kernel(b, rsh(h), rsw(w), depth);
                            }
                        }
                    }
                }
            }
        }
    }

private:
    int kernel_size_;
};


class GradDeepDotOp : public OpKernel {
public:
    explicit GradDeepDotOp(OpKernelConstruction *context) : OpKernel(context) {
        OP_REQUIRES_OK(context, context->GetAttr("kernel_size", &kernel_size_));
    }

    void Compute(OpKernelContext *context) override {
        // Grab the input tensor
        const Tensor &grad_composed = context->input(0);
        OP_REQUIRES(context, grad_composed.dims() == 4,
                    errors::InvalidArgument("grad must be 4-dimensional",
                                            grad_composed.shape().DebugString()));
        auto grad = grad_composed.tensor<float, 4>();

        const Tensor &origin_tensor = context->input(1);
        OP_REQUIRES(context, origin_tensor.shape() == grad_composed.shape(),
                    errors::InvalidArgument("shape of grad_composed and origin must the same"));
        auto origin = origin_tensor.tensor<float, 4>();

        const Tensor &kernel_tensor = context->input(2);
        OP_REQUIRES(context, kernel_tensor.dims() == 4,
                    errors::InvalidArgument("kernel must be 4-dimensional",
                                            kernel_tensor.shape().DebugString()));
        auto kernel = kernel_tensor.tensor<float, 4>();

        OP_REQUIRES(context, origin_tensor.dim_size(0) == kernel_tensor.dim_size(0),
                    errors::InvalidArgument("origin and kernel must have identity batch_size",
                                            kernel_tensor.shape().DebugString()));
        OP_REQUIRES(context, origin_tensor.dim_size(1) == kernel_tensor.dim_size(1),
                    errors::InvalidArgument("origin and kernel must have identity height",
                                            kernel_tensor.shape().DebugString()));
        OP_REQUIRES(context, origin_tensor.dim_size(2) == kernel_tensor.dim_size(2),
                    errors::InvalidArgument("origin and kernel must have identity width",
                                            kernel_tensor.shape().DebugString()));
        OP_REQUIRES(context, kernel_tensor.dim_size(3) == kernel_size_ * kernel_size_,
                    errors::InvalidArgument("kernel_size not match",
                                            kernel_tensor.shape().DebugString()));

        // Create the output tensor
        Tensor *grad_origin_tensor = nullptr;
        OP_REQUIRES_OK(context, context->allocate_output(0, origin_tensor.shape(), &grad_origin_tensor));
        auto grad_origin = grad_origin_tensor->tensor<float, 4>();
        std::memset(grad_origin.data(), 0, grad_origin_tensor->TotalBytes());

        Tensor *grad_kernel_tensor = nullptr;
        OP_REQUIRES_OK(context, context->allocate_output(1, kernel_tensor.shape(), &grad_kernel_tensor));
        auto grad_kernel = grad_kernel_tensor->tensor<float, 4>();
        std::memset(grad_kernel.data(), 0, grad_kernel_tensor->TotalBytes());

        int start = -kernel_size_ / 2;
        int end = kernel_size_ + start;
        int offset = -(kernel_size_ + 1) * start;

        // context->device()->tensorflow_cpu_worker_threads()->workers->Schedule()
        for (int b = 0; b < origin_tensor.dim_size(0); ++b) {
            for (int h = 0; h < origin_tensor.dim_size(1); ++h) {
                for (int w = 0; w < origin_tensor.dim_size(2); ++w) {
                    for (int k = 0; k < origin_tensor.dim_size(3); ++k) {
                        float grad_hwk = grad(b, h, w, k);
                        for (int i = start; i < end; ++i) {  // height
                            for (int j = start; j < end; ++j) {  // width
                                if (h + i < 0 || h + i >= origin_tensor.dim_size(1) ||
                                    w + j < 0 || w + j >= origin_tensor.dim_size(2))
                                    continue;
                                int depth = kernel_size_ * i + j + offset;

                                grad_origin(b, h + i, w + j, k) += kernel(b, h, w, depth) * grad_hwk;
                                grad_kernel(b, h, w, depth) += origin(b, h + i, w + j, k) * grad_hwk;
                            }
                        }
                    }
                }
            }
        }
    }

private:
    int kernel_size_;
};


REGISTER_KERNEL_BUILDER(Name("DeepDot").Device(DEVICE_CPU), DeepDotOp);

REGISTER_KERNEL_BUILDER(Name("GradDeepDot").Device(DEVICE_CPU), GradDeepDotOp);
