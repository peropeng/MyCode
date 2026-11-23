"""Replay existing public-feature inference without the original machine."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import types


def project_root():
    return Path(__file__).resolve().parents[2]


def file_sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream,"sha256").hexdigest()


def _module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def load_models(root=None):
    root = root or project_root()
    source = root/"src/thesis_recovery/frozen/ranking"
    upstream = root/".external/StepFinder/model.py"
    if not upstream.is_file():
        raise FileNotFoundError("Run python tools/fetch_external.py --core first")
    previous_path = list(sys.path)
    names = ("common","stepfinder_model","owned_exp130_model","original_models")
    previous = {name:sys.modules.get(name) for name in names}
    try:
        common=types.ModuleType("common")
        common.E=source
        common.CONTEXT_ARMS=("AB_GLOBAL","AB_LOCAL","AB_STATIC","AB_VALUE_PERM")
        sys.modules["common"]=common
        sys.modules["stepfinder_model"]=_module("thesis_frozen_stepfinder",upstream)
        sys.path.insert(0,str(source/"sources"))
        sys.modules["owned_exp130_model"]=_module("thesis_owned_exp130_model",source/"sources/owned_exp130_model.py")
        sys.modules["original_models"]=_module("thesis_owned_original_models",source/"sources/original_models.py")
        return _module("thesis_owned_context_models",source/"context_models.py")
    finally:
        sys.path[:]=previous_path
        for name,old in previous.items():
            if old is None:
                sys.modules.pop(name,None)
            else:
                sys.modules[name]=old


def replay_source3(root=None):
    """Check the original three checkpoints against 18 recorded public inputs.

    This is a migration/replay check, not a new scientific comparison.
    No training, labels, API requests or private acceptance are executed.
    """
    import numpy as np
    import torch
    root=root or project_root()
    manifest=json.loads((root/"manifests/current_method.json").read_text(encoding="utf-8"))
    for record in [manifest["features"],*manifest["source3_checkpoints"]]:
        target=root/record["path"]
        if not target.is_file() or file_sha(target)!=record["sha256"]:
            raise RuntimeError("Missing or changed core asset: "+record["path"])
    models=load_models(root)
    torch.set_num_threads(4)
    models.seed_all(0)
    data=torch.load(root/manifest["features"]["path"],map_location="cpu",weights_only=False)["records"]
    batches=manifest["batches"]
    expected=manifest["reference_probabilities"]
    outputs={}
    maximum_error=0.0
    for checkpoint in manifest["source3_checkpoints"]:
        ck=torch.load(root/checkpoint["path"],map_location="cpu",weights_only=False)
        model=models.create("AB_GLOBAL")
        model.load_state_dict(ck["state_dict"],strict=True)
        model.eval()
        result={}
        with torch.inference_mode():
            for members in batches:
                batch=models.collate(members,data,(ck["scaler_mean"],ck["scaler_std"]),torch.device("cpu"))
                scores,_=models.forward(model,"AB_GLOBAL",batch)
                for task,score in zip(members,scores):
                    probabilities=torch.softmax(score.cpu(),0).tolist()
                    reference=expected[str(checkpoint["seed"])][task]
                    error=float(np.max(np.abs(np.asarray(probabilities)-np.asarray(reference))))
                    maximum_error=max(maximum_error,error)
                    order=sorted(range(len(probabilities)),key=lambda i:(-probabilities[i],i))
                    reference_order=sorted(range(len(reference)),key=lambda i:(-reference[i],i))
                    if order!=reference_order or error>1e-5:
                        raise RuntimeError("Replay differs from frozen public inference: "+task)
                    result[task]=order
        outputs[str(checkpoint["seed"])]=result
    return {"check":"source3_portable_replay","models":len(outputs),"tasks":len(manifest["task_order"]),"rankings_checked":sum(len(v) for v in outputs.values()),"all_orders_match":True,"maximum_probability_error":maximum_error,"training_steps":0,"api_requests":0,"gold_reads":0}
