import onnxruntime as ort

ort_sess = ort.InferenceSession("model1.onnx", providers = ['CPUExecutionProvider'])
print(ort_sess.device_name())