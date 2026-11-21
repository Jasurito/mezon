"""Pre-generated character speech (docs/TTS.md).

Runtime (backend image, no ML dependencies): ``voices`` decides who speaks with which voice, ``catalog`` reads the
audio manifests from object storage and gives the API an ``audio_url`` for each spoken line.
Build tool (``python -m app.tts``, extra ``[tts]``: torch, lameenc, boto3): ``lines``, ``text``, ``synth``,
``build`` and ``storage`` turn scenario texts into MP3 files and upload them.
"""
