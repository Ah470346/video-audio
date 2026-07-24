import math
import contextlib
import io
import tempfile
import unittest
import wave
from pathlib import Path
from types import SimpleNamespace

import convert_script_to_audio_voxcpm as renderer
import convert_script_to_audio_voxcpm_kaggle as kaggle_launcher
import convert_short_script_to_audio_voxcpm as short_renderer
import voxcpm_story_core as core
from tools import prepare_kaggle_voxcpm_job as prepare
from tools import prepare_kaggle_voxcpm_short_job as prepare_short


def ctc_args(**overrides):
    values = {
        "verify_ctc_probe": True,
        "verify_ctc_out_of_text_ms": 120,
        "verify_ctc_out_of_text_chars": 2,
        "verify_ctc_veto_similarity": 0.98,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class FakeCtcProbe:
    """Stands in for the wav2vec2 session; ``greedy`` is keyed by frame window."""

    error = None
    frames_per_sec = 50.0

    def __init__(self, aligned, greedy, full_text):
        self.aligned = aligned
        self.greedy = greedy
        self.full_text = full_text

    def load(self):
        return True

    def emissions(self, _wav_path):
        return "emissions"

    def greedy_text(self, _emissions, start_frame=None, end_frame=None):
        if start_frame is None and end_frame is None:
            return self.full_text
        return self.greedy.get((start_frame, end_frame), "")

    def align(self, _emissions, _text):
        return self.aligned


def write_sine_fixture(path, segments, sample_rate=16000):
    samples = []
    for duration, amplitude, frequency in segments:
        count = int(sample_rate * duration)
        for index in range(count):
            if amplitude <= 0.0:
                samples.append(0)
            else:
                value = amplitude * math.sin(2.0 * math.pi * frequency * index / sample_rate)
                samples.append(max(-32767, min(32767, int(value * 32767))))
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(b"".join(sample.to_bytes(2, "little", signed=True) for sample in samples))


class VoxCPMStoryCoreTests(unittest.TestCase):
    def test_normalize_vietnamese_tokens_for_tts(self):
        text = "Tin nhan gui luc 19:45, ma ho so ADN 03/2024."

        normalized = core.normalize_for_tts(text)

        self.assertIn("mười chín giờ bốn mươi lăm", normalized)
        self.assertIn("a đê en", normalized)
        self.assertNotIn("19:45", normalized)

    def test_plan_chunks_preserves_sentence_boundaries(self):
        chunks = core.plan_chunks(
            "Tôi đặt tờ đơn xuống. Anh không nhìn tôi. Cửa sau lưng khép lại.",
            max_chars=42,
            max_words=10,
            min_words=1,
        )

        self.assertGreaterEqual(len(chunks), 2)
        self.assertTrue(all(chunk["text"].endswith((".", "?", "!")) for chunk in chunks))

    def test_exact_asr_swallowed_syllable_is_warning_not_fault(self):
        words = []
        text_tokens = ["mot", "hai", "ba", "bon", "nam", "sau", "bay", "tam", "chin", "muoi"]
        segments = []
        cursor = 0.0
        for index, token in enumerate(text_tokens):
            amplitude = 0.12 if token == "nam" else 0.40
            segments.append((0.16, amplitude, 220.0))
            segments.append((0.08, 0.0, 220.0))
            words.append({"word": token, "start": cursor, "end": cursor + 0.16})
            cursor += 0.24
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "swallowed.wav"
            write_sine_fixture(path, segments)

            _score, reason = core.timing_defects_from_words(
                str(path),
                " ".join(text_tokens),
                words,
                "unused",
                retry_timing_anomalies=True,
                retry_text_mismatch=True,
                min_local_wps=1.0,
                max_local_wps=10.0,
            )

            self.assertTrue(reason.startswith("ok"), reason)
            self.assertIn("warnings: swallowed", reason)

    def test_exact_asr_timing_anomaly_is_warning_not_fault(self):
        words = []
        text_tokens = ["mot", "hai", "ba", "bon", "nam"]
        cursor = 0.0
        for token in text_tokens:
            words.append({"word": token, "start": cursor, "end": cursor + 0.04})
            cursor += 0.05
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fast.wav"
            write_sine_fixture(path, [(0.35, 0.35, 220.0)])

            _score, reason = core.timing_defects_from_words(
                str(path),
                " ".join(text_tokens),
                words,
                "unused",
                retry_timing_anomalies=True,
                retry_text_mismatch=True,
                min_local_wps=1.0,
                max_local_wps=10.0,
            )

            self.assertTrue(reason.startswith("ok"), reason)
            self.assertIn("warnings: fast local tempo", reason)

    def test_repeated_inserted_word_is_hard_by_default(self):
        args = SimpleNamespace(
            verify_inserted_words=3,
            verify_repeat_max_ngram=4,
            verify_repeat_severity="hard",
        )
        words = [{"word": word} for word in "Tôi tôi muốn nói".split()]

        defect = renderer.duplicate_text_defect("Tôi còn muốn nói", words, args)

        self.assertIsNotNone(defect)
        self.assertEqual(defect[0], "hard")

    def test_text_lock_defect_uses_cfg_two_first(self):
        result = {"defects": [{"type": "repetition", "severity": "hard", "message": "repeated"}]}

        ladder = renderer.retry_ladder_for_result(result)

        self.assertEqual(ladder[0]["cfg_value"], 2.0)

    def test_renderer_uses_three_verify_retries_by_default(self):
        args = renderer.build_parser().parse_args(["--input", "story.md"])

        self.assertEqual(args.max_verify_retries, 3)

    def test_ctc_probe_flags_out_of_text_tail_audio(self):
        """Chunk 0038's real failure: junk after the sentence that full-text
        ASR ignores because it never becomes a word."""
        args = ctc_args()
        probe = FakeCtcProbe(
            aligned=[
                {"word": "tôi", "start_frame": 5, "end_frame": 20, "start": 0.1, "end": 0.4, "score": 0.99},
                {"word": "về", "start_frame": 22, "end_frame": 40, "start": 0.44, "end": 0.8, "score": 0.98},
            ],
            greedy={(46, None): "neo lua mũ n hốt"},
            full_text="tôi về",
        )

        metrics, defects = renderer.ctc_probe_metrics("Tôi về.", "unused.wav", args, probe)

        hard = [defect for defect in defects if defect[1] == "hard"]
        self.assertEqual(len(hard), 1)
        self.assertEqual(hard[0][0], "ctc_out_of_text_audio")
        self.assertEqual(hard[0][3]["position"], "tail")
        self.assertEqual(metrics["out_of_text"]["tail"], "neo lua mũ n hốt")

    def test_ctc_probe_clean_tail_produces_no_defect(self):
        args = ctc_args()
        probe = FakeCtcProbe(
            aligned=[
                {"word": "tôi", "start_frame": 5, "end_frame": 20, "start": 0.1, "end": 0.4, "score": 0.99},
                {"word": "về", "start_frame": 22, "end_frame": 40, "start": 0.44, "end": 0.8, "score": 0.98},
            ],
            greedy={},
            full_text="tôi về",
        )

        _metrics, defects = renderer.ctc_probe_metrics("Tôi về.", "unused.wav", args, probe)

        self.assertEqual(defects, [])

    def test_ctc_probe_vetoes_when_context_free_read_is_exact(self):
        """Chunk 0071: the energy heuristic called a word swallowed while both
        Whisper and a language-model-free CTC read transcribed it."""
        args = ctc_args()
        probe = FakeCtcProbe(aligned=[], greedy={}, full_text="cô là người thông minh")

        metrics, _defects = renderer.ctc_probe_metrics(
            "Cô là người thông minh.", "unused.wav", args, probe
        )

        self.assertTrue(metrics["veto"])

    def test_ctc_probe_does_not_veto_when_read_disagrees(self):
        args = ctc_args()
        probe = FakeCtcProbe(aligned=[], greedy={}, full_text="cô là người")

        metrics, _defects = renderer.ctc_probe_metrics(
            "Cô là người thông minh.", "unused.wav", args, probe
        )

        self.assertFalse(metrics["veto"])

    def test_ctc_probe_unavailable_warns_and_never_fails(self):
        args = ctc_args()

        metrics, defects = renderer.ctc_probe_metrics("Tôi về.", "unused.wav", args, None)

        self.assertFalse(metrics["available"])
        self.assertEqual([defect[1] for defect in defects], ["warn"])

    def test_qc_change_does_not_share_a_hash_with_render_params(self):
        """A QC threshold tweak must not invalidate rendered audio."""
        base = renderer.build_parser().parse_args(["--input", "story.md"])
        tweaked = renderer.build_parser().parse_args(
            ["--input", "story.md", "--verify_ctc_veto_similarity", "0.90"]
        )

        self.assertEqual(renderer.render_sha256(base), renderer.render_sha256(tweaked))
        self.assertNotEqual(renderer.qc_sha256(base), renderer.qc_sha256(tweaked))

    def test_render_change_changes_the_render_hash(self):
        base = renderer.build_parser().parse_args(["--input", "story.md"])
        tweaked = renderer.build_parser().parse_args(
            ["--input", "story.md", "--cfg_value", "1.9"]
        )

        self.assertNotEqual(renderer.render_sha256(base), renderer.render_sha256(tweaked))

    def test_long_renderer_has_no_control_argument(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                renderer.build_parser().parse_args(["--input", "story.md", "--control", "slow"])


class VoxCPMShortRendererTests(unittest.TestCase):
    def test_short_entrypoint_defaults_are_reference_controlled(self):
        args = renderer.build_parser().parse_args(
            [*short_renderer.SHORT_EXPRESSIVE_DEFAULT_ARGS, "--input", "story.md"]
        )
        short_args, _rest = short_renderer.build_short_parser().parse_known_args([])

        self.assertEqual(args.clone_mode, "reference")
        self.assertEqual(args.max_chunk_chars, 80)
        self.assertEqual(args.max_chunk_words, 14)
        self.assertEqual(args.cfg_value, 2.0)
        self.assertEqual(args.inference_timesteps, 16)
        self.assertIn("expressive Vietnamese", short_args.control)

    def test_style_directive_is_metadata_not_spoken_text(self):
        text = "@style slow, fearful\nĐừừng...\nđừng mở cửa.\n\n@style off\nTôi nghe rồi."

        blocks = short_renderer.parse_style_blocks(text, short_renderer.DEFAULT_CONTROL)

        self.assertEqual(blocks[0]["style_control"], "slow, fearful")
        self.assertIsNone(blocks[1]["style_control"])
        self.assertNotIn("@style", blocks[0]["text"])

    def test_short_prepare_chunks_keeps_style_out_of_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "short.md"
            path.write_text("@style slow, fearful\nĐừừng...\nđừng mở cửa.\n", encoding="utf-8")
            args = renderer.build_parser().parse_args(
                [*short_renderer.SHORT_EXPRESSIVE_DEFAULT_ARGS, "--input", str(path)]
            )
            short_renderer.ACTIVE_DEFAULT_CONTROL = short_renderer.DEFAULT_CONTROL

            _normalized, _word_count, chunks = short_renderer.prepare_chunks(args)

        self.assertTrue(chunks)
        self.assertEqual(chunks[0]["style_control"], "slow, fearful")
        self.assertNotIn("@style", chunks[0]["text"])
        self.assertNotIn("slow", chunks[0]["text"].lower())


class VoxCPMPrepareJobTests(unittest.TestCase):
    def test_bundle_ships_the_ctc_probe(self):
        self.assertEqual(
            prepare.COPY_FILES,
            [
                "convert_script_to_audio_voxcpm.py",
                "voxcpm_story_core.py",
                "voxcpm_ctc_probe.py",
            ],
        )

    def test_prepare_uses_three_verify_retries_by_default(self):
        args = prepare.build_parser().parse_args(
            [
                "--kernel-id", "user/kernel",
                "--title", "kernel",
                "--job-dir", "/tmp/kernel",
                "--input", "story.md",
            ]
        )

        self.assertEqual(args.max_verify_retries, 3)

    def test_prepare_never_installs_whisperx(self):
        """whisperx pins faster-whisper==1.0.0 and ctranslate2==4.4.0, which
        contradict the faster-whisper pin here. A single pip install of both
        fails to resolve and takes the whole kernel down before rendering."""
        names = [spec.split("==")[0] for spec in prepare.DEFAULT_PIP_PACKAGES]

        self.assertNotIn("whisperx", names)
        self.assertIn("faster-whisper==1.2.1", prepare.DEFAULT_PIP_PACKAGES)

    def test_prepare_passes_the_ctc_probe_model_through(self):
        args = prepare.build_parser().parse_args(
            [
                "--kernel-id", "user/kernel",
                "--title", "kernel",
                "--job-dir", "/tmp/kernel",
                "--input", "story.md",
            ]
        )

        self.assertTrue(args.verify_ctc_probe)
        self.assertEqual(args.verify_ctc_model, prepare.DEFAULT_CTC_MODEL)

    def test_prepare_attaches_model_dataset_cache_by_default(self):
        args = prepare.build_parser().parse_args(
            [
                "--kernel-id", "user/kernel",
                "--title", "kernel",
                "--job-dir", "/tmp/kernel",
                "--input", "story.md",
            ]
        )

        self.assertIn(prepare.DEFAULT_MODEL_DATASET_SOURCE, args.dataset_source)


class VoxCPMShortPrepareJobTests(unittest.TestCase):
    def test_short_prepare_defaults_to_adam_reference_control(self):
        args = prepare_short.build_parser().parse_args(
            [
                "--job-dir", "/tmp/kernel",
                "--input", "short.md",
            ]
        )

        self.assertEqual(args.voice, "adam")
        self.assertEqual(args.clone_mode, "reference")
        self.assertEqual(args.max_chunk_chars, 80)
        self.assertEqual(args.cfg_value, 2.0)
        self.assertIn("expressive Vietnamese", args.control)
        self.assertIn(prepare_short.base.DEFAULT_MODEL_DATASET_SOURCE, args.dataset_source)

    def test_short_prepare_manifest_runs_short_entrypoint(self):
        args = prepare_short.build_parser().parse_args(
            [
                "--job-dir", "/tmp/kernel",
                "--input", "short.md",
            ]
        )
        prepare_short.base.resolve_voice_args(args)

        render_args = prepare_short.render_args(args, "job_inputs/short.md", "job_inputs/adam.wav")

        self.assertIn("convert_short_script_to_audio_voxcpm.py", prepare_short.COPY_FILES)
        self.assertIn("convert_script_to_audio_voxcpm.py", prepare_short.COPY_FILES)
        self.assertIn("--control", render_args)
        self.assertIn("--retry_badcase_ratio_threshold", render_args)


class KaggleLauncherTests(unittest.TestCase):
    def test_replace_arg_value_updates_existing_flag(self):
        args = ["--model", "openbmb/VoxCPM2", "--verify_asr_model", "large-v3"]

        resolved = kaggle_launcher.replace_arg_value(args, "--verify_asr_model", "/cache/asr")

        self.assertEqual(resolved, ["--model", "openbmb/VoxCPM2", "--verify_asr_model", "/cache/asr"])

    def test_replace_arg_value_appends_missing_flag(self):
        resolved = kaggle_launcher.replace_arg_value(["--model", "openbmb/VoxCPM2"], "--verify_ctc_model", "/cache/ctc")

        self.assertEqual(resolved, ["--model", "openbmb/VoxCPM2", "--verify_ctc_model", "/cache/ctc"])

    def test_find_snapshot_checks_dataset_title_alias(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            snapshot = root / "tts-and-qc-models" / "openbmb_voxcpm2"
            snapshot.mkdir(parents=True)
            original_path = kaggle_launcher.Path

            def fake_path(value):
                return root if value == "/kaggle/input" else original_path(value)

            try:
                kaggle_launcher.Path = fake_path
                dataset_root, direct_path, archive_path = kaggle_launcher.find_snapshot_in_dataset_roots(
                    "openbmb_voxcpm2"
                )
            finally:
                kaggle_launcher.Path = original_path

        self.assertEqual(dataset_root.name, "tts-and-qc-models")
        self.assertEqual(direct_path.name, "openbmb_voxcpm2")
        self.assertIsNone(archive_path)


if __name__ == "__main__":
    unittest.main()
