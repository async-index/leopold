"""Image → 3D mesh with Hunyuan3D-2 (shape only; the page supplies the material).

Usage: .venv/bin/python generate.py [seed] [model] [input.png]
  model: full (default) | mini
Run from the folder holding input.png; writes raw-<model>-<seed>.glb and
mesh-<model>-<seed>.glb (cleaned, decimated) there.
"""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault("HY3DGEN_MODELS", os.path.join(HERE, "models"))
sys.path.insert(0, os.path.join(HERE, "hy3d"))
import torch
from PIL import Image
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline, FloaterRemover, DegenerateFaceRemover, FaceReducer

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 12345
model = sys.argv[2] if len(sys.argv) > 2 else "full"
source = sys.argv[3] if len(sys.argv) > 3 else "input.png"
repo, sub = {
    "full": ("tencent/Hunyuan3D-2", "hunyuan3d-dit-v2-0"),
    "mini": ("tencent/Hunyuan3D-2mini", "hunyuan3d-dit-v2-mini"),
}[model]

pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
    repo, subfolder=sub, variant="fp16", use_safetensors=True, device="mps", dtype=torch.float16)

t = time.time()
mesh = pipeline(image=Image.open(source), num_inference_steps=50, octree_resolution=380,
                num_chunks=20000, generator=torch.manual_seed(seed), output_type="trimesh")[0]
print(f"generated in {time.time() - t:.0f}s, {len(mesh.faces)} faces")
mesh.export(f"raw-{model}-{seed}.glb")

mesh = FloaterRemover()(mesh)
mesh = DegenerateFaceRemover()(mesh)
mesh = FaceReducer()(mesh, max_facenum=120000)
mesh.export(f"mesh-{model}-{seed}.glb")
print(f"cleaned: {len(mesh.faces)} faces")
