"""
Visual Media & Optical Intelligence Analyzer
============================================
Comprehensive visual intelligence extraction script implementing:
1. Technical & Optical Properties (Aspect ratio, resolution, exposure, blur metrics)
2. Dominant Color Palette Extraction (K-Means color clustering via scikit-learn)
3. Forensic EXIF & Geolocation Metadata Parsing (GPS extraction, device fingerprinting)
4. Biometric & Face Inspection (Integrated with Parla FacialRecognitionEngine)
5. Zero-Trace Privacy & Anonymization Audit (VOID Pillar bystander redaction)
6. Markdown / JSON Intelligence Report Generation

Adheres to Windows Python Resilience Rule (.agents/rules/windows-python-resilience.md).
"""

import sys
import os
import argparse
import json
import math
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from PIL import Image, ImageStat, ExifTags
from sklearn.cluster import KMeans

# Add project root to sys.path so parla modules are importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from parla.domains.facial_recognition_engine import (
        FacialRecognitionEngine,
        WatchlistGallery,
        WatchlistTarget,
        MatchClassification
    )
except ImportError:
    FacialRecognitionEngine = None
    WatchlistGallery = None

try:
    from parla.core.ledger import OfflineLedger
except ImportError:
    OfflineLedger = None


class VisualMediaAnalyzer:
    """Multi-vector image forensics, optical metrics, and biometric inspector."""

    def __init__(self, gallery: Optional[Any] = None, ledger: Optional[Any] = None, load_accountability: bool = False):
        self.gallery = gallery or (WatchlistGallery() if WatchlistGallery else None)
        if load_accountability and self.gallery and hasattr(self.gallery, "load_from_accountability_roster"):
            self.gallery.load_from_accountability_roster()
        self.ledger = ledger
        self.engine = FacialRecognitionEngine(gallery=self.gallery, ledger=self.ledger) if FacialRecognitionEngine else None

    @staticmethod
    def extract_optical_properties(img: Image.Image) -> Dict[str, Any]:
        """Calculates optical dimensions, aspect ratio, luminance, and contrast."""
        width, height = img.size
        gcd = math.gcd(width, height)
        aspect_ratio_str = f"{width // gcd}:{height // gcd}" if gcd > 0 else f"{width}:{height}"
        decimal_ratio = round(width / height, 3) if height > 0 else 0.0

        # Convert to grayscale for optical variance & exposure
        gray = img.convert("L")
        stat = ImageStat.Stat(gray)
        mean_luminance = round(stat.mean[0], 2)
        std_contrast = round(stat.stddev[0], 2)

        # Estimate sharpness via discrete Laplacian gradient approximation
        arr = np.asarray(gray, dtype=np.float32)
        laplacian = (
            np.pad(arr[1:, :], ((0, 1), (0, 0)), mode="edge")
            + np.pad(arr[:-1, :], ((1, 0), (0, 0)), mode="edge")
            + np.pad(arr[:, 1:], ((0, 0), (0, 1)), mode="edge")
            + np.pad(arr[:, :-1], ((0, 0), (1, 0)), mode="edge")
            - 4 * arr
        )
        sharpness_variance = round(float(laplacian.var()), 2)

        lighting_eval = "BALANCED"
        if mean_luminance > 180:
            lighting_eval = "HIGH-KEY / OVEREXPOSED"
        elif mean_luminance < 75:
            lighting_eval = "LOW-KEY / UNDEREXPOSED"

        return {
            "resolution": f"{width}x{height}",
            "width_px": width,
            "height_px": height,
            "aspect_ratio": f"{decimal_ratio}:1 ({aspect_ratio_str})",
            "format": img.format or "UNKNOWN",
            "color_mode": img.mode,
            "mean_luminance": mean_luminance,
            "contrast_std": std_contrast,
            "sharpness_variance": sharpness_variance,
            "lighting_assessment": lighting_eval
        }

    @staticmethod
    def extract_dominant_colors(img: Image.Image, num_colors: int = 5) -> List[Dict[str, Any]]:
        """Extracts dominant hex color palette using K-Means clustering."""
        img_rgb = img.convert("RGB").resize((150, 150))
        arr = np.asarray(img_rgb).reshape(-1, 3)

        kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
        kmeans.fit(arr)

        labels = kmeans.labels_
        counts = np.bincount(labels)
        total_pixels = len(labels)

        palette = []
        for center, count in sorted(zip(kmeans.cluster_centers_, counts), key=lambda x: x[1], reverse=True):
            r, g, b = [int(round(c)) for c in center]
            hex_code = f"#{r:02X}{g:02X}{b:02X}"
            percentage = round((count / total_pixels) * 100, 1)
            palette.append({
                "hex": hex_code,
                "rgb": [r, g, b],
                "percentage": percentage
            })
        return palette

    @staticmethod
    def extract_exif_metadata(img: Image.Image) -> Dict[str, Any]:
        """Extracts forensic camera EXIF details and GPS coordinates if present."""
        exif_raw = img.getexif()
        if not exif_raw:
            return {"exif_present": False, "details": {}, "gps": None}

        exif_data = {}
        for tag_id, value in exif_raw.items():
            tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
            # Filter non-serializable byte blobs
            if isinstance(value, (str, int, float)):
                exif_data[tag_name] = value

        # Check for GPS Info
        gps_info = None
        gps_tag_id = 0x8825  # GPSInfo tag
        if gps_tag_id in exif_raw:
            gps_sub = exif_raw.get_ifd(gps_tag_id)
            gps_info = {
                ExifTags.GPSTAGS.get(k, str(k)): v
                for k, v in gps_sub.items()
                if isinstance(v, (str, int, float, tuple))
            }

        return {
            "exif_present": True,
            "device_make": exif_data.get("Make", "Unknown"),
            "device_model": exif_data.get("Model", "Unknown"),
            "date_time": exif_data.get("DateTime", "Unknown"),
            "software": exif_data.get("Software", "Unknown"),
            "gps_info": gps_info,
            "raw_tags": exif_data
        }

    def inspect_biometrics(
        self,
        img: Image.Image,
        source_id: str = "VISUAL_ANALYZER_01",
        anonymize: bool = False
    ) -> Dict[str, Any]:
        """Runs face detection, watchlist search, and optional bystander redaction."""
        if not self.engine:
            return {
                "biometrics_available": False,
                "message": "FacialRecognitionEngine not loaded."
            }

        result = self.engine.process_frame(
            image=img,
            source_id=source_id,
            anonymize_bystanders=anonymize
        )
        return {
            "biometrics_available": True,
            "total_faces_detected": result["total_faces_detected"],
            "targets_matched": result["targets_matched"],
            "bystanders_anonymized": result["bystanders_anonymized"],
            "detections": result["detections"],
            "ledger_events": result["ledger_events"],
            "redacted_image": result["processed_image"] if anonymize else None
        }

    def analyze(
        self,
        image_path: str,
        anonymize_bystanders: bool = False,
        output_redacted_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Performs complete multi-vector optical, colorimetric, forensic, and biometric analysis."""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        img = Image.open(str(path))

        optical = self.extract_optical_properties(img)
        palette = self.extract_dominant_colors(img)
        exif = self.extract_exif_metadata(img)
        biometrics = self.inspect_biometrics(img, source_id=path.name, anonymize=anonymize_bystanders)

        # Save redacted image if requested
        if anonymize_bystanders and biometrics.get("redacted_image") and output_redacted_path:
            out_p = Path(output_redacted_path)
            out_p.parent.mkdir(parents=True, exist_ok=True)
            biometrics["redacted_image"].save(str(out_p))
            biometrics["redacted_image_path"] = str(out_p)

        return {
            "file_name": path.name,
            "file_size_kb": round(path.stat().st_size / 1024, 2),
            "optical_metrics": optical,
            "dominant_palette": palette,
            "metadata_audit": exif,
            "biometric_audit": {
                k: v for k, v in biometrics.items() if k != "redacted_image"
            }
        }

    @staticmethod
    def format_markdown_report(report: Dict[str, Any]) -> str:
        """Formats the analysis result into a clean, GitHub-flavored markdown report."""
        opt = report["optical_metrics"]
        meta = report["metadata_audit"]
        bio = report["biometric_audit"]

        lines = [
            f"# Visual Media & Optical Intelligence Report: {report['file_name']}",
            "",
            "## 1. Technical & Optical Telemetry",
            f"- **Resolution:** {opt['resolution']} ({opt['aspect_ratio']})",
            f"- **Color Space:** {opt['color_mode']} | Format: {opt['format']}",
            f"- **Mean Luminance:** {opt['mean_luminance']} / 255.0 ({opt['lighting_assessment']})",
            f"- **Contrast Standard Deviation:** {opt['contrast_std']}",
            f"- **Sharpness Variance (Laplacian):** {opt['sharpness_variance']}",
            "",
            "## 2. Dominant Colorimetric Palette (K-Means)",
            "| Rank | Hex Code | RGB | Coverage |",
            "| :--- | :--- | :--- | :--- |"
        ]

        for i, c in enumerate(report["dominant_palette"], 1):
            lines.append(f"| {i} | `{c['hex']}` | `{c['rgb']}` | {c['percentage']}% |")

        lines.extend([
            "",
            "## 3. Forensic Metadata & Privacy Audit",
            f"- **EXIF Header Present:** {meta.get('exif_present', False)}",
            f"- **Camera Hardware:** {meta.get('device_make', 'N/A')} {meta.get('device_model', 'N/A')}",
            f"- **Software / Pipeline:** {meta.get('software', 'N/A')}",
            f"- **GPS Telemetry Detected:** {'YES (Micro-coordinates found)' if meta.get('gps_info') else 'NO (Clean / Sanitized)'}",
            "",
            "## 4. Biometric & Face Recognition Audit",
            f"- **Total Faces Detected:** {bio.get('total_faces_detected', 0)}",
            f"- **Enrolled Targets Matched:** {bio.get('targets_matched', 0)}",
            f"- **Bystanders Anonymized (VOID Pillar):** {bio.get('bystanders_anonymized', 0)}"
        ])

        if bio.get("detections"):
            lines.append("")
            lines.append("### Detections Detail")
            for d in bio["detections"]:
                status = "TARGET MATCH" if not d["is_bystander"] else "BYSTANDER"
                lines.append(f"- `BBox {d['bbox']}` -> {status} (Classification: `{d['classification']}`, Score: {d['similarity_score']})")

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Parla Visual Media & Optical Intelligence Analyzer")
    parser.add_argument("image_path", help="Path to the image file to analyze")
    parser.add_argument("--anonymize", action="store_true", help="Redact/blur non-target bystander faces")
    parser.add_argument("--output-redacted", help="Save blurred/redacted image copy to this path")
    parser.add_argument("--watchlist-accountability", action="store_true", help="Enroll UN FFM / ICC / IIMM accountability roster into watchlist gallery")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of Markdown")
    args = parser.parse_args()

    analyzer = VisualMediaAnalyzer(load_accountability=args.watchlist_accountability)
    try:
        report = analyzer.analyze(
            image_path=args.image_path,
            anonymize_bystanders=args.anonymize,
            output_redacted_path=args.output_redacted
        )

        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(analyzer.format_markdown_report(report))
    except Exception as e:
        print(f"[FAIL] Error analyzing image: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
