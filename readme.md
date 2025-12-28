# ARCON – Archive Conversion Tool

_Este documento está também disponível em [Portuguese](./docs/readme.pt.md)._

_to build this project refer to [Build](./docs/BUILD.md)

When digitizing a physical archive, it is essential to preserve a high-quality digital twin of the original material. Some digital cameras capture images in RAW formats, which preserve the maximum amount of information recorded by the camera sensor, including detailed technical metadata. For this reason, RAW files can be used in digital archives and are often considered suitable for forensic examinations.

However, RAW formats are not appropriate for public distribution, as most online platforms and social media services do not offer native support for them. This makes conversion to other formats that are widely accepted on the internet necessary in order to facilitate access to and dissemination of the content.

With the dissemination of digitized archives, concerns arise regarding licensing, authorship, copyright, and proper use of the content, especially in light of advances in generative artificial intelligence technologies, which make it possible to create versions that modify the original content of documents. One strategy to mitigate misuse, including use by crawlers and AI systems, of archives distributed on the internet is the incorporation of licensing, ownership, and AI-usage restriction metadata directly into the image files.

## What is ARCON?

**ARCON** is a platform-independent archive conversion tool designed to support archival digitization workflows by combining format conversion and metadata application into a single process.

ARCON was developed to:

- Preserve the original hierarchical structure of the digitized archive  
- Batch-convert images into a defined output format  
- Embed licensing, authorship, and copyright metadata directly into the converted files  
- Add metadata aimed at limiting the use of content by AI systems  

## Why not use existing conversion tools?

Most existing bulk conversion tools:

- Are not designed for archival workflows  
- Do not preserve the hierarchical folder structure and original folder names  
- Do not integrate image conversion and licensing metadata application into a single workflow  
- Do not implement techniques aimed at restricting use by AI systems  

ARCON was created to address these gaps, with a focus on archival integrity, controlled dissemination, and responsible use of content.
