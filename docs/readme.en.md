# ARCON – Archive Conversion Tool

_Este documento também está disponível em [Português](../readme.md)._

## Table of Contents

- What is ARCON?
- Key Features
- About the Project
- Getting Started

## What is ARCON?

ARCON is a open-source, platform-independent image processing tool designed to support archival digitization workflows by combining image format conversion and metadata embedding into a single process.

## Key Features

- Preserve hierarchical folder structure  
- Batch-convert RAW images to JPEG  
- Embed licensing and authorship metadata  
- Discourage AI-based misuse via metadata  
- Browser-based UI and CLI mode  

## About the Project

When digitizing a physical archive, it is essential to preserve a high-quality digital twin that remains as faithful as possible to the original material. Many digital cameras capture images in RAW formats, also refered to as "Digital Negatives". This is so, because the RAW format retain extensive metadata from the camera sensor. For this reason, RAW files may be used in professional archival digitization and may be suitable for forensic and evidentiary purposes.

However, RAW formats are not appropriate for public dissemination. Most web platforms and social media services do not support them natively, which limits accessibility and reuse. As a result, archives intended for online access typically require conversion to widely supported formats such as JPEG.

At the same time, the publication of digitized archives raises concerns related to licensing, authorship, copyright, and acceptable use, particularly in the context of modern generative artificial intelligence systems.

ARCON combines image format conversion and metadata embedding for this purpose.

## Getting Started

### Installation

```sh
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Building

```sh
pyinstaller arcon.spec
```

## Usage

```sh
./arcon
```

### CLI

```sh
./arcon -- -h
```
