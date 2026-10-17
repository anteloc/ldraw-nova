"""Supplier-neutral, exact LDraw part/color palettes and quantity limits.

CSV columns: part_id, color_id; optional name, sku, max_quantity.
Unknown columns are ignored and omitted from canonical palette exports.
"""
from __future__ import annotations

import csv
import io
import math
import re
import zipfile
import zlib
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

PART_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,79}$")
MAX_CATALOG_BYTES = 16 * 1024 * 1024


def normalize_part_id(value: str) -> str:
    value = value.strip().lower().replace("\\", "/")
    if value.startswith("parts/"):
        value = value[6:]
    if value.endswith(".dat"):
        value = value[:-4]
    if not PART_ID.fullmatch(value):
        raise ValueError("Invalid LDraw part identifier")
    return value


@dataclass(frozen=True)
class CatalogPart:
    part_id: str
    color_id: int
    name: str
    sku: str
    max_quantity: int | None = None


class PartsUnavailable(ValueError):
    """An actionable, bounded report for the agent or inventory caller."""


class PartsCatalog:
    def __init__(self, parts: list[CatalogPart], *, name: str = "Parts catalog"):
        self.name = name
        self.parts = {}
        skus = {}
        for part in parts:
            key = (part.part_id, part.color_id)
            if key in self.parts and self.parts[key] != part:
                raise ValueError(f"Ambiguous catalog mapping: {part.part_id}/{part.color_id}")
            self.parts[key] = part
            terms = part.max_quantity
            if part.sku in skus and skus[part.sku] != terms:
                raise ValueError('Inconsistent quantity limit for an inventory group')
            skus[part.sku] = terms
        if not self.parts:
            raise ValueError("Parts palette has no mapped parts")

    @classmethod
    def from_csv(cls, content: str, *, name: str = "Parts catalog") -> PartsCatalog:
        try:
            return cls._from_csv(content, name=name)
        except (csv.Error, TypeError, KeyError):
            raise ValueError("Invalid part, color or quantity in parts palette") from None

    @classmethod
    def _from_csv(cls, content: str, *, name: str) -> PartsCatalog:
        if len(content.encode()) > MAX_CATALOG_BYTES:
            raise ValueError("Parts catalog exceeds its size limit")
        reader = csv.DictReader(io.StringIO(content.lstrip("\ufeff")))
        required = {"part_id", "color_id"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Parts catalog is missing required columns")
        parts = []
        for row in reader:
            if not row["part_id"] or not row["color_id"]:
                continue
            color = int(row["color_id"])
            limit = int(row["max_quantity"]) if row.get("max_quantity") else None
            if color < 0 or color in {16, 24} or limit is not None and limit < 0:
                raise ValueError("Invalid catalog color or quantity limit")
            part_name = row.get('name') or row['part_id']
            sku = row.get('sku') or f"{normalize_part_id(row['part_id'])}-{color}"
            if len(part_name) > 300 or len(sku) > 100:
                raise ValueError("Invalid catalog description or SKU")
            parts.append(CatalogPart(normalize_part_id(row["part_id"]), color,
                part_name, sku, limit))
        return cls(parts, name=name)

    @classmethod
    def load(cls, path: Path) -> PartsCatalog:
        if path.stat().st_size > MAX_CATALOG_BYTES:
            raise ValueError("Parts catalog exceeds its size limit")
        return cls.from_upload(path.name, path.read_bytes())

    @classmethod
    def from_upload(cls, filename: str, data: bytes) -> PartsCatalog:
        """Normalize inventories without extracting archives or fetching references."""
        try:
            return cls._from_upload(filename, data)
        except (csv.Error, TypeError, KeyError):
            raise ValueError("Invalid part, color or quantity in parts palette") from None

    @classmethod
    def _from_upload(cls, filename: str, data: bytes) -> PartsCatalog:
        if not data or len(data) > MAX_CATALOG_BYTES:
            raise ValueError("Choose a nonempty parts palette no larger than 16 MB")
        extension = Path(filename).suffix.lower()
        if extension not in {".csv", ".xml", ".ldr", ".mpd", ".io"}:
            raise ValueError("Choose an LDR, CSV, XML, or Studio IO parts palette")
        if extension == ".io":
            content = studio_model(data)
        else:
            try:
                content = data.decode("utf-8-sig")
            except UnicodeDecodeError:
                raise ValueError("Parts palettes must contain UTF-8 text") from None
        if extension == ".csv":
            reader = csv.DictReader(io.StringIO(content))
            if {"LdrawId", "LDrawColorId", "Qty"}.issubset(reader.fieldnames or []):
                inventory = Counter()
                for row in reader:
                    try:
                        key = normalize_part_id(row["LdrawId"]), int(row["LDrawColorId"])
                        quantity = int(row["Qty"])
                    except (ValueError, TypeError):
                        raise ValueError("Invalid LDraw BOM part, color or quantity") from None
                    if quantity <= 0:
                        raise ValueError("Inventory quantities must be positive")
                    inventory[key] += quantity
            else:
                return cls.from_csv(content)
        elif extension == ".xml":
            inventory = xml_inventory(content)
        else:
            inventory = ldraw_inventory(content)
        parts = []
        for (part, color), quantity in inventory.items():
            if color < 0 or color in {16, 24} or color >= 0x2000000:
                raise ValueError("Inventory requires exact LDraw colors, not inherited or custom colors")
            parts.append(CatalogPart(part, color, part, f"{part}-{color}", quantity))
        return cls(parts)

    def validate(self, inventory: dict[tuple[str, int], int]) -> None:
        errors, quantities, limits = [], Counter(), {}
        for (part_id, color), quantity in inventory.items():
            if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
                raise ValueError("Part quantities must be positive integers")
            part = self.parts.get((normalize_part_id(part_id), color))
            if part is None:
                errors.append(f"{part_id}.dat color {color} (x{quantity})")
                continue
            quantities[part.sku] += quantity
            limits[part.sku] = part.max_quantity
        for sku, quantity in quantities.items():
            limit = limits[sku]
            if limit is not None and quantity > limit:
                errors.append(f"{sku}: requested {quantity}, available {limit}")
        if errors:
            remaining = f"; and {len(errors) - 20} more" if len(errors) > 20 else ""
            raise PartsUnavailable("Parts unavailable in the allowed catalog: " + "; ".join(errors[:20]) + remaining)
        if not inventory:
            raise ValueError("Model contains no physical parts")

    def to_csv(self) -> str:
        """Serialize only palette fields, keeping external metadata out of Nova."""
        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\n")
        writer.writerow(["part_id", "color_id", "name", "sku", "max_quantity"])
        for part in sorted(self.parts.values(), key=lambda item: (item.part_id, item.color_id)):
            writer.writerow([part.part_id, part.color_id, part.name, part.sku,
                             part.max_quantity if part.max_quantity is not None else ""])
        return output.getvalue()

    def search(self, query: str = "", color_id: int | None = None, *, offset: int = 0, limit: int = 50) -> dict:
        query = query.casefold().strip()
        rows = [part for part in self.parts.values()
                if (color_id is None or part.color_id == color_id)
                and (not query or query in f"{part.part_id} {part.name} {part.sku}".casefold())]
        rows.sort(key=lambda part: (part.part_id, part.color_id))
        return {"total": len(rows), "parts": [
            {"part_id": part.part_id + ".dat", "color_id": part.color_id,
             "name": part.name, "sku": part.sku,
             "max_quantity": part.max_quantity} for part in rows[offset:offset + limit]]}


def flat_model_inventory(content: str) -> dict[tuple[str, int], int]:
    """Read only root physical placements of Nova's already-expanded export.

    Embedded DAT geometry is retained for rendering, never counted as inventory.
    Custom colors/geometry cannot be used to impersonate a allowed library part.
    """
    reject_custom_parts(content)
    inventory = Counter()
    root_started = False
    for line in content.splitlines():
        tokens = line.split()
        if not tokens:
            continue
        if tokens[:2] == ["0", "FILE"]:
            if root_started:
                break
            root_started = True
            continue
        if tokens[:2] == ["0", "!COLOUR"]:
            raise PartsUnavailable("Custom colors are not allowed by the parts catalog")
        if tokens[0] in {"2", "3", "4", "5"}:
            raise PartsUnavailable("Custom geometry is not a allowed library part")
        if tokens[0] != "1":
            continue
        if len(tokens) != 15 or not tokens[14].lower().endswith(".dat"):
            raise ValueError("Expected expanded physical DAT placements")
        try:
            color = int(tokens[1])
            if not all(math.isfinite(float(value)) for value in tokens[2:14]):
                raise ValueError()
        except ValueError:
            raise ValueError("Invalid physical placement") from None
        inventory[(normalize_part_id(tokens[14]), color)] += 1
    return dict(inventory)


def reject_custom_parts(content: str) -> None:
    for line in content.splitlines():
        tokens = line.split()
        if tokens[:2] == ['0', '!COLOUR']:
            raise PartsUnavailable('Custom colors are not allowed by the parts catalog')
        if tokens[:2] == ['0', 'FILE'] and tokens[-1].lower().endswith('.dat'):
            raise PartsUnavailable('Embedded DAT definitions cannot override library parts')
        if tokens and tokens[0] in {'2', '3', '4', '5'}:
            raise PartsUnavailable('Custom geometry is not a allowed library part')


def parts_csv_inventory(content: str) -> dict[tuple[str, int], int]:
    """Parse saved BOMs strictly, retaining color and validating quantities."""
    reader = csv.DictReader(io.StringIO(content))
    if not {'LdrawId', 'LDrawColorId', 'Qty'}.issubset(reader.fieldnames or []):
        raise ValueError('Parts CSV requires LdrawId, LDrawColorId and Qty')
    inventory = Counter()
    for row in reader:
        try:
            part = normalize_part_id(row['LdrawId'])
            color, quantity = int(row['LDrawColorId']), int(row['Qty'])
            if quantity <= 0 or color < 0:
                raise ValueError()
        except (ValueError, TypeError):
            raise ValueError('Invalid part, color or quantity in parts CSV') from None
        inventory[(part, color)] += quantity
    return dict(inventory)


def safe_model_name(name: str) -> str:
    name = name.replace("\\", "/").strip().lower()
    path = PurePosixPath(name)
    if not name or path.is_absolute() or ".." in path.parts or ":" in name or any(ord(c) < 32 for c in name):
        raise ValueError("Unsafe model reference")
    return name


def studio_model(data: bytes) -> str:
    """Read Studio's model.ldr in memory, including separately stored submodels."""
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            entries = archive.infolist()
            if len(entries) > 2000 or sum(item.file_size for item in entries) > MAX_CATALOG_BYTES:
                raise ValueError("Studio archive exceeds its expanded size limit")
            names = [safe_model_name(item.filename) for item in entries]
            if len(names) != len(set(names)) or "model.ldr" not in names:
                raise ValueError("Studio archive needs a unique model.ldr")
            models = {}
            for item, name in zip(entries, names):
                if (not item.is_dir() and name.endswith((".ldr", ".mpd", ".dat"))
                        and name not in {"model2.ldr", "modelv1.ldr"}):
                    # Public Studio container-format password, not a user credential.
                    with archive.open(item, pwd=b"soho0909") as stream:
                        content = stream.read(MAX_CATALOG_BYTES + 1)
                    if len(content) > MAX_CATALOG_BYTES:
                        raise ValueError("Studio model exceeds its size limit")
                    models[name] = content.decode("utf-8-sig")
            root = models.pop("model.ldr")
            if not re.search(r"^0\s+FILE\s+", root, re.MULTILINE | re.IGNORECASE):
                root = "0 FILE model.ldr\n" + root
            embedded = {safe_model_name(name) for name in re.findall(
                r"^0\s+FILE\s+(.+)$", root, re.MULTILINE | re.IGNORECASE)}
            for name, content in models.items():
                if name not in embedded:
                    root += "\n0 FILE " + name + "\n" + content
            return root
    except (zipfile.BadZipFile, RuntimeError, NotImplementedError, UnicodeError, OSError, EOFError, zlib.error):
        raise ValueError("Unable to read Studio IO file; try exporting it as LDraw") from None


def ldraw_inventory(content: str) -> dict[tuple[str, int], int]:
    """Count DAT placements in the root model, expanding self-contained MPDs."""
    sections, current, root = {}, None, None
    has_sections = bool(re.search(r"^0\s+FILE\s+", content, re.MULTILINE | re.IGNORECASE))
    if not has_sections:
        sections["model.ldr"] = []
        current = root = "model.ldr"
    for line in content.splitlines():
        fields = line.split(None, 14)
        if not fields:
            continue
        if fields[0] == "0":
            command = fields[1].upper() if len(fields) > 1 else ""
            if command == "FILE":
                name = safe_model_name(line.split(None, 2)[2]) if len(fields) > 2 else ""
                if not name or name in sections or name.endswith(".dat"):
                    raise ValueError("Duplicate or invalid model section")
                sections[name] = []
                current = name
                root = root or name
            elif command == "NOFILE":
                current = None
            elif command == "!COLOUR":
                raise ValueError("Custom colors cannot define a parts palette")
            continue
        if fields[0] != "1" or current is None or len(fields) != 15:
            raise ValueError("Expected physical LDraw part placements")
        try:
            color = int(fields[1])
            if not all(math.isfinite(float(value)) for value in fields[2:14]):
                raise ValueError()
        except ValueError:
            raise ValueError("Invalid LDraw placement") from None
        sections[current].append((safe_model_name(fields[14]), color))

    # Memoize by section and inherited color; reject explosive or cyclic graphs.
    cache, active = {}, set()
    def expand(name: str, inherited: int) -> Counter:
        key = name, inherited
        if name in active or len(active) >= 64:
            raise ValueError("Recursive or excessively nested LDraw submodels")
        if key in cache:
            return cache[key]
        active.add(name)
        result, total = Counter(), 0
        for reference, color in sections[name]:
            color = inherited if color == 16 else color
            if reference in sections:
                child = expand(reference, color)
                result.update(child)
                total += sum(child.values())
            elif reference.endswith(".dat"):
                result[(normalize_part_id(reference), color)] += 1
                total += 1
            else:
                raise ValueError("Missing submodel; upload a self-contained LDraw model")
            if total > 100_000:
                raise ValueError("Palette exceeds 100,000 physical parts")
        active.remove(name)
        cache[key] = result
        return result
    return dict(expand(root, 16)) if root else {}


def xml_inventory(content: str) -> dict[tuple[str, int], int]:
    """Read BrickLink INVENTORY XML, translating its color namespace explicitly."""
    if re.search(r"<!\s*(DOCTYPE|ENTITY)", content, re.IGNORECASE):
        raise ValueError("XML entities and document types are not allowed")
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        raise ValueError("Invalid inventory XML") from None
    if root.tag != "INVENTORY" or any(item.tag != "ITEM" for item in root):
        raise ValueError("Expected BrickLink INVENTORY XML")
    inventory = Counter()
    for item in root:
        if (item.findtext("ITEMTYPE") or "").strip() != "P":
            raise ValueError("Only physical parts (ITEMTYPE P) can define a palette")
        try:
            part = normalize_part_id(item.findtext("ITEMID") or "")
            bricklink_color = int(item.findtext("COLOR") or "")
            color = BRICKLINK_COLORS[bricklink_color]
            quantity = int(item.findtext("MINQTY") or item.findtext("QTY") or "1")
        except (ValueError, KeyError):
            raise ValueError("Invalid XML part or unmapped BrickLink color; use an LDraw export") from None
        if quantity <= 0:
            raise ValueError("Inventory quantities must be positive")
        inventory[(part, color)] += quantity
    return dict(inventory)


# BrickLink -> LDraw cross-references from the Rebrickable color catalogue.
# https://rebrickable.com/colors/ (2025 export). Ambiguous mappings are omitted.
BRICKLINK_COLORS = {
    1: 15, 2: 19, 3: 14, 4: 25, 5: 4, 6: 2, 7: 1, 8: 6,
    9: 7, 10: 8, 11: 0, 12: 47, 13: 40, 14: 33, 15: 43, 16: 42,
    17: 36, 18: 38, 19: 46, 20: 34, 21: 334, 22: 383, 23: 13, 24: 22,
    25: 12, 26: 100, 27: 216, 28: 92, 29: 366, 31: 462, 32: 125, 33: 18,
    34: 27, 35: 120, 36: 10, 37: 74, 38: 17, 39: 3, 40: 11, 41: 118,
    42: 73, 43: 110, 44: 20, 46: 21, 47: 5, 48: 378, 49: 503, 50: 37,
    51: 52, 52: 61, 54: 373, 55: 379, 56: 77, 57: 60, 58: 335, 59: 320,
    60: 79, 61: 142, 62: 9, 63: 272, 64: 62, 65: 82, 66: 135, 67: 80,
    68: 484, 69: 28, 70: 81, 71: 26, 72: 313, 73: 112, 74: 41, 76: 115,
    78: 137, 80: 288, 81: 178, 82: 63, 83: 183, 84: 134, 85: 72, 86: 71,
    87: 232, 88: 70, 89: 85, 90: 78, 91: 86, 93: 69, 94: 351, 95: 179,
    96: 68, 97: 89, 98: 57, 99: 151, 100: 114, 101: 117, 102: 129, 103: 226,
    104: 29, 105: 212, 106: 450, 107: 45, 108: 35, 109: 23, 110: 191, 111: 132,
    113: 39, 114: 44, 115: 297, 116: 75, 117: 76, 118: 294, 119: 150, 120: 308,
    121: 54, 122: 64, 150: 84, 151: 133, 152: 323, 153: 321, 154: 31, 155: 330,
    156: 322, 157: 30, 158: 326, 159: 329, 160: 509, 162: 302, 163: 339, 164: 231,
    167: 402, 168: 423, 169: 422, 220: 353, 221: 285, 222: 341, 223: 362, 224: 364,
    225: 128, 226: 227, 227: 218, 228: 360, 229: 363, 230: 365, 235: 189, 236: 368,
    240: 370, 241: 371, 244: 83, 245: 219, 248: 510, 250: 300, 251: 10375, 252: 184,
    253: 186, 254: 185,
}
