"""
Audio generation service using Piper TTS.
Falls back gracefully if Piper is not installed.
"""
import logging
import os
import uuid
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


class AudioService:
    """Piper TTS audio generation."""

    def _get_piper_binary(self) -> Optional[str]:
        """Find the piper executable."""
        # Try pip-installed piper-tts
        import importlib.util
        if importlib.util.find_spec("piper") is not None:
            return "piper"
        # Try system PATH
        import shutil
        return shutil.which("piper")

    def _get_voice_model(self, voice: str) -> Optional[str]:
        """Return path to .onnx voice file for given voice name."""
        voices_dir = settings.get_piper_voices_dir()
        # Look for voice.onnx
        candidates = [
            voices_dir / f"{voice}.onnx",
            voices_dir / f"{voice.replace('-', '_')}.onnx",
        ]
        for c in candidates:
            if c.exists():
                return str(c)
        return None

    async def generate(
        self,
        text: str,
        upload_id: int,
        voice: Optional[str] = None,
        speed: float = 1.0,
    ) -> Optional[str]:
        """
        Generate audio from text using Piper TTS.
        Returns audio_id if successful, None otherwise.
        """
        voice = voice or settings.PIPER_VOICE
        audio_dir = settings.get_audio_dir()
        audio_dir.mkdir(parents=True, exist_ok=True)

        audio_id = f"audio_{uuid.uuid4().hex}"
        audio_path = audio_dir / f"{audio_id}.wav"

        # Try Piper TTS
        piper_bin = self._get_piper_binary()
        if piper_bin:
            voice_model = self._get_voice_model(voice)
            if voice_model:
                try:
                    result = subprocess.run(
                        [piper_bin, "--model", voice_model,
                         "--output_file", str(audio_path),
                         "--length_scale", str(1.0 / max(speed, 0.1))],
                        input=text.encode("utf-8"),
                        capture_output=True,
                        timeout=120,
                    )
                    if result.returncode == 0 and audio_path.exists():
                        logger.info(f"Piper TTS: generated {audio_path}")
                        return self._save_record(audio_id, str(audio_path), voice, speed)
                    else:
                        logger.warning(f"Piper returned code {result.returncode}: {result.stderr.decode()}")
                except subprocess.TimeoutExpired:
                    logger.warning("Piper TTS timed out")
                except Exception as e:
                    logger.warning(f"Piper TTS error: {e}")
            else:
                logger.warning(f"Piper voice model not found: {voice}. Download with: "
                               f"piper --download-voice {voice} --data-dir {settings.PIPER_VOICES_DIR}")

        # Fallback: try Windows SAPI (win32com) for fully offline TTS
        try:
            import importlib
            win32com_mod = importlib.import_module("win32com.client")
            wav_path = audio_dir / f"{audio_id}.wav"
            sapi = win32com_mod.Dispatch("SAPI.SpVoice")
            stream = win32com_mod.Dispatch("SAPI.SpFileStream")
            stream.Open(str(wav_path), 3)  # SSFMCreateForWrite = 3
            sapi.AudioOutputStream = stream
            sapi.Rate = max(-10, min(10, int((speed - 1.0) * 5)))  # -10..10
            sapi.Speak(text[:8000])
            stream.Close()
            if wav_path.exists() and wav_path.stat().st_size > 100:
                logger.info(f"Windows SAPI TTS: generated {wav_path}")
                return self._save_record(audio_id, str(wav_path), "sapi", speed)
        except (ImportError, ModuleNotFoundError):
            pass
        except Exception as e:
            logger.warning(f"Windows SAPI TTS failed: {e}")

        # Fallback: try gTTS if available (requires internet)
        try:
            import importlib
            gtts_mod = importlib.import_module("gtts")
            gTTS = getattr(gtts_mod, "gTTS")
            tts = gTTS(text=text[:5000], lang="en", slow=(speed < 0.75))
            mp3_path = audio_dir / f"{audio_id}.mp3"
            tts.save(str(mp3_path))
            if mp3_path.exists():
                logger.info(f"gTTS fallback: generated {mp3_path}")
                return self._save_record(audio_id, str(mp3_path), "gtts", speed)
        except (ImportError, ModuleNotFoundError):
            pass
        except Exception as e:
            logger.warning(f"gTTS fallback failed: {e}")

        logger.warning("No TTS engine available. Audio generation skipped.")
        return None

    def _save_record(self, audio_id: str, audio_path: str, voice: str, speed: float) -> str:
        """Return audio_id (DB record saved by caller)."""
        return audio_id

    def get_audio_path(self, audio_id: str) -> Optional[str]:
        """Find the audio file for a given audio_id."""
        audio_dir = settings.get_audio_dir()
        for ext in [".wav", ".mp3"]:
            path = audio_dir / f"{audio_id}{ext}"
            if path.exists():
                return str(path)
        return None


audio_service = AudioService()

