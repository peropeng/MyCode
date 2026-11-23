"""Restore the frozen inference policy in a fresh process before any159 outputs."""
from common import *
import models159 as models
import predict159
import torch

def run():
 require_time(new_long_task=True)
 seal=read(E/'prediction_runtime_entry_sealed.json')
 if seal['entry_sha256']!=sha(__file__) or seal['prediction_source_sha256']!=sha(E/'predict159.py') or seal['protocol_sha256']!=sha(E/'protocol.json'):raise RuntimeError('Frozen prediction runtime entry changed')
 if (E/'physical_generation_events.jsonl').exists() or (E/'label_join_started.json').exists():raise RuntimeError('Runtime entry must precede every new prediction and target label join')
 models.seed_all(0);actual=models.backend_policy()
 if actual!=EXPECTED_BACKEND or torch.get_default_dtype()!=torch.float32:raise RuntimeError('Frozen FP32/deterministic/noTF32/threads4 inference policy not restored')
 write_new(E/'prediction_runtime_receipt.json',{'at_utc':now(),'status':'PASS','protocol_sha256':sha(E/'protocol.json'),'entry_path':str(Path(__file__).resolve()),'entry_sha256':sha(__file__),'entry_seal_sha256':sha(E/'prediction_runtime_entry_sealed.json'),'prediction_source_sha256':sha(E/'predict159.py'),'actual_runtime_backend_policy':actual,'expected_runtime_backend_policy':EXPECTED_BACKEND,'initialization_seed_for_inference_only':0,'torch_default_dtype':str(torch.get_default_dtype()),'prediction_outputs_before_entry':0,'target_label_values_before_entry':0,'new_model_fits_or_forwards_for_policy_restoration':0,'frozen_training_or_prediction_sources_modified':False,'reason':'Fresh inference process does not inherit trainer flags; use exact158 seed_all(0) policy before159 predictor without changing sealed training protocol.'})
 predict159.run()

if __name__=='__main__':run()
