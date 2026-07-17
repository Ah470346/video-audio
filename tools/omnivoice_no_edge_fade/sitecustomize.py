"""Disable OmniVoice's hard-coded 100 ms edge fade/pad for batch rendering.

The upstream batch CLI always calls ``fade_and_pad_audio`` after generation.
For long-form audiobooks rendered as many external chunks, that fade lands on
the first syllable of every chunk.  This shim is loaded through PYTHONPATH by
``convert_script_to_audio_k2fsa.py`` and leaves the rest of OmniVoice unchanged.
"""

import os


def _install():
    if os.environ.get("K2FSA_OMNIVOICE_NO_EDGE_FADE") != "1":
        return
    try:
        import omnivoice.utils.audio as audio_utils
    except Exception:
        return

    def no_edge_fade(audio, *args, **kwargs):
        return audio

    os.environ["K2FSA_OMNIVOICE_NO_EDGE_FADE_ACTIVE"] = "1"
    audio_utils.fade_and_pad_audio = no_edge_fade
    try:
        import omnivoice.models.omnivoice as omnivoice_model
    except Exception:
        return
    omnivoice_model.fade_and_pad_audio = no_edge_fade

    try:
        import torch
    except Exception:
        return

    original_from_pretrained = omnivoice_model.OmniVoice.from_pretrained

    def mps_safe_from_pretrained(*args, **kwargs):
        device_map = kwargs.get("device_map")
        dtype = kwargs.get("dtype")
        if device_map == "mps" and dtype == torch.float16:
            kwargs = dict(kwargs)
            kwargs["dtype"] = torch.float32
            os.environ["K2FSA_OMNIVOICE_MPS_SAFE_DTYPE_ACTIVE"] = "float32"
        return original_from_pretrained(*args, **kwargs)

    omnivoice_model.OmniVoice.from_pretrained = mps_safe_from_pretrained


_install()
