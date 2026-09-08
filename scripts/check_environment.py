import platform

import torch


def check_environment():
    print("=" * 60)
    print("Kazakh Morphology Project — Environment Report")
    print("=" * 60)
    print(f"Python: {platform.python_version()}")
    print(f"Platform: {platform.platform()}")
    print(f"Processor: {platform.processor()}")
    print(f"PyTorch: {torch.__version__}")
    print(f"Torch CUDA runtime: {torch.version.cuda}")
    print(f"CUDA available: {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        props = torch.cuda.get_device_properties(0)
        print(f"VRAM: {props.total_memory / (1024**2):.0f} MB")
        print(f"BF16 supported: {torch.cuda.is_bf16_supported()}")
        print(f"Compute capability: {props.major}.{props.minor}")
        print(f"Multiprocessor count: {props.multi_processor_count}")
    else:
        print("No CUDA GPU available")

    try:
        import transformers
        print(f"Transformers: {transformers.__version__}")
    except ImportError:
        print("Transformers: NOT INSTALLED")

    try:
        import accelerate
        print(f"Accelerate: {accelerate.__version__}")
    except ImportError:
        print("Accelerate: NOT INSTALLED")

    try:
        import bitsandbytes
        print(f"BitsAndBytes: {bitsandbytes.__version__}")
    except ImportError:
        print("BitsAndBytes: NOT INSTALLED")

    print("=" * 60)


if __name__ == "__main__":
    check_environment()
