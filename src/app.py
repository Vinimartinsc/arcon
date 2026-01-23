#!/usr/bin/env python3
"""
Image Archive Processor
Converts RAW images and applies metadata
Supports both CLI and web interface with C2PA signing
"""

# std imports
import os
import sys
import subprocess
import argparse
import webbrowser
from threading import Timer

# 3rd party imports
import logging
import shutil
import json
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, request, jsonify

# Conditional C2PA import with graceful fallback
try:
    from c2pa import Builder, Signer, C2paSignerInfo, C2paSigningAlg, Reader
    C2PA_AVAILABLE = True
except ImportError:
    C2PA_AVAILABLE = False

app = Flask(__name__)


class ImageProcessor:
    """Class to handle image processing and metadata application."""

    def __init__(
        self,
        archive,
        output_dir,
        logs_dir="logs",
        quality=95,
        rotate=0,
        license_only=False,
        creator="",
        credit="",
        copyright_name="",
        usage_terms="",
        license_url="",
        sign_images=False,
        cert_path="",
        private_key_path="",
        signing_alg="es256",
    ):
        self.archive = Path(archive)
        self.output_dir = Path(output_dir)
        self.logs_dir = Path(logs_dir)
        self.quality = quality
        self.rotate = rotate
        self.license_only = license_only
        self.year = datetime.now().year

        self.creator = creator
        self.credit = credit
        self.copyright_name = copyright_name
        self.usage_terms = usage_terms
        self.license_url = license_url

        # C2PA signing parameters
        self.sign_images = sign_images
        self.cert_path = Path(cert_path) if cert_path else None
        self.private_key_path = Path(private_key_path) if private_key_path else None
        self.signing_alg = signing_alg

        # Setup bundled binaries path
        self.bundle_dir = self._get_bundle_dir()
        self.dcraw_cmd = self._get_binary("dcraw")
        self.convert_cmd = self._get_binary("magick")
        self.exiftool_cmd = self._get_binary("exiftool")

        self.log = []

    def _get_bundle_dir(self):
        """Get the bundled binaries directory based on platform."""
        # First check if running as PyInstaller executable
        if getattr(sys, "frozen", False):
            base_path = Path(sys._MEIPASS)
        else:
            # Running as script - look for bundle relative to script location
            base_path = Path(__file__).parent.parent

        if sys.platform == "win32":
            return base_path / "bundle" / "windows"
        else:
            return base_path / "bundle" / "unix"

    def _get_binary(self, cmd):
        """Get the full path to a binary, preferring bundled version."""
        bundled_binary = self.bundle_dir / cmd / cmd

        # For Windows, add .exe extension if not present
        if sys.platform == "win32" and not bundled_binary.suffix:
            bundled_binary = self.bundle_dir / cmd / f"{cmd}.exe"

        # Use bundled binary if it exists, otherwise fall back to system PATH
        if bundled_binary.exists():
            return str(bundled_binary)

        # Fall back to system command
        system_cmd = shutil.which(cmd)
        if system_cmd:
            return system_cmd

        return cmd  # Will fail later during execution if not found

    def log_message(self, msg):
        """Log a message with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {msg}"
        self.log.append(log_line)
        print(log_line)

    def check_dependencies(self):
        """Verify all required binaries are available."""
        missing = []

        if not self.dcraw_cmd or (
            not self.bundle_dir.joinpath(
                "dcraw/dcraw" if sys.platform != "win32" else "dcraw/dcraw.exe"
            ).exists()
            and not shutil.which("dcraw")
        ):
            missing.append("dcraw")
        if not self.convert_cmd or (
            not self.bundle_dir.joinpath(
                "magick/magick" if sys.platform != "win32" else "magick/magick.exe"
            ).exists()
            and not shutil.which("magick")
        ):
            missing.append("magick")
        if not self.exiftool_cmd or (
            not self.bundle_dir.joinpath(
                "exiftool/exiftool"
                if sys.platform != "win32"
                else "exiftool/exiftool.exe"
            ).exists()
            and not shutil.which("exiftool")
        ):
            missing.append("exiftool")

        if missing:
            raise RuntimeError(
                f"Missing dependencies: {', '.join(missing)}. Bundled in {self.bundle_dir}"
            )

        # Check C2PA signing requirements
        if self.sign_images:
            if not C2PA_AVAILABLE:
                raise RuntimeError(
                    "C2PA library not installed. Install with: pip install c2pa-python\n"
                    "See: https://github.com/contentauth/c2pa-python"
                )
            if not self.cert_path or not self.cert_path.exists():
                raise RuntimeError(f"C2PA certificate not found: {self.cert_path}")
            if not self.private_key_path or not self.private_key_path.exists():
                raise RuntimeError(
                    f"C2PA private key not found: {self.private_key_path}"
                )

    def validate(self):
        """Validate input parameters."""
        if not self.archive.is_dir():
            raise ValueError(f"Archive folder not found: {self.archive}")

        if self.archive.resolve() == self.output_dir.resolve():
            raise ValueError(
                "Output folder must be different from input archive folder"
            )

        if not 1 <= self.quality <= 100:
            raise ValueError("Quality must be between 1 and 100")

        try:
            int(self.rotate)
        except ValueError as exc:
            raise ValueError("Rotate must be an integer") from exc

    def process(self):
        """Process the images and apply metadata."""
        self.log_message("=" * 50)
        self.log_message(f"Started at: {datetime.now()}")
        self.log_message(f"Archive Name: {self.archive}")
        self.log_message(f"Image Quality: {self.quality}")
        self.log_message(f"Image Rotation: {self.rotate}")
        self.log_message(f"License Only: {self.license_only}")
        self.log_message(f"C2PA Signing: {self.sign_images}")
        if self.sign_images and C2PA_AVAILABLE:
            self.log_message(f"C2PA Algorithm: {self.signing_alg}")
        self.log_message("=" * 50)

        archive_name = self.archive.name
        base_public = self.output_dir / archive_name
        base_logs = self.logs_dir

        base_public.mkdir(parents=True, exist_ok=True)
        base_logs.mkdir(parents=True, exist_ok=True)

        log_file = (
            base_logs
            / f"{archive_name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
        )

        if not self.license_only:
            self.process_images(base_public)
        else:
            self.log_message("License-only mode — skipping image conversion")

        self.apply_metadata(base_public)

        if self.sign_images:
            self.sign_all_images(base_public)

        # Save log to file
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("\n".join(self.log))

        self.log_message("=" * 50)
        self.log_message(f"Completed at: {datetime.now()}")
        self.log_message(f"Log file: {log_file}")
        self.log_message("=" * 50)

        return "\n".join(self.log)

    def process_images(self, base_public):
        """Process RAW images in the archive."""
        # Detect structure: check if archive root has image files directly
        root_has_images = any(
            (list(self.archive.glob("*.NEF")) + list(self.archive.glob("*.nef")))
        )

        if root_has_images:
            # Simple structure: /dossier/image_files.NEF (archive root IS the dossier)
            self.log_message(f"Processing Document: {self.archive.name}")
            output_dir = base_public
            output_dir.mkdir(parents=True, exist_ok=True)

            nef_files = list(self.archive.glob("*.NEF")) + list(
                self.archive.glob("*.nef")
            )
            for raw in nef_files:
                self._convert_raw_to_jpg(raw, output_dir)
        else:
            # Nested structure: /archive/dossier/document/image_files.NEF
            for dossier in self.archive.iterdir():
                if not dossier.is_dir():
                    continue

                self.log_message(f"Processing Dossier: {dossier.name}")

                for document in dossier.iterdir():
                    if not document.is_dir():
                        continue

                    self.log_message(f"  Processing Document: {document.name}")

                    output_dir = base_public / dossier.name / document.name
                    output_dir.mkdir(parents=True, exist_ok=True)

                    nef_files = list(document.glob("*.NEF")) + list(
                        document.glob("*.nef")
                    )

                    for raw in nef_files:
                        self._convert_raw_to_jpg(raw, output_dir)

    def _convert_raw_to_jpg(self, raw, output_dir):
        """Helper method to convert a single RAW file to JPG."""
        output_file = output_dir / f"{raw.stem}.jpg"
        self.log_message(f"    Converting: {raw.name}")

        try:
            # dcraw conversion
            dcraw_cmd = [
                self.dcraw_cmd,
                "-c",
                "-w",
                "-g",
                "2.2",
                "12.92",
                "-q",
                "3",
                "-H",
                "2",
                str(raw),
            ]
            dcraw_proc = subprocess.Popen(
                dcraw_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            # ImageMagick conversion using magick
            convert_cmd = [self.convert_cmd, "-"]
            if self.rotate != 0:
                convert_cmd.extend(["-rotate", str(self.rotate)])
            convert_cmd.extend(["-quality", str(self.quality), f"jpg:{output_file}"])

            convert_proc = subprocess.Popen(
                convert_cmd, stdin=dcraw_proc.stdout, stderr=subprocess.PIPE
            )
            dcraw_proc.stdout.close()

            _, convert_err = convert_proc.communicate()

            if convert_proc.returncode != 0:
                self.log_message(f"    ERROR: {convert_err.decode(errors='replace')}")

        except Exception as e:
            self.log_message(f"    ERROR: {str(e)}")

    def apply_metadata(self, base_public):
        """Apply XMP/IPTC metadata to all JPG images."""
        if not any(
            [
                self.creator,
                self.credit,
                self.copyright_name,
                self.usage_terms,
                self.license_url,
            ]
        ):
            self.log_message("No license metadata provided — skipping")
            return

        self.log_message("Writing XMP/IPTC metadata...")

        jpg_files = list(base_public.rglob("*.jpg")) + list(base_public.rglob("*.JPG"))

        if not jpg_files:
            self.log_message("No JPG files found to apply metadata")
            return

        cmd = [self.exiftool_cmd, "-overwrite_original"]

        if self.creator:
            cmd.extend(
                [f"-XMP-dc:Creator={self.creator}", f"-IPTC:By-line={self.creator}"]
            )
        if self.copyright_name:
            cmd.extend(
                [
                    f"-XMP-dc:Rights={self.copyright_name}",
                    f"-IPTC:CopyrightNotice={self.copyright_name}",
                ]
            )
        if self.usage_terms:
            cmd.extend(
                [
                    f"-XMP-xmpRights:UsageTerms={self.usage_terms}",
                    f"-IPTC:SpecialInstructions={self.usage_terms}",
                ]
            )
        if self.license_url:
            cmd.extend(
                [
                    f"-XMP-xmpRights:WebStatement={self.license_url}",
                    f"-IPTC:Source={self.license_url}",
                ]
            )
        if self.credit:
            cmd.append(f"-IPTC:Credit={self.credit}")

        cmd.extend([str(f) for f in jpg_files])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                self.log_message(f"Metadata applied to {len(jpg_files)} files")
            else:
                self.log_message(f"ERROR applying metadata: {result.stderr}")
        except Exception as e:
            self.log_message(f"ERROR: {str(e)}")

    def sign_all_images(self, base_public):
        """Sign all JPG images with C2PA credentials."""
        if not C2PA_AVAILABLE:
            self.log_message("ERROR: C2PA library not available, skipping signing")
            return

        self.log_message("Signing images with C2PA credentials...")

        jpg_files = list(base_public.rglob("*.jpg")) + list(base_public.rglob("*.JPG"))

        if not jpg_files:
            self.log_message("No JPG files found to sign")
            return

        signed_count = 0
        error_count = 0

        for jpg_file in jpg_files:
            try:
                self._sign_single_image(jpg_file)
                signed_count += 1
            except Exception as e:
                self.log_message(f"    ERROR signing {jpg_file.name}: {str(e)}")
                error_count += 1

        self.log_message(
            f"C2PA signing complete: {signed_count} signed, {error_count} errors"
        )

    def _sign_single_image(self, image_path):
        """Sign a single image with C2PA using correct API."""
        self.log_message(f"    Signing: {image_path.name}")

        # Create backup first for safety
        backup_path = image_path.parent / f"{image_path.stem}_backup_temp.jpg"
        temp_output = image_path.parent / f"{image_path.stem}_signed_temp.jpg"

        try:
            # Backup original
            shutil.copy2(str(image_path), str(backup_path))

            # Build manifest
            manifest_json = self._build_manifest_json(image_path)

            # Read certificate and private key as BYTES (official API expects bytes)
            with open(self.cert_path, "rb") as cert_file:
                cert_data = cert_file.read()

            with open(self.private_key_path, "rb") as key_file:
                key_data = key_file.read()

            # Map algorithm string to C2paSigningAlg enum
            alg_map = {
                "es256": C2paSigningAlg.ES256,
                "es384": C2paSigningAlg.ES384,
                "es512": C2paSigningAlg.ES512,
                "ps256": C2paSigningAlg.PS256,
                "ps384": C2paSigningAlg.PS384,
                "ps512": C2paSigningAlg.PS512,
                "ed25519": C2paSigningAlg.ED25519,
            }

            signing_alg = alg_map.get(self.signing_alg.lower(), C2paSigningAlg.ES256)

            # Create signer info using POSITIONAL arguments in this exact order:
            # C2paSignerInfo(alg, sign_cert, private_key, ta_url)
            signer_info = C2paSignerInfo(
                signing_alg,  # 1st: alg
                cert_data,  # 2nd: sign_cert (as bytes)
                key_data,  # 3rd: private_key (as bytes)
                "http://timestamp.digicert.com",  # 4th: ta_url
            )

            # Create signer from signer info
            signer = Signer.from_info(signer_info)

            # Create builder and sign using STREAMS (not file paths)
            # The official API uses streams with open() in binary mode
            with Builder(manifest_json) as builder:
                with open(image_path, "rb") as source_file:
                    with open(temp_output, "w+b") as dest_file:
                        # Sign with streams - mime_type, source, dest
                        builder.sign(
                            signer, "image/jpeg", source_file, dest_file
                        )

            # If successful, replace original with signed version
            if temp_output.exists():
                shutil.move(str(temp_output), str(image_path))
                self.log_message("      ✓ Successfully signed")
            else:
                raise RuntimeError("Signing failed - no output file created")

            # Remove backup
            if backup_path.exists():
                backup_path.unlink()

        except Exception as e:
            # Restore from backup on failure
            if backup_path.exists():
                if temp_output.exists():
                    temp_output.unlink()
                shutil.move(str(backup_path), str(image_path))
            raise e

    def _build_manifest_json(self, image_path):
        """Build C2PA manifest JSON for an image."""
        manifest = {
            "claim_generator": "Image Archive Processor/1.0",
            "title": image_path.name,
            "assertions": [],
        }

        # Add creative work assertion with metadata
        creative_work = {}

        if self.creator:
            creative_work["author"] = [{"name": self.creator}]

        if self.copyright_name:
            creative_work["copyright"] = {
                "notice": self.copyright_name,
                "year": self.year,
            }

        if self.license_url:
            creative_work["license"] = self.license_url

        if self.usage_terms:
            creative_work["usage_terms"] = self.usage_terms

        if self.credit:
            creative_work["credit_line"] = self.credit

        # Only add creative work assertion if we have metadata
        if creative_work:
            manifest["assertions"].append(
                {
                    "label": "stds.schema-org.CreativeWork",
                    "data": {
                        "@context": "https://schema.org",
                        "@type": "ImageObject",
                        **creative_work,
                    },
                }
            )

        # Add AI no train assertion
        manifest["assertions"].append(
            {
                "label": "c2pa.training-mining",
                "data": {
                    "entries": {
                        "c2pa.ai_generative_training": {"use": "notAllowed"},
                        "c2pa.ai_inference": {"use": "notAllowed"},
                        "c2pa.ai_training": {"use": "notAllowed"},
                        "c2pa.data_mining": {"use": "notAllowed"},
                    }
                },
            }
        )

        # Add actions assertion (simpler structure)
        manifest["assertions"].append(
            {
                "label": "c2pa.actions",
                "data": {
                    "actions": [
                        {
                            "action": "c2pa.edited",
                            "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/digitalCapture ",
                            "softwareAgent": "Image Archive Converter/1.0",
                        }
                    ]
                },
            }
        )

        return json.dumps(manifest, indent=2)


# Flask routes
@app.route("/")
def index(): 
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process(): 
    processor = None
    try:
        data = request.json

        processor = ImageProcessor(
            archive=data["archive"],
            output_dir=data["outputDir"],
            logs_dir=data.get("logsDir", "logs"),
            quality=int(data.get("quality", 95)),
            rotate=int(data.get("rotate", 0)),
            license_only=data.get("licenseOnly", False),
            creator=data.get("creator", ""),
            credit=data.get("credit", ""),
            copyright_name=data.get("copyright", ""),
            usage_terms=data.get("usageTerms", ""),
            license_url=data.get("licenseUrl", ""),
            sign_images=data.get("signImages", False),
            cert_path=data.get("certPath", ""),
            private_key_path=data.get("privateKeyPath", ""),
            signing_alg=data.get("signingAlg", "es256"),
        )

        processor.check_dependencies()
        processor.validate()
        log = processor.process()

        return jsonify({"success": True, "log": log})

    except Exception as e:
        log_content = (
            "\n".join(processor.log) if processor and hasattr(processor, "log") else ""
        )
        return jsonify({"success": False, "error": str(e), "log": log_content})


def run_cli():
    """Run the application in CLI mode."""
    parser = argparse.ArgumentParser(
        description="Archive Converter - Bulk Convert Archive images and apply metadata"
    )

    parser.add_argument("--archive", required=True, help="Root archive folder (input)")
    parser.add_argument(
        "--output", required=True, help="Output folder for processed images"
    )
    parser.add_argument("--logs", default="logs", help="Logs directory (default: logs)")
    parser.add_argument("--quality", type=int, default=95, help="JPEG quality (1-100)")
    parser.add_argument(
        "--rotate", type=int, default=0, help="Rotation angle in degrees"
    )
    parser.add_argument(
        "--license-only", action="store_true", help="Only apply license metadata"
    )

    parser.add_argument("--creator", default="", help="Creator / author")
    parser.add_argument("--credit", default="", help="Credit line")
    parser.add_argument("--copyright", default="", help="Copyright holder")
    parser.add_argument("--usage-terms", default="", help="License / usage terms")
    parser.add_argument("--license-url", default="", help="License URL")

    # C2PA signing arguments
    parser.add_argument(
        "--sign-images", action="store_true", help="Sign images with C2PA"
    )
    parser.add_argument("--cert", default="", help="Path to C2PA certificate file")
    parser.add_argument("--private-key", default="", help="Path to private key file")
    parser.add_argument(
        "--signing-alg",
        default="es256",
        choices=["es256", "es384", "es512", "ps256", "ps384", "ps512", "ed25519"],
        help="Signing algorithm (default: es256)",
    )

    args = parser.parse_args(sys.argv[2:])

    try:
        processor = ImageProcessor(
            archive=args.archive,
            output_dir=args.output,
            logs_dir=args.logs,
            quality=args.quality,
            rotate=args.rotate,
            license_only=args.license_only,
            creator=args.creator,
            credit=args.credit,
            copyright_name=args.copyright,
            usage_terms=args.usage_terms,
            license_url=args.license_url,
            sign_images=args.sign_images,
            cert_path=args.cert,
            private_key_path=args.private_key,
            signing_alg=args.signing_alg,
        )

        processor.check_dependencies()
        processor.validate()
        processor.process()

    except Exception as e:
        print(f"[ERROR] {str(e)}", file=sys.stderr)
        sys.exit(1)


def run_web():
    """Run the application in web server mode."""
    log = logging.getLogger("werkzeug")
    log.disabled = True
    log.setLevel(logging.ERROR)

    cli = sys.modules["flask.cli"]
    cli.show_server_banner = lambda *x: None

    print("Starting Archive Conversion Tool...")
    print("Open your browser: http://localhost:3932")
    Timer(1, webbrowser.open_new, args=("http://localhost:3932",)).start()
    print("\nTo stop the server, press Ctrl+C")
    app.run(host="0.0.0.0", port=3932, debug=False, use_reloader=False)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--":
        run_cli()
    else:
        run_web()
