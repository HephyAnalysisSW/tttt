import  numpy as np
import onnxruntime as ort

model = '/groups/hephy/cms/lena.wild/tttt/models/TTTT_MS_mean_ctt_epochs-10000_hs1-80_hs2-45_hsc-5_lstm-1_hs-lstm-1'

X = np.zeros((1,40))
V = np.zeros((1,10,4))

options = ort.SessionOptions()
options.inter_op_num_threads = 1    

 
ort_sess = ort.InferenceSession(model+'.onnx',  sess_options=options, providers = ['CPUExecutionProvider'])
val = ort_sess.run(["output1"], {"input1": X.astype(np.float32),"input2": V.astype(np.float32)})[0][0] 
print (val)    