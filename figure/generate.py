"""Image → 3D mesh with Hunyuan3D-2 (shape only; the page supplies the material).

Usage: .venv/bin/python generate.py [seed] [model]
  model: full (default) | mini
Writes raw-<model>-<seed>.glb and figure-<model>-<seed>.glb (cleaned, decimated).
"""
import os, sys, time
os.environ.setdefault("HY3DGEN_MODELS", os.path.join(os.path.dirname(os.path.abspath(__file__)), "models"))
sys.path.insert(0, "hy3d")
import torch
from PIL import Image
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline, FloaterRemover, DegenerateFaceRemover, FaceReducer

seed = int(sys.argv[1]) if len(sys.argv) > 1 else 12345
model = sys.argv[2] if len(sys.argv) > 2 else "full"
repo, sub = {
    "full": ("tencent/Hunyuan3D-2", "hunyuan3d-dit-v2-0"),
    "mini": ("tencent/Hunyuan3D-2mini", "hunyuan3d-dit-v2-mini"),
}[model]

pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
    repo, subfolder=sub, variant="fp16", use_safetensors=True, device="mps", dtype=torch.float16)

t = time.time()
mesh = pipeline(image=Image.open("input.png"), num_inference_steps=50, octree_resolution=380,
                num_chunks=20000, generator=torch.manual_seed(seed), output_type="trimesh")[0]
print(f"generated in {time.time() - t:.0f}s, {len(mesh.faces)} faces")
mesh.export(f"raw-{model}-{seed}.glb")

mesh = FloaterRemover()(mesh)
mesh = DegenerateFaceRemover()(mesh)
mesh = FaceReducer()(mesh, max_facenum=120000)
mesh.export(f"figure-{model}-{seed}.glb")
print(f"cleaned: {len(mesh.faces)} faces")
