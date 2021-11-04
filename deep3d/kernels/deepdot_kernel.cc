#include "tensorflow/core/framework/op_kernel.h"

namespace tensorflow {
class CustomOp : public OpKernel{
    public:
        explicit CustomOp(OpKernelConstruction* context) : OpKernel(context) {}
        void Compute(OpKernelContext* context) override {
            // 获取输入 tensor.
            const Tensor& input_tensor = context->input(0);
            auto input = input_tensor.flat<int32>();
            // 创建一个输出 tensor.
            Tensor* output_tensor = nullptr;
            OP_REQUIRES_OK(context, context->allocate_output(0, input_tensor.shape(),
                                                             &output_tensor));
            auto output = output_tensor->template flat<int32>();
            //进行具体的运算，操作input和output
            //……
        }
};

REGISTER_KERNEL_BUILDER(Name("Custom").Device(DEVICE_CPU), CustomOp);
}  // namespace tensorflow


