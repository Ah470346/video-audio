import unittest
import re
import os
import tempfile
from array import array
from types import SimpleNamespace
from unittest import mock

import omnivoice_story_core as tts


class FakeStrictSession:
    def __init__(self, aligned_words, secondary_words):
        self.aligned_words = aligned_words
        self.secondary_words = secondary_words
        self.last_error = None

    def align(self, _audio, _text, _model, batch_size=1):
        return self.aligned_words

    def transcribe(
            self, _audio, _model, cpu_threads=4, clip_timestamps=None):
        return {"segments": [{"words": self.secondary_words}]}


class VerificationDecisionTests(unittest.TestCase):
    def test_fast_verify_rejects_flag_even_with_perfect_asr_score(self):
        self.assertFalse(
            tts.verification_passed(
                1.0,
                "swallowed 'Chỉ' at 1.2s (-8.5 dB under median)",
                verify=False,
                fast_verify=True,
                threshold=0.995,
            )
        )

    def test_fast_verify_accepts_explicit_ok_independent_of_raw_score(self):
        self.assertTrue(
            tts.verification_passed(
                0.957,
                "ok (fast verify 0.957)",
                verify=False,
                fast_verify=True,
                threshold=0.995,
            )
        )

    def test_swallowed_syllable_check_works_without_numpy(self):
        samples = array("f")
        words = []
        sample_rate = 100
        for index in range(10):
            amplitude = 0.1 if index == 4 else 1.0
            samples.extend([amplitude] * 10)
            words.append({"word": f"w{index}", "start": index / 10, "end": (index + 1) / 10})

        with mock.patch.object(tts, "np", None), mock.patch.object(
            tts, "_decode_samples", return_value=samples
        ):
            result = tts.swallowed_syllable(
                "unused.wav", words, sample_rate=sample_rate, hop=5, frame=5
            )

        self.assertIsNotNone(result)
        self.assertEqual(result[1], "w4")
        self.assertLess(result[0], -15.0)

    def test_full_verify_uses_similarity_threshold(self):
        self.assertFalse(
            tts.verification_passed(
                0.994,
                "ASR similarity 0.994",
                verify=True,
                fast_verify=True,
                threshold=0.995,
            )
        )
        self.assertTrue(
            tts.verification_passed(
                0.995,
                "ASR similarity 0.995",
                verify=True,
                fast_verify=True,
                threshold=0.995,
            )
        )

    def test_low_confidence_word_requires_acoustic_stretch(self):
        words = [
            {"word": "bình", "start": 0.0, "end": 0.2, "probability": 0.99},
            {"word": "thường", "start": 0.2, "end": 0.4, "probability": 0.70},
            {"word": "sẽ", "start": 0.4, "end": 0.8, "probability": 0.85},
            {"word": "đọc", "start": 0.8, "end": 1.0, "probability": 0.99},
            {"word": "đúng", "start": 1.0, "end": 1.2, "probability": 0.99},
        ]

        result = tts.low_confidence_word(words)

        self.assertIsNotNone(result)
        self.assertEqual(result[1], "sẽ")
        self.assertGreaterEqual(result[2], 1.7)

    def test_low_confidence_ignores_word_after_written_pause(self):
        words = [
            {"word": "ngày", "start": 0.0, "end": 0.2, "probability": 0.99},
            {"word": "và", "start": 0.2, "end": 0.6, "probability": 0.40},
            {"word": "tôi", "start": 0.6, "end": 0.8, "probability": 0.99},
        ]

        result = tts.low_confidence_word(
            words, expected_text="hai mươi ngày, và tôi biết trước"
        )

        self.assertIsNone(result)

    def test_local_tempo_detects_fast_burst(self):
        words = [
            {
                "word": f"w{index}",
                "start": index * 0.12,
                "end": index * 0.12 + 0.1,
                "probability": 1.0,
            }
            for index in range(5)
        ]

        result = tts.local_tempo_defect(words)

        self.assertIsNotNone(result)
        self.assertEqual(result[0], "fast")

    def test_borderline_similarity_uses_adaptive_clause_probe(self):
        expected_words = [
            f"token{chr(97 + index // 26)}{chr(97 + index % 26)}"
            for index in range(50)
        ]
        heard_words = expected_words[:-1]
        words = [
            {"word": word, "start": index * 0.2, "end": index * 0.2 + 0.2,
             "probability": 1.0}
            for index, word in enumerate(heard_words)
        ]
        payload = {"segments": [{"words": words}]}
        with mock.patch.object(tts, "_whisper_bin", return_value="mlx_whisper"), \
             mock.patch.object(tts, "_run_whisper", return_value=payload), \
             mock.patch.object(tts, "swallowed_syllable", return_value=None), \
             mock.patch.object(tts, "asr_similarity", return_value=0.98) as probe:
            score, reason = tts.timing_defects(
                "unused.wav",
                " ".join(expected_words),
                "model",
                adaptive=True,
                adaptive_floor=0.995,
                retry_text_mismatch=True,
                min_local_wps=0.0,
                max_local_wps=999.0,
            )

        probe.assert_called_once()
        self.assertLess(score, 0.995)
        self.assertIn("local ASR similarity", reason)


class RetryPolicyTests(unittest.TestCase):
    def test_retry_temperature_changes_deterministic_baseline(self):
        self.assertEqual(tts.retry_position_temperature(0.0, 0), 0.0)
        self.assertEqual(tts.retry_position_temperature(0.0, 1), 2.0)
        self.assertEqual(tts.retry_position_temperature(0.0, 2), 3.0)

    def test_measured_default_resamples_before_increasing_diversity(self):
        self.assertEqual(tts.retry_position_temperature(2.0, 0), 2.0)
        self.assertEqual(tts.retry_position_temperature(2.0, 1), 2.0)
        self.assertEqual(tts.retry_position_temperature(2.0, 2), 3.0)
        self.assertEqual(tts.retry_position_temperature(2.0, 5), 3.0)

    def test_resume_skips_rejected_deterministic_baseline(self):
        self.assertEqual(
            tts.resume_start_attempt({"chunk_0004"}, [], max_retries=2), 1
        )

    def test_resume_keeps_baseline_when_any_chunk_is_missing(self):
        self.assertEqual(
            tts.resume_start_attempt({"chunk_0004"}, ["chunk_0005"], max_retries=2), 0
        )


class AssembledAudioReviewTests(unittest.TestCase):
    def test_assign_words_to_chunk_spans_uses_word_midpoint(self):
        spans = [
            {"id": "story_0001", "start": 0.0, "end": 1.0, "duration": 1.0},
            {"id": "story_0002", "start": 1.0, "end": 2.0, "duration": 1.0},
        ]
        words = [
            {"word": "một", "start": 0.80, "end": 0.95},
            {"word": "hai", "start": 1.02, "end": 1.20},
        ]

        by_chunk = tts.assign_words_to_chunk_spans(words, spans)

        self.assertEqual([w["word"] for w in by_chunk["story_0001"]], ["một"])
        self.assertEqual([w["word"] for w in by_chunk["story_0002"]], ["hai"])

    def assembled_args(self, **overrides):
        values = dict(
            verify=False,
            fast_verify=True,
            verify_model="model",
            swallow_db=-99.0,
            adaptive_verify=False,
            fast_similarity_floor=0.94,
            verify_threshold=0.985,
            word_probability_floor=0.78,
            word_duration_ratio=2.4,
            min_local_wps=0.0,
            max_local_wps=999.0,
            dropped_words=2,
            drag_ratio=999.0,
            retry_text_mismatch=False,
            retry_timing_anomalies=False,
            retry_empty_asr=False,
        )
        values.update(overrides)
        return SimpleNamespace(**values)

    def test_review_assembled_audio_treats_text_mismatch_as_warning_by_default(self):
        entries = [
            {"id": "story_0001", "text": "một hai ba"},
            {"id": "story_0002", "text": "bốn năm sáu bảy tám"},
        ]
        spans = [
            {"id": "story_0001", "start": 0.0, "end": 1.0, "duration": 1.0},
            {"id": "story_0002", "start": 1.0, "end": 2.0, "duration": 1.0},
        ]
        words = [
            {"word": "một", "start": 0.0, "end": 0.2, "probability": 1.0},
            {"word": "hai", "start": 0.2, "end": 0.4, "probability": 1.0},
            {"word": "ba", "start": 0.4, "end": 0.6, "probability": 1.0},
            {"word": "bốn", "start": 1.0, "end": 1.2, "probability": 1.0},
        ]
        args = self.assembled_args()

        with mock.patch.object(
            tts, "transcribe_word_timestamps", return_value=({"segments": []}, words)
        ), mock.patch.object(tts, "swallowed_syllable", return_value=None):
            results = tts.review_assembled_audio(
                "assembled.wav", entries, spans, args
            )

        self.assertTrue(results["story_0001"][1].startswith("ok"))
        self.assertTrue(results["story_0002"][1].startswith("ok"))
        self.assertIn("warnings:", results["story_0002"][1])
        self.assertIn("dropped", results["story_0002"][1])

    def test_review_assembled_audio_can_retry_text_mismatch_in_strict_mode(self):
        entries = [{"id": "story_0001", "text": "một hai ba bốn năm"}]
        spans = [{"id": "story_0001", "start": 0.0, "end": 1.0, "duration": 1.0}]
        words = [
            {"word": "một", "start": 0.0, "end": 0.2, "probability": 1.0},
        ]
        args = self.assembled_args(retry_text_mismatch=True)

        with mock.patch.object(
            tts, "transcribe_word_timestamps", return_value=({"segments": []}, words)
        ), mock.patch.object(tts, "swallowed_syllable", return_value=None):
            results = tts.review_assembled_audio(
                "assembled.wav", entries, spans, args
            )

        self.assertIn("dropped", results["story_0001"][1])


class ContextPrerollTests(unittest.TestCase):
    def context_args(self, **overrides):
        values = dict(
            context_preroll_words=3,
            context_postroll_words=2,
            context_cut_pad_start=0.05,
            context_cut_pad_end=0.07,
            context_min_alignment=0.72,
            verify_model="model",
        )
        values.update(overrides)
        return SimpleNamespace(**values)

    def test_context_render_entries_wrap_target_text(self):
        entries = [
            {"id": "story_0001", "text": "Một hai ba bốn."},
            {"id": "story_0002", "text": "Tôi đọc câu này."},
            {"id": "story_0003", "text": "Rồi đi tiếp."},
        ]
        args = self.context_args()
        with mock.patch.object(tts, "build_entry", side_effect=lambda cid, text, _args: {"id": cid, "text": text}):
            render_entries, parts = tts.build_context_render_entries(
                entries, ["story_0002"], args
            )

        self.assertEqual(render_entries[0]["id"], "story_0002")
        self.assertIn("hai ba bốn", render_entries[0]["text"])
        self.assertIn("Tôi đọc câu này.", render_entries[0]["text"])
        self.assertIn("Rồi đi", render_entries[0]["text"])
        self.assertEqual(parts["story_0002"]["target"], "Tôi đọc câu này.")

    def test_context_render_can_fall_back_to_direct_target(self):
        entries = [
            {"id": "story_0001", "text": "Một câu trước."},
            {"id": "story_0002", "text": "Cố Dao vừa bước vào."},
        ]
        args = self.context_args()
        with mock.patch.object(
            tts, "build_entry",
            side_effect=lambda cid, text, _args: {"id": cid, "text": text},
        ):
            render_entries, parts = tts.build_context_render_entries(
                entries, ["story_0002"], args,
                direct_ids={"story_0002"},
            )

        self.assertEqual(render_entries[0]["text"], "Cố Dao vừa bước vào.")
        self.assertTrue(parts["story_0002"]["direct"])

    def test_context_alignment_rejects_one_token_match(self):
        words = [{"word": "Tôi", "start": 1.0, "end": 1.2}]

        span = tts.context_target_span_from_words(
            "Câu trước. Tôi đọc đủ bốn từ. Câu sau.",
            "Câu trước.", "Tôi đọc đủ bốn từ.", words,
            min_ratio=0.90,
        )

        self.assertIsNone(span)

    def test_direct_context_retry_is_copied_without_asr_cut(self):
        args = self.context_args()
        with mock.patch.object(tts.shutil, "copy2") as copy, mock.patch.object(
            tts, "transcribe_word_timestamps"
        ) as transcribe:
            ok, reason = tts.materialize_context_render(
                "context.wav", "chunk.wav",
                {"direct": True}, args,
            )

        self.assertTrue(ok)
        self.assertIn("direct retry", reason)
        copy.assert_called_once_with("context.wav", "chunk.wav")
        transcribe.assert_not_called()

    def test_context_target_span_uses_reference_alignment(self):
        render_text = "Một hai ba. Tôi đọc câu này. Rồi đi."
        prefix = "Một hai ba."
        target = "Tôi đọc câu này."
        words = [
            {"word": "Một", "start": 0.00, "end": 0.20},
            {"word": "hai", "start": 0.20, "end": 0.40},
            {"word": "ba", "start": 0.40, "end": 0.60},
            {"word": "Tôi", "start": 0.80, "end": 1.00},
            {"word": "đọc", "start": 1.00, "end": 1.20},
            {"word": "câu", "start": 1.20, "end": 1.40},
            {"word": "này", "start": 1.40, "end": 1.60},
            {"word": "Rồi", "start": 1.80, "end": 2.00},
            {"word": "đi", "start": 2.00, "end": 2.20},
        ]

        span = tts.context_target_span_from_words(
            render_text, prefix, target, words,
            pad_start=0.05, pad_end=0.07,
        )

        self.assertAlmostEqual(span[0], 0.75)
        self.assertAlmostEqual(span[1], 1.67)

    def test_materialize_context_render_cuts_aligned_span(self):
        args = self.context_args()
        parts = {
            "render_text": "Một hai ba. Tôi đọc câu này. Rồi đi.",
            "prefix": "Một hai ba.",
            "target": "Tôi đọc câu này.",
        }
        words = [
            {"word": "Một", "start": 0.00, "end": 0.20},
            {"word": "hai", "start": 0.20, "end": 0.40},
            {"word": "ba", "start": 0.40, "end": 0.60},
            {"word": "Tôi", "start": 0.80, "end": 1.00},
            {"word": "đọc", "start": 1.00, "end": 1.20},
            {"word": "câu", "start": 1.20, "end": 1.40},
            {"word": "này", "start": 1.40, "end": 1.60},
            {"word": "Rồi", "start": 1.80, "end": 2.00},
            {"word": "đi", "start": 2.00, "end": 2.20},
        ]

        with mock.patch.object(
            tts, "transcribe_word_timestamps", return_value=({"segments": []}, words)
        ), mock.patch.object(tts, "extract_audio_span", return_value=True) as extract:
            ok, reason = tts.materialize_context_render(
                "context.wav", "chunk.wav", parts, args
            )

        self.assertTrue(ok)
        extract.assert_called_once()
        self.assertEqual(extract.call_args.args[:2], ("context.wav", "chunk.wav"))
        self.assertAlmostEqual(extract.call_args.args[2], 0.75)
        self.assertAlmostEqual(extract.call_args.args[3], 1.67)
        self.assertIn("context cut", reason)


class StitchLevelingTests(unittest.TestCase):
    def test_opening_level_gain_detects_quiet_opening(self):
        sample_rate = 100
        samples = array("f", [0.10] * 80 + [0.45] * 240)

        with mock.patch.object(tts, "_decode_samples", return_value=samples):
            gain = tts.opening_level_gain_db(
                "unused.wav",
                head_window=0.8,
                body_window=2.4,
                min_gain_db=2.0,
                max_gain_db=5.0,
                sample_rate=sample_rate,
            )

        self.assertGreater(gain, 2.0)
        self.assertLessEqual(gain, 5.0)

    def test_opening_level_gain_ignores_even_level(self):
        sample_rate = 100
        samples = array("f", [0.30] * 320)

        with mock.patch.object(tts, "_decode_samples", return_value=samples):
            gain = tts.opening_level_gain_db(
                "unused.wav",
                head_window=0.8,
                body_window=2.4,
                min_gain_db=2.0,
                max_gain_db=5.0,
                sample_rate=sample_rate,
            )

        self.assertEqual(gain, 0.0)

    def test_opening_level_gain_detects_short_attack_dip(self):
        sample_rate = 100
        samples = array("f", [0.05] * 20 + [0.30] * 300)

        with mock.patch.object(tts, "_decode_samples", return_value=samples):
            gain, release = tts.opening_level_adjustment(
                "unused.wav",
                head_window=0.8,
                body_window=2.4,
                min_gain_db=2.0,
                max_gain_db=5.0,
                attack_min_gain_db=2.0,
                attack_max_gain_db=7.0,
                attack_extra_gain_db=3.0,
                attack_release=0.65,
                sample_rate=sample_rate,
            )

        self.assertGreater(gain, 0.0)
        self.assertLessEqual(gain, 7.0)
        self.assertEqual(release, 0.65)

    def test_leading_silence_trim_keeps_cushion(self):
        sample_rate = 100
        samples = array("f", [0.0] * 10 + [0.4] * 90)

        with mock.patch.object(tts, "_decode_samples", return_value=samples):
            trim = tts.leading_silence_trim_seconds(
                "unused.wav",
                max_trim=0.12,
                keep=0.02,
                min_trim=0.01,
                sample_rate=sample_rate,
            )

        self.assertGreater(trim, 0.0)
        self.assertLessEqual(trim, 0.12)

    def test_trailing_silence_trim_keeps_cushion(self):
        sample_rate = 100
        samples = array("f", [0.4] * 85 + [0.0] * 15)

        with mock.patch.object(tts, "_decode_samples", return_value=samples):
            trim = tts.trailing_silence_trim_seconds(
                "unused.wav",
                max_trim=0.16,
                keep=0.04,
                min_trim=0.01,
                sample_rate=sample_rate,
            )

        self.assertGreater(trim, 0.0)
        self.assertLessEqual(trim, 0.16)


class TextNormalizationTests(unittest.TestCase):
    def normalized(self, text):
        return tts.normalize_for_tts(text, tts.DEFAULT_PRON_DICT)

    def test_number_and_symbol_normalization(self):
        self.assertEqual(
            tts.normalize_for_tts("Giảm 12,5% & còn 1.000₫", {}),
            "Giảm mười hai phẩy năm phần trăm và còn một nghìn đồng",
        )

    def test_asr_comparison_treats_digits_as_spoken_numbers(self):
        self.assertEqual(
            tts._normalize_for_compare("Có 2 lựa chọn"),
            tts._normalize_for_compare("Có hai lựa chọn"),
        )

    def test_range_dash_is_not_read_as_minus(self):
        self.assertEqual(self.normalized("Anh ta 3-5 lần gọi tôi."),
                         "Anh ta ba đến năm lần gọi tôi.")

    def test_negative_number_still_reads_as_am(self):
        self.assertEqual(self.normalized("Nhiệt độ -5 độ."), "Nhiệt độ âm năm độ.")

    def test_full_date_is_read_as_a_date(self):
        self.assertEqual(
            self.normalized("Ngày 12/5/2024, tôi ký đơn."),
            "Ngày mười hai tháng năm năm hai nghìn không trăm hai mươi bốn, tôi ký đơn.",
        )

    def test_bare_slash_pair_is_a_fraction_unless_led_by_a_date_word(self):
        self.assertEqual(self.normalized("Tỷ lệ 1/3 thôi."), "Tỷ lệ một phần ba thôi.")
        self.assertEqual(self.normalized("Hôm 1/3 anh đi đâu?"),
                         "Hôm một tháng ba anh đi đâu?")

    def test_clock_times_are_read_as_hours(self):
        self.assertEqual(self.normalized("Đúng 7h30 sáng."), "Đúng bảy giờ ba mươi sáng.")
        self.assertEqual(self.normalized("Gọi lúc 19:45."), "Gọi lúc mười chín giờ bốn mươi lăm.")
        self.assertEqual(self.normalized("Chờ đến 7h."), "Chờ đến bảy giờ.")

    def test_score_is_not_mistaken_for_a_time(self):
        self.assertEqual(self.normalized("Tỉ số 2:1."), "Tỉ số hai: một.")

    def test_phone_number_is_read_digit_by_digit(self):
        self.assertEqual(
            self.normalized("Số của anh ta là 0912345678."),
            "Số của anh ta là không chín một hai ba bốn năm sáu bảy tám.",
        )

    def test_four_digit_year_stays_a_quantity(self):
        self.assertEqual(self.normalized("Năm 1975."), "Năm một nghìn chín trăm bảy mươi lăm.")

    def test_units_are_spelled_and_grouping_dots_survive(self):
        self.assertEqual(self.normalized("Mua 5kg cam, hết 250.000đ."),
                         "Mua năm ki lô gam cam, hết hai trăm năm mươi nghìn đồng.")

    def test_per_period_slash(self):
        self.assertEqual(self.normalized("Lương 15 triệu/tháng."),
                         "Lương mười lăm triệu mỗi tháng.")

    def test_roman_numeral_only_behind_a_numeral_word(self):
        self.assertEqual(self.normalized("Thế kỷ XXI rồi."), "Thế kỷ hai mươi mốt rồi.")
        # A bare initial must survive: it is a name, not a numeral.
        self.assertEqual(self.normalized("Anh V đứng đó."), "Anh V đứng đó.")

    def test_known_acronyms_expand_and_titles_lose_their_false_sentence_end(self):
        self.assertEqual(
            self.normalized("TS. Nam đưa USB và xét nghiệm ADN cho MC."),
            "tiến sĩ Nam đưa u ét bê và xét nghiệm a đê en cho em xi.",
        )
        self.assertEqual(self.normalized("Tôi sống ở TP.HCM."),
                         "Tôi sống ở thành phố Hồ Chí Minh.")

    def test_emphasis_caps_are_never_spelled_out(self):
        self.assertEqual(self.normalized("Tôi KHÔNG đồng ý!"), "Tôi KHÔNG đồng ý!")

    def test_unknown_acronym_is_left_alone(self):
        self.assertEqual(self.normalized("Công ty ABC."), "Công ty ABC.")

    def test_pron_dict_overrides_the_builtin_acronym_reading(self):
        self.assertEqual(
            tts.normalize_for_tts("Chiếc USB đó.", {"USB": "u ét bê nhé"}),
            "Chiếc u ét bê nhé đó.",
        )

    def test_parentheses_become_audible_asides(self):
        self.assertEqual(self.normalized("Chị Lan (vợ anh ta) đứng đó."),
                         "Chị Lan, vợ anh ta, đứng đó.")

    def test_dialogue_dash_and_em_dash(self):
        self.assertEqual(self.normalized("- Anh đi đâu đấy?"), "Anh đi đâu đấy?")
        self.assertEqual(self.normalized("lễ đính hôn — trước khi"), "lễ đính hôn, trước khi")
        self.assertEqual(self.normalized("một ly cà-phê"), "một ly cà phê")

    def test_collapsed_numeral_token_is_not_judged_as_one_word(self):
        # Whisper returns a spoken phone number as one token holding every
        # syllable's timestamps. Judged as a word it looks dragged ~10x and
        # impossibly slow, which failed word-perfect audio on a real render.
        words = [
            {"word": "số", "start": 0.0, "end": 0.3, "probability": 0.99},
            {"word": "0912345678", "start": 0.3, "end": 4.5, "probability": 0.74},
            {"word": "đòi", "start": 4.5, "end": 4.8, "probability": 0.99},
            {"word": "tôi", "start": 4.8, "end": 5.1, "probability": 0.99},
            {"word": "trả", "start": 5.1, "end": 5.4, "probability": 0.99},
            {"word": "tiền", "start": 5.4, "end": 5.7, "probability": 0.99},
        ]
        self.assertIsNone(tts.low_confidence_word(words))
        self.assertIsNone(tts.local_tempo_defect(words))

    def test_whisper_number_spellings_fold_together(self):
        # The same phone number came back spelled both ways on two takes.
        spoken = "gọi vào số không chín một hai ba bốn năm sáu bảy tám nhé"
        for written in ["gọi vào số 0912345678 nhé", "gọi vào số 0912 345 678 nhé"]:
            self.assertEqual(
                tts._normalize_for_compare(written),
                tts._normalize_for_compare(spoken),
                written,
            )

    def test_grouped_amount_is_not_folded_into_an_identifier(self):
        self.assertEqual(
            tts._normalize_for_compare("nợ 1.500.000.000 đồng"),
            tts._normalize_for_compare("nợ một tỷ năm trăm triệu đồng"),
        )

    def test_verifier_compares_spoken_form_against_whisper_orthography(self):
        # Whisper writes back what it hears in orthography; the chunk was
        # rendered from the spoken form. Both must reduce to one transcript, or
        # every normalized chunk scores as a mismatch and retries needlessly.
        for written, spoken in [
            ("Gọi lúc 7h30 nhé", "Gọi lúc bảy giờ ba mươi nhé"),
            ("Đưa USB đây", "Đưa u ét bê đây"),
            ("Ngày 12/5/2024", "Ngày mười hai tháng năm năm 2024"),
            ("Hết 250.000đ", "Hết hai trăm năm mươi nghìn đồng"),
        ]:
            self.assertEqual(
                tts._normalize_for_compare(written),
                tts._normalize_for_compare(spoken),
                f"{written!r} vs {spoken!r}",
            )

    def test_chunking_preserves_all_words(self):
        text = "Một câu ngắn. " + " ".join(f"từ{i}" for i in range(25)) + "."
        chunks = tts.split_text_into_chunks(text, max_chars=55, max_words=8)
        words = lambda value: re.findall(r"[\wÀ-ỹ]+", value)
        self.assertEqual(words(" ".join(chunks)), words(text))
        self.assertTrue(all(len(chunk.split()) <= 8 for chunk in chunks))


class StrictFinalVerificationTests(unittest.TestCase):
    def strict_args(self):
        return SimpleNamespace(
            ctc_align_model="ctc",
            ctc_batch_size=1,
            secondary_verify_model="secondary",
            secondary_verify_threads=1,
            ctc_mean_score_floor=-1.70,
            ctc_word_score_floor=-4.0,
            ctc_critical_score_floor=-8.0,
            ctc_consecutive_bad_words=2,
            strict_similarity_floor=0.94,
            strict_dropped_words=2,
            verify_model="primary",
            verify=False,
            fast_verify=True,
            verify_threshold=0.985,
        )

    def word_timestamps(self, text):
        return [
            {
                "word": word,
                "start": index * 0.2,
                "end": index * 0.2 + 0.15,
                "probability": 1.0,
            }
            for index, word in enumerate(text.split())
        ]

    def aligned(self, text, scores=None):
        words = text.split()
        scores = scores or [-0.2] * len(words)
        return [
            {"text": word, "score": score}
            for word, score in zip(words, scores)
        ]

    def review(self, expected, primary_heard, secondary_heard, ctc_scores,
               primary_reason="word similarity 0.800",
               isolated_heard=None):
        entry = {"id": "story_0001", "text": expected}
        span = {
            "id": "story_0001", "start": 0.0, "end": 5.0,
            "duration": 5.0,
        }
        primary_words = self.word_timestamps(primary_heard)
        session = FakeStrictSession(
            self.aligned(expected, ctc_scores),
            self.word_timestamps(secondary_heard),
        )
        isolated_heard = (
            expected if isolated_heard is None else isolated_heard
        )
        with mock.patch.object(
            tts, "clause_asr_transcript_span", return_value=isolated_heard
        ):
            return tts.review_strict_final_audio(
                "candidate.wav", [entry], [span], self.strict_args(),
                {"story_0001": (0.8, primary_reason)},
                {"story_0001": primary_words},
                mock.Mock(), session,
            )

    def test_ctc_rejects_two_consecutive_acoustically_absent_words(self):
        result = tts.ctc_alignment_evidence([
            {"text": "Tôi", "score": -0.2},
            {"text": "trả", "score": -6.0},
            {"text": "lời", "score": -5.0},
            {"text": "thay", "score": -0.3},
        ])

        self.assertTrue(result["failed"])
        self.assertEqual(result["max_bad_run"], 2)

    def test_one_asr_mistake_does_not_fail_when_other_evidence_is_clean(self):
        results, details = self.review(
            "Tôi về nhà", "Tôi về nha", "Tôi về nhà",
            [-0.2, -0.2, -0.2],
        )

        self.assertTrue(results["story_0001"][1].startswith("ok"))
        self.assertTrue(details["story_0001"]["passed"])

    def test_corroborated_name_and_insertion_mismatch_fails(self):
        results, details = self.review(
            "Cố Dao quay lại", "Và Cố Đao quay lại",
            "Và Cố Đao quay lại", [-0.2] * 4,
            isolated_heard="Và Cố Đao quay lại",
        )

        reason = results["story_0001"][1]
        self.assertFalse(details["story_0001"]["passed"])
        self.assertIn("independent verifiers", reason)
        self.assertIn("protected term mismatch", reason)

    def test_protected_name_does_not_consume_following_lowercase_word(self):
        self.assertEqual(
            tts.protected_terms("Cố Dao được nhà họ Cố nhận về."),
            ["cố dao"],
        )

    def test_sentence_leading_noun_does_not_join_following_name(self):
        self.assertEqual(
            tts.protected_terms("Mặt Cố Dao trắng đi."),
            ["cố dao"],
        )

    def test_three_word_vietnamese_name_keeps_its_surname(self):
        self.assertEqual(
            tts.protected_terms("Cố Minh Trạch quay lại."),
            ["cố minh trạch"],
        )

    def test_dao_pronunciation_hint_preserves_name_capitalization(self):
        self.assertEqual(
            tts.normalize_for_tts("Cố Dao cầm dao.", tts.DEFAULT_PRON_DICT),
            "Cố Giao cầm giao.",
        )

    def test_northern_name_homophones_do_not_become_false_mismatches(self):
        evidence = tts.transcript_evidence(
            "Cố Giao gặp Cố Minh Trạch.",
            "Cố Dao gặp Cố Minh Chạch.",
        )

        self.assertEqual(evidence["similarity"], 1.0)
        self.assertEqual(evidence["changed_expected"], [])
        self.assertEqual(
            tts.missing_protected_terms(
                "Cố Giao gặp Cố Minh Trạch.",
                "Cố Dao gặp Cố Minh Chạch.",
            ),
            [],
        )

    def test_hard_d_is_not_accepted_as_a_dao_name_homophone(self):
        evidence = tts.transcript_evidence("Cố Giao quay lại.", "Cố Đao quay lại.")

        self.assertIn("giao", evidence["changed_expected"])
        self.assertEqual(
            tts.missing_protected_terms("Cố Giao quay lại.", "Cố Đao quay lại."),
            ["cố giao"],
        )

    def test_matching_full_file_boundary_drift_needs_isolated_confirmation(self):
        results, details = self.review(
            "Tôi về nhà", "Không Tôi về nhà", "Không Tôi về nhà",
            [-0.2, -0.2, -0.2], isolated_heard="Tôi về nhà",
        )

        self.assertTrue(results["story_0001"][1].startswith("ok"))
        self.assertTrue(details["story_0001"]["passed"])

    def test_publish_refuses_to_overwrite_final_when_any_chunk_failed(self):
        with tempfile.TemporaryDirectory() as directory:
            candidate = os.path.join(directory, "candidate.wav")
            output = os.path.join(directory, "final.wav")
            with open(candidate, "wb") as fh:
                fh.write(b"new")
            with open(output, "wb") as fh:
                fh.write(b"old")

            with self.assertRaises(tts.AudioQualityError):
                tts.publish_verified_candidate(
                    candidate, output,
                    {"story_0001": {"passed": False}},
                )

            with open(output, "rb") as fh:
                self.assertEqual(fh.read(), b"old")
            self.assertTrue(os.path.exists(candidate))

    def test_publish_atomically_moves_a_fully_verified_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            candidate = os.path.join(directory, "candidate.wav")
            output = os.path.join(directory, "final.wav")
            with open(candidate, "wb") as fh:
                fh.write(b"verified")

            tts.publish_verified_candidate(
                candidate, output,
                {"story_0001": {"passed": True}},
            )

            self.assertFalse(os.path.exists(candidate))
            with open(output, "rb") as fh:
                self.assertEqual(fh.read(), b"verified")


if __name__ == "__main__":
    unittest.main()
