"""Bounded, color-preserving GLB voxelization using Python Trimesh.

Like BrickBuilderAI's trimesh_voxelizer, sample UVs at the closest surface
point before palette mapping. Keep mesh instances separate so concatenation
cannot discard textures. Packing and support repair remain in conversion.py.
"""
from __future__ import annotations

from io import BytesIO
import json
from pathlib import Path
import re
import struct

import numpy as np
from PIL import Image
import trimesh

from .conversion import MAX_GRID_CELLS, MAX_VOXELS

MAX_GLB_BYTES = 16 * 1024 * 1024
MAX_FACES = 100_000
MAX_VERTICES = 200_000
MAX_SAMPLES = 2_000_000


def validate_glb(data: bytes) -> None:
    """Check embedded resources before handing an untrusted file to a loader."""
    try:
        if not 20 <= len(data) <= MAX_GLB_BYTES:
            raise ValueError("Choose a GLB between 20 bytes and 16 MB")
        magic, version, length = struct.unpack_from("<4sII", data)
        if magic != b"glTF" or version != 2 or length != len(data):
            raise ValueError("Choose a valid binary glTF 2.0 (.glb) file")
        offset, chunks = 12, []
        while offset < length:
            size, kind = struct.unpack_from("<II", data, offset)
            offset += 8
            if size % 4 or offset + size > length:
                raise ValueError("Invalid GLB chunk length")
            chunks.append((kind, data[offset:offset + size]))
            offset += size
        if not chunks or chunks[0][0] != 0x4E4F534A or len(chunks) != 2 or chunks[1][0] != 0x004E4942:
            raise ValueError("GLB must contain JSON and an embedded binary buffer")
        document = json.loads(chunks[0][1])
        if not isinstance(document, dict):
            raise ValueError("GLB JSON must be an object")
        if document.get("asset", {}).get("version") != "2.0":
            raise ValueError("GLB must use glTF 2.0")
        if document.get("extensionsRequired"):
            raise ValueError("Export an uncompressed GLB without required extensions")
        buffers = document.get("buffers", [])
        if len(buffers) != 1 or "uri" in buffers[0]:
            raise ValueError("Embed buffers and textures in the GLB; external resources are not supported")
        binary = chunks[1][1]
        if not 0 < buffers[0]["byteLength"] <= len(binary):
            raise ValueError("Invalid GLB buffer length")
        for view in document.get("bufferViews", []):
            start, size = view.get("byteOffset", 0), view["byteLength"]
            if view.get("buffer", 0) != 0 or start < 0 or size < 0 or start + size > len(binary):
                raise ValueError("Invalid GLB buffer view")
        vertices = faces = 0
        mesh_face_counts = []
        accessors = document.get("accessors", [])
        for mesh in document.get("meshes", []):
            mesh_faces = 0
            for primitive in mesh.get("primitives", []):
                if primitive.get("mode", 4) != 4 or primitive.get("extensions"):
                    raise ValueError("Export an uncompressed triangle mesh")
                count = accessors[primitive["attributes"]["POSITION"]]["count"]
                vertices += count
                mesh_faces += accessors[primitive["indices"]]["count"] // 3 if "indices" in primitive else count // 3
            faces += mesh_faces
            mesh_face_counts.append(mesh_faces)
        if not 0 < faces <= MAX_FACES or not 0 < vertices <= MAX_VERTICES:
            raise ValueError("Keep the GLB within 100,000 triangles and 200,000 vertices")
        if len(document.get("nodes", [])) > 128:
            raise ValueError("Keep the GLB within 128 scene nodes")
        if sum(mesh_face_counts[node["mesh"]] for node in document.get("nodes", []) if "mesh" in node) > MAX_FACES:
            raise ValueError("Keep the GLB within 100,000 instanced triangles")
        if document.get("skins") or any(p.get("targets") for m in document.get("meshes", []) for p in m.get("primitives", [])):
            raise ValueError("Bake skinning and morph targets into a static mesh before importing")
        for material in document.get("materials", []):
            texture = material.get("pbrMetallicRoughness", {}).get("baseColorTexture", {})
            if texture.get("texCoord", 0) != 0 or texture.get("extensions"):
                raise ValueError("Bake texture transforms into the first UV channel before importing")
        for image in document.get("images", []):
            if "uri" in image or image.get("mimeType") not in {"image/png", "image/jpeg"}:
                raise ValueError("Embed PNG or JPEG textures in the GLB")
            view = document["bufferViews"][image["bufferView"]]
            start = view.get("byteOffset", 0)
            with Image.open(BytesIO(binary[start:start + view["byteLength"]])) as decoded:
                if decoded.format not in {"PNG", "JPEG"}:
                    raise ValueError("Embed PNG or JPEG textures in the GLB")
                if decoded.width * decoded.height > 4_194_304:
                    raise ValueError("Keep each embedded texture within 4 megapixels")
                decoded.verify()
    except (KeyError, IndexError, TypeError, struct.error, OSError, Image.DecompressionBombError) as exc:
        raise ValueError("Malformed GLB mesh or embedded texture") from exc


def ldraw_palette(library: Path) -> tuple[np.ndarray, np.ndarray]:
    """Use explicit opaque colors from the installed official LDraw palette."""
    colors = {}
    for line in (library / "LDConfig.ldr").read_text().splitlines():
        match = re.match(r"0\s+!COLOUR\s+\S+\s+CODE\s+(\d+)\s+VALUE\s+#([\dA-Fa-f]{6})", line)
        if match and not re.search(r"\bALPHA\s+\d+", line):
            code = int(match[1])
            if 0 <= code <= 511 and code not in {16, 24}:
                colors[code] = [int(match[2][i:i + 2], 16) for i in (0, 2, 4)]
    if not colors:
        raise ValueError("The LDraw library has no explicit opaque colors")
    codes = np.array(sorted(colors), dtype=int)
    return codes, np.array([colors[code] for code in codes], dtype=float)


def surface_colors(mesh: trimesh.Trimesh, points: np.ndarray, *, surface=None) -> np.ndarray:
    """Sample textures and interpolate vertex colors at closest triangle points."""
    closest, _, face_indices = surface if surface is not None else mesh.nearest.on_surface(points)
    barycentric = trimesh.triangles.points_to_barycentric(mesh.triangles[face_indices], closest)
    visual = mesh.visual
    if visual.kind == "texture":
        material = visual.material
        image = getattr(material, "baseColorTexture", None)
        if image is None:
            image = getattr(material, "image", None)
        factor = getattr(material, "baseColorFactor", None)
        if factor is None:
            factor = getattr(material, "diffuse", [255, 255, 255, 255])
        factor = np.asarray(factor, dtype=float)[:3] / 255.0
        vertex = visual.vertex_attributes.get("color")
        if vertex is not None:
            values = np.asarray(vertex)
            divisor = np.iinfo(values.dtype).max if np.issubdtype(values.dtype, np.integer) else 1.0
            tint = (barycentric[:, :, None] * values[mesh.faces[face_indices], :3]).sum(axis=1) / divisor
            factor = factor * tint
        if image is not None:
            if visual.uv is None:
                raise ValueError("A textured mesh is missing UV coordinates")
            uv = (barycentric[:, :, None] * visual.uv[mesh.faces[face_indices]]).sum(axis=1)
            # PBR baseColorFactor multiplies the texture; Trimesh.to_color does
            # not apply that factor when a texture exists.
            return trimesh.visual.color.uv_to_color(uv, image)[:, :3] * factor
        return np.broadcast_to(factor * 255, (len(points), 3)).copy()
    if visual.kind == "face":
        return visual.face_colors[face_indices, :3]
    if visual.kind == "vertex":
        return (barycentric[:, :, None] * visual.vertex_colors[mesh.faces[face_indices], :3]).sum(axis=1)
    return np.tile([160, 165, 169], (len(points), 1))


def voxelize_glb(path: str | Path, *, resolution: int, library: Path) -> tuple[dict, dict]:
    if type(resolution) is not int or not 8 <= resolution <= 48:
        raise ValueError("Choose a resolution from 8 to 48 studs")
    path = Path(path)
    if path.stat().st_size > MAX_GLB_BYTES:
        raise ValueError("GLB exceeds 16 MB")
    data = path.read_bytes()
    validate_glb(data)
    scene = trimesh.load_scene(BytesIO(data), file_type="glb", process=False, allow_remote=False)
    meshes = []
    for node in sorted(scene.graph.nodes_geometry):
        transform, name = scene.graph[node]
        mesh = scene.geometry[name].copy()
        if not isinstance(mesh, trimesh.Trimesh) or not len(mesh.faces):
            continue
        mesh.apply_transform(transform)
        # glTF Y-up -> sculpture Z-up. One brick is 1.2 studs tall: compensate
        # before voxelization so the exported sculpture retains its proportions.
        mesh.vertices = mesh.vertices[:, [0, 2, 1]] * [1, -1, 1 / 1.2]
        meshes.append(mesh)
    if not meshes or sum(len(m.faces) for m in meshes) > MAX_FACES:
        raise ValueError("GLB has no usable mesh, or too many instanced triangles")
    bounds = np.array([m.bounds for m in meshes])
    if not np.isfinite(bounds).all():
        raise ValueError("GLB contains non-finite coordinates")
    origin = bounds[:, 0].min(axis=0)
    extents = bounds[:, 1].max(axis=0) - origin
    if extents.max() <= 1e-12:
        raise ValueError("GLB mesh has zero extent")
    scale = (resolution - 1) / extents.max()
    codes, palette = ldraw_palette(library)
    cells: dict[tuple, tuple] = {}
    sample_budget = 0
    for mesh in meshes:
        mesh.vertices = (mesh.vertices - origin) * scale
        edges = mesh.triangles - np.roll(mesh.triangles, 1, axis=1)
        longest = np.linalg.norm(edges, axis=2).max(axis=1)
        levels = np.maximum(0, np.ceil(np.log2(np.maximum(longest / 0.5, 1))))
        sample_budget += int(np.power(4., levels).sum())
        if sample_budget > MAX_SAMPLES:
            raise ValueError("This mesh is too complex at that resolution; simplify it or lower the resolution")
        grid = mesh.voxelized(pitch=1, method="subdivide", max_iter=10)
        points = grid.points
        if len(points) + len(cells) > MAX_VOXELS * 2:
            raise ValueError("Too many surface voxels; lower the resolution")
        # Chunk nearest-surface queries to bound temporary triangle/color arrays.
        for start in range(0, len(points), 512):
            batch = points[start:start + 512]
            surface = mesh.nearest.on_surface(batch)
            rgb = surface_colors(mesh, batch, surface=surface)
            if not np.isfinite(rgb).all():
                raise ValueError("GLB contains invalid UVs or colors")
            distances = ((rgb[:, None, :] - palette[None, :, :]) ** 2).sum(axis=2)
            colors = codes[distances.argmin(axis=1)]
            nearest_distance = surface[1]
            for point, color, distance in zip(batch, colors, nearest_distance):
                key = tuple(np.rint(point).astype(int))
                # A shared voxel takes the closest surface's color. Stable scene
                # ordering resolves equal-distance overlap deterministically.
                if key not in cells or distance < cells[key][0]:
                    cells[key] = (float(distance), int(color))
        if len(cells) > MAX_VOXELS:
            raise ValueError("Too many surface voxels; lower the resolution")
    if not cells:
        raise ValueError("Voxelization produced no cells")
    coordinates = np.array(sorted(cells), dtype=int)
    minimum = coordinates.min(axis=0)
    dimensions = coordinates.max(axis=0) - minimum + 1
    if np.prod(dimensions) > MAX_GRID_CELLS:
        raise ValueError("Voxel grid is too large; lower the resolution")
    rows = [[*map(int, np.array(key) - minimum), cells[key][1]] for key in sorted(cells)]
    return {"voxels": rows}, {"voxelizer": "trimesh-subdivide", "resolution": resolution,
        "mesh_instances": len(meshes), "surface_voxels": len(rows),
        "palette_colors": len({row[3] for row in rows}), "dimensions": dimensions.tolist()}
