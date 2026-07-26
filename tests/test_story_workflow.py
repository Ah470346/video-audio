import contextlib
import hashlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools import prepare_kaggle_voxcpm_job as prepare
from tools import prepare_kaggle_voxcpm_short_job as prepare_short


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "agent-tools" / "agent-workflow" / "validate_story_gate.py"
LONG_PREPARE = ROOT / "tools" / "prepare_kaggle_voxcpm_job.py"
SHORT_PREPARE = ROOT / "tools" / "prepare_kaggle_voxcpm_short_job.py"


def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_valid_gate(folder, story_text="Đây là bản thảo kiểm tra cổng kỹ thuật.\n"):
    story = folder / "story.md"
    story.write_text(story_text, encoding="utf-8")
    digest = sha256_file(story)
    revision = 1
    manifest = {
        "protocol_version": 2,
        "story_path": "story.md",
        "current_revision": revision,
        "current_sha256": digest,
        "pre_polish_development_receipt": {
            "protocol_version": 2,
            "issued_by": "audio-story-developmental-editor",
            "scope": "full-draft",
            "mode": "developmental",
            "revision": revision,
            "sha256": digest,
            "status": "clean",
            "coverage": "complete",
            "total_blockers": 0,
            "total_major_findings": 0,
            "total_moderate_findings": 0,
        },
        "pre_polish_clarity_receipt": {
            "protocol_version": 2,
            "issued_by": "audio-story-clarity-check",
            "scope": "full-draft",
            "stage": "pre-polish",
            "revision": revision,
            "sha256": digest,
            "status": "clean",
            "coverage": "complete",
            "total_findings": 0,
            "continuity_gaps": [],
        },
        "development_receipt": {
            "protocol_version": 2,
            "issued_by": "audio-story-developmental-editor",
            "scope": "full-draft",
            "mode": "post-polish",
            "revision": revision,
            "sha256": digest,
            "status": "clean",
            "coverage": "complete",
            "total_blockers": 0,
            "total_major_findings": 0,
            "total_moderate_findings": 0,
        },
        "clarity_receipt": {
            "protocol_version": 2,
            "issued_by": "audio-story-clarity-check",
            "scope": "full-draft",
            "stage": "post-polish",
            "revision": revision,
            "sha256": digest,
            "status": "clean",
            "coverage": "complete",
            "total_findings": 0,
            "continuity_gaps": [],
        },
        "final_polish_receipt": {
            "protocol_version": 2,
            "issued_by": "audio-story-final-polish",
            "status": "completed",
            "input_revision": revision,
            "input_sha256": digest,
            "output_revision": revision,
            "output_sha256": digest,
        },
        "completion_gate_receipt": {
            "protocol_version": 2,
            "status": "pass",
            "revision": revision,
            "sha256": digest,
            "gate_agent": "audio-story-completion-gate",
            "validator_mode": "pre-gate",
        },
    }
    manifest_path = folder / "story.gate.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return story, manifest_path, manifest


def run_validator(story, manifest, mode="final"):
    return subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--story",
            str(story),
            "--manifest",
            str(manifest),
            "--mode",
            mode,
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


class StoryGateValidatorTests(unittest.TestCase):
    def test_valid_receipt_chain_passes_final_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            story, manifest, _data = write_valid_gate(Path(tmp))

            result = run_validator(story, manifest)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("GATE_VALIDATION_OK", result.stdout)

    def test_pre_gate_passes_before_completion_receipt_but_final_does_not(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            story, manifest, data = write_valid_gate(folder)
            data.pop("completion_gate_receipt")
            manifest.write_text(json.dumps(data), encoding="utf-8")

            pre_gate = run_validator(story, manifest, mode="pre-gate")
            final_gate = run_validator(story, manifest, mode="final")

        self.assertEqual(pre_gate.returncode, 0, pre_gate.stdout + pre_gate.stderr)
        self.assertNotEqual(final_gate.returncode, 0)
        self.assertIn("completion gate receipt is required", final_gate.stdout)

    def test_final_polish_input_fields_are_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            story, manifest, data = write_valid_gate(folder)
            data["final_polish_receipt"].pop("input_revision")
            data["final_polish_receipt"].pop("input_sha256")
            manifest.write_text(json.dumps(data), encoding="utf-8")

            result = run_validator(story, manifest)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("final polish input_revision", result.stdout)
        self.assertIn("final polish input_sha256", result.stdout)

    def test_designated_receipt_issuer_is_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            story, manifest, data = write_valid_gate(folder)
            data["development_receipt"]["issued_by"] = "main-writer"
            manifest.write_text(json.dumps(data), encoding="utf-8")

            result = run_validator(story, manifest)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("development receipt has unexpected issuer", result.stdout)

    def test_final_polish_revision_jump_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            story, manifest, data = write_valid_gate(folder)
            data["current_revision"] = 3
            data["development_receipt"]["revision"] = 3
            data["clarity_receipt"]["revision"] = 3
            data["final_polish_receipt"]["output_revision"] = 3
            data["completion_gate_receipt"]["revision"] = 3
            manifest.write_text(json.dumps(data), encoding="utf-8")

            result = run_validator(story, manifest)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("revision transition", result.stdout)

    def test_one_revision_final_polish_change_forms_a_valid_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            story, manifest, data = write_valid_gate(folder)
            current_hash = sha256_file(story)
            input_hash = hashlib.sha256(b"pre-polish bytes").hexdigest()
            data["current_revision"] = 2
            for slot in ("pre_polish_development_receipt", "pre_polish_clarity_receipt"):
                data[slot]["revision"] = 1
                data[slot]["sha256"] = input_hash
            for slot in ("development_receipt", "clarity_receipt"):
                data[slot]["revision"] = 2
                data[slot]["sha256"] = current_hash
            data["final_polish_receipt"].update(
                {
                    "input_revision": 1,
                    "input_sha256": input_hash,
                    "output_revision": 2,
                    "output_sha256": current_hash,
                }
            )
            data["completion_gate_receipt"]["revision"] = 2
            data["completion_gate_receipt"]["sha256"] = current_hash
            manifest.write_text(json.dumps(data), encoding="utf-8")

            result = run_validator(story, manifest)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_post_polish_clarity_stage_is_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            story, manifest, data = write_valid_gate(folder)
            data["clarity_receipt"].pop("stage")
            manifest.write_text(json.dumps(data), encoding="utf-8")

            result = run_validator(story, manifest)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("clarity receipt must have stage=post-polish", result.stdout)

    def test_stale_story_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            story, manifest, _data = write_valid_gate(folder)
            story.write_text("Bản thảo đã bị thay đổi.\n", encoding="utf-8")

            result = run_validator(story, manifest)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("current_sha256 mismatch", result.stdout)

    def test_non_object_manifest_fails_cleanly(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            story = folder / "story.md"
            story.write_text("Bản thảo.\n", encoding="utf-8")
            manifest = folder / "story.gate.json"
            manifest.write_text("[]\n", encoding="utf-8")

            result = run_validator(story, manifest)

        self.assertEqual(result.returncode, 1)
        self.assertIn("manifest root must be an object", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_validator_bypass_requires_an_explicit_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            story = folder / "story.md"
            story.write_text("Bản thảo.\n", encoding="utf-8")
            manifest = folder / "missing.gate.json"

            result = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--story",
                    str(story),
                    "--manifest",
                    str(manifest),
                    "--mode",
                    "final",
                    "--allow-user-bypass",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )

        self.assertEqual(result.returncode, 2)
        self.assertIn("--bypass-reason is required", result.stdout)


class KagglePrepareStoryGateTests(unittest.TestCase):
    def test_direct_prepare_rejects_story_without_gate_before_creating_job(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            story = folder / "unverified.md"
            story.write_text("Bản thảo chưa duyệt.\n", encoding="utf-8")
            job_dir = folder / "job"

            result = subprocess.run(
                [
                    sys.executable,
                    str(LONG_PREPARE),
                    "--kernel-id",
                    "user/audit",
                    "--title",
                    "audit",
                    "--job-dir",
                    str(job_dir),
                    "--input",
                    str(story),
                    "--voice",
                    "adam",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            job_was_created = job_dir.exists()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("manifest not found", result.stdout)
        self.assertFalse(job_was_created)

    def test_bypass_requires_a_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "unverified.md"
            story.write_text("Bản thảo chưa duyệt.\n", encoding="utf-8")

            with self.assertRaises(SystemExit) as raised:
                prepare.validate_story_for_render(story, allow_user_bypass=True)

        self.assertIn("--bypass-reason is required", str(raised.exception))

    def test_direct_short_prepare_also_rejects_story_without_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            story = folder / "unverified.md"
            story.write_text("Bản thảo ngắn chưa duyệt.\n", encoding="utf-8")
            job_dir = folder / "short-job"

            result = subprocess.run(
                [
                    sys.executable,
                    str(SHORT_PREPARE),
                    "--job-dir",
                    str(job_dir),
                    "--input",
                    str(story),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            job_was_created = job_dir.exists()

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("manifest not found", result.stdout)
        self.assertFalse(job_was_created)

    def test_verified_long_bundle_records_gate_and_excludes_dotenv(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            story, manifest, _data = write_valid_gate(folder)
            job_dir = folder / "job"

            result = subprocess.run(
                [
                    sys.executable,
                    str(LONG_PREPARE),
                    "--kernel-id",
                    "user/audit",
                    "--title",
                    "audit",
                    "--job-dir",
                    str(job_dir),
                    "--input",
                    str(story),
                    "--manifest",
                    str(manifest),
                    "--voice",
                    "adam",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            render_job = json.loads((job_dir / "render_job.json").read_text(encoding="utf-8"))
            metadata = json.loads((job_dir / "kernel-metadata.json").read_text(encoding="utf-8"))
            build_info = json.loads((job_dir / "build_info.json").read_text(encoding="utf-8"))
            launcher = (job_dir / "convert_script_to_audio_voxcpm_kaggle.py").read_text(
                encoding="utf-8"
            )
            render_args = render_job["render_args"]
            retry_flag = render_args.index("--max_verify_retries")

            self.assertEqual(render_job["story_gate"]["status"], "verified")
            self.assertEqual(
                render_job["story_gate"]["story_sha256"],
                sha256_file(story),
            )
            self.assertEqual(render_args[retry_flag + 1], "2")
            self.assertTrue((job_dir / "job_inputs" / manifest.name).is_file())
            self.assertFalse((job_dir / ".env").exists())
            self.assertIn("ah470346/voxcpm2-snapshot", metadata["dataset_sources"])
            self.assertNotIn(
                build_info["EMBEDDED_BUNDLE_SHA256"],
                (None, "set-by-launcher-after-extraction"),
            )
            self.assertIn("tts-and-qc-models", launcher)
            self.assertIn("find_snapshot_in_dataset_roots", launcher)
            for package in (
                render_job.get("pip_packages_no_deps", [])
                + render_job.get("pip_packages", [])
            ):
                self.assertIn("==", package)

    def test_long_and_short_prepare_defaults_use_two_retries(self):
        long_args = prepare.build_parser().parse_args(
            [
                "--kernel-id",
                "user/kernel",
                "--title",
                "kernel",
                "--job-dir",
                "/tmp/kernel",
                "--input",
                "story.md",
            ]
        )
        short_args = prepare_short.build_parser().parse_args(
            ["--job-dir", "/tmp/kernel", "--input", "story.md"]
        )

        self.assertEqual(long_args.max_verify_retries, 2)
        self.assertEqual(short_args.max_verify_retries, 2)

    def test_user_bypass_is_recorded_by_prepare_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            story = Path(tmp) / "unverified.md"
            story.write_text("Bản thảo chưa duyệt.\n", encoding="utf-8")

            with contextlib.redirect_stdout(io.StringIO()):
                evidence, _story, manifest = prepare.validate_story_for_render(
                    story,
                    allow_user_bypass=True,
                    bypass_reason="explicit audit override",
                )
            manifest_was_created = manifest.exists()

        self.assertEqual(evidence["status"], "user-bypassed")
        self.assertEqual(evidence["bypass_reason"], "explicit audit override")
        self.assertFalse(manifest_was_created)


if __name__ == "__main__":
    unittest.main()
