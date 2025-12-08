# Docker Image Size Analysis

The current Docker image size (~15 GB) is driven primarily by the `open-webui` package and its deep learning dependencies.

## Top 5 Largest Dependencies

1.  **PyTorch (`torch`, `torchvision`, `torchaudio`)**
    *   **Estimated Size**: 2 GB - 5 GB (depending on whether CUDA/GPU support is included).
    *   **Usage**: Core machine learning framework used by OpenWebUI for local embeddings (RAG), speech-to-text (Whisper), and image generation features.
    *   **Impact**: This is the single largest component. By default, `pip install open-webui` may pull the version compatible with GPU, which includes massive NVIDIA CUDA binaries.

2.  **NVIDIA CUDA Libraries (`nvidia-cudnn-cu12`, `nvidia-cuda-runtime-cu12`, etc.)**
    *   **Estimated Size**: 1 GB - 4 GB.
    *   **Usage**: Required for GPU acceleration of PyTorch models.
    *   **Impact**: Even if running on CPU, `pip` might install these if the default `torch` wheel includes them or lists them as dependencies.

3.  **Transformers (`transformers`) & Sentence Transformers (`sentence-transformers`)**
    *   **Estimated Size**: ~200 MB - 500 MB (libraries only, not including cached models).
    *   **Usage**: Used for handling local Large Language Models (LLMs) and embedding models for semantic search (RAG).

4.  **ChromaDB (`chromadb`)**
    *   **Estimated Size**: ~100 MB - 300 MB (build dependencies and onnxruntime).
    *   **Usage**: Vector database used to store and retrieve document embeddings for RAG.

5.  **Misc ML Libraries (`pandas`, `numpy`, `scipy`)**
    *   **Estimated Size**: ~100 MB - 200 MB combined.
    *   **Usage**: Data manipulation and numerical operations required by the ML stack.

## Conclusion & Recommendation

To reach the target size of **25 MB - 250 MB**, it is **impossible** to include the full `open-webui` backend package, as it inherently requires PyTorch and other heavy ML libraries.

**Options to resolve:**

1.  **Standalone MCP Bridge (Recommended for Size Constraint)**: 
    *   Remove `open-webui` from this container.
    *   Run only the `src/openwebui_bridge.py` (or similar) as a lightweight FastMCP server.
    *   Connect this lightweight container to an existing OpenWebUI instance running elsewhere.
    *   **Resulting Size**: ~150 MB - 250 MB.

2.  **CPU-Only OpenWebUI (Partial Reduction)**:
    *   Force install CPU-only versions of PyTorch.
    *   **Resulting Size**: ~1.5 GB - 3 GB (still exceeds strict 250 MB limit).
