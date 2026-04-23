from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Callable

from app.core.analyzer import Analyzer
from app.core.free_space_wiper import FreeSpaceWiper
from app.core.metadata_mode import metadata_mode_summary
from app.core.metadata_sanitizer import MetadataSanitizer
from app.core.verifier import Verifier
from app.core.wipe_methods import build_method

ProgressCb = Callable[[int, int, str], None]


@dataclass
class WipeRequest:
    target_path: str
    target_type: str
    method_name: str
    passes: int = 1
    chunk_size: int = 1024 * 1024
    verify: bool = True
    dry_run: bool = True
    demo_safe_mode: bool = True
    custom_byte_value: int | None = None
    secure_rename_rounds: int = 2
    quick_mode: bool = False
    hash_before: bool = False
    metadata_mode: str = "Enhanced"
    metadata_actions: dict = field(default_factory=dict)
    generate_reports: bool = True
    report_formats: list[str] = field(default_factory=lambda: ["json", "html", "txt", "csv"])


@dataclass
class WipeResult:
    success: bool
    bytes_processed: int = 0
    warnings: list[str] = field(default_factory=list)
    forensic_notes: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    verification: str = "not-run"
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


class WipeEngine:
    def __init__(self) -> None:
        self._log = logging.getLogger("forensiwipe.engine")
        self._analyzer = Analyzer()
        self._free_space = FreeSpaceWiper()

    def execute(
        self,
        request: WipeRequest,
        progress_cb: ProgressCb | None = None,
        cancel_flag: Callable[[], bool] | None = None,
    ) -> WipeResult:
        target = Path(request.target_path)
        analysis = self._analyzer.analyze_path(target)
        method = build_method(request.method_name, request.custom_byte_value)
        actions = self._metadata_actions_for_request(request)
        result = WipeResult(
            success=False,
            metadata={
                "analysis": analysis.to_dict(),
                "metadata_mode": request.metadata_mode,
                "metadata_actions": actions,
                "metadata_summary": metadata_mode_summary(request.metadata_mode),
            },
        )

        fs = analysis.filesystem
        if actions.get("forensic_notes"):
            result.forensic_notes.extend(MetadataSanitizer.forensic_notes_for_fs(fs))
            result.forensic_notes.extend(MetadataSanitizer.generic_limitations())

        if request.demo_safe_mode and request.target_type in {"partition", "free-space"} and not request.dry_run:
            result.errors.append("Demo Safe Mode blocks destructive partition/free-space operations.")
            return result

        try:
            if request.target_type == "file":
                result.bytes_processed = self._wipe_file(target, request, method, progress_cb, cancel_flag, result)
            elif request.target_type == "folder":
                result.bytes_processed = self._wipe_directory(
                    target,
                    request,
                    method,
                    progress_cb,
                    cancel_flag,
                    result,
                    remove_root=True,
                )
            elif request.target_type == "partition":
                result.bytes_processed = self._wipe_partition(target, request, method, progress_cb, cancel_flag, result)
            elif request.target_type == "free-space":
                bytes_done, notes = self._free_space.wipe(
                    target,
                    method,
                    request.passes,
                    request.chunk_size,
                    request.dry_run,
                    progress_cb,
                    cancel_flag,
                )
                result.bytes_processed = bytes_done
                result.forensic_notes.extend(notes)
            else:
                result.errors.append(f"Unsupported target type: {request.target_type}")
                return result

            if actions.get("suggest_free_space_wipe") and request.target_type in {"file", "folder"}:
                result.warnings.append(
                    "Forensic-aware mode suggests running a free-space wipe to reduce recoverable remnants."
                )

            if request.dry_run:
                result.verification = "dry-run"
                result.warnings.append("Dry Run enabled: no on-disk changes were made.")
                result.success = not result.errors
                return result

            if request.verify and request.target_type in {"file", "folder"}:
                deleted = Verifier.path_deleted(target)
                result.verification = "deleted" if deleted else "residual-detected"
                if not deleted and not request.dry_run:
                    result.warnings.append("Target still appears on filesystem after operation.")
            else:
                result.verification = "completed"
            result.success = not result.errors
        except Exception as exc:
            self._log.exception("Wipe operation failed")
            result.errors.append(str(exc))
        return result

    def _metadata_actions_for_request(self, request: WipeRequest) -> dict:
        base = {
            "overwrite": True,
            "rename_rounds": request.secure_rename_rounds,
            "truncate": True,
            "sha256_pre_wipe": request.hash_before,
            "forensic_notes": False,
            "suggest_free_space_wipe": False,
        }
        base.update(request.metadata_actions or {})
        base["rename_rounds"] = int(base.get("rename_rounds", 0) or 0)
        return base

    def _wipe_file(
        self,
        path: Path,
        req: WipeRequest,
        method,
        progress_cb: ProgressCb | None,
        cancel_flag,
        result: WipeResult,
    ) -> int:
        if not path.exists():
            raise FileNotFoundError(path)
        size = path.stat().st_size
        if req.dry_run:
            if progress_cb:
                progress_cb(size, size, "Dry-run simulation complete for file")
            return size

        actions = self._metadata_actions_for_request(req)

        if actions.get("sha256_pre_wipe"):
            result.metadata["sha256_before"] = Verifier.file_sha256(path, req.chunk_size)

        current_path = path
        rename_rounds = int(actions.get("rename_rounds", 0))
        if rename_rounds > 0:
            renamed_paths = MetadataSanitizer.secure_rename(current_path, rename_rounds)
            current_path = Path(renamed_paths[-1])
            result.metadata["rename_chain"] = renamed_paths

        bytes_processed = 0
        if actions.get("overwrite", True):
            for p in range(req.passes):
                with current_path.open("r+b", buffering=0) as f:
                    f.seek(0, os.SEEK_SET)
                    remaining = size
                    while remaining > 0:
                        if cancel_flag and cancel_flag():
                            raise RuntimeError("Operation cancelled by user.")
                        read_len = min(req.chunk_size, remaining)
                        old_chunk = f.read(read_len)
                        f.seek(-len(old_chunk), os.SEEK_CUR)
                        new_chunk = method.transform(old_chunk or (b"\x00" * read_len), p)
                        f.write(new_chunk)
                        remaining -= len(new_chunk)
                        bytes_processed += len(new_chunk)
                        if progress_cb:
                            progress_cb(bytes_processed, size * req.passes, f"Pass {p + 1}/{req.passes}")
                    f.flush()
                    os.fsync(f.fileno())

        if actions.get("truncate", True):
            MetadataSanitizer.truncate(current_path)
        current_path.unlink()
        return bytes_processed

    def _wipe_partition(
        self,
        partition_root: Path,
        req: WipeRequest,
        method,
        progress_cb: ProgressCb | None,
        cancel_flag,
        result: WipeResult,
    ) -> int:
        bytes_processed = self._wipe_directory(
            partition_root,
            req,
            method,
            progress_cb,
            cancel_flag,
            result,
            remove_root=False,
        )
        if req.dry_run:
            free_bytes_processed, notes = self._free_space.wipe(
                partition_root,
                method,
                req.passes,
                req.chunk_size,
                True,
                progress_cb,
                cancel_flag,
            )
            result.forensic_notes.extend(notes)
            return bytes_processed + free_bytes_processed

        free_bytes_processed, notes = self._free_space.wipe(
            partition_root,
            method,
            req.passes,
            req.chunk_size,
            False,
            progress_cb,
            cancel_flag,
        )
        result.forensic_notes.extend(notes)
        return bytes_processed + free_bytes_processed

    def _wipe_directory(
        self,
        folder: Path,
        req: WipeRequest,
        method,
        progress_cb: ProgressCb | None,
        cancel_flag,
        result: WipeResult,
        *,
        remove_root: bool,
    ) -> int:
        if not folder.exists():
            raise FileNotFoundError(folder)
        files = [Path(root) / f for root, _, fs in os.walk(folder) for f in fs]
        total_bytes = sum(fp.stat().st_size for fp in files if fp.exists())
        if req.dry_run:
            if progress_cb:
                progress_cb(total_bytes, total_bytes, f"Dry-run folder simulation for {len(files)} files")
            return total_bytes
        done = 0
        for fp in files:
            req_file = WipeRequest(**{**req.__dict__, "target_type": "file", "target_path": str(fp)})
            file_result = self.execute(req_file, progress_cb=progress_cb, cancel_flag=cancel_flag)
            done += file_result.bytes_processed
            result.warnings.extend(file_result.warnings)
            result.errors.extend(file_result.errors)
        for root, dirs, _ in os.walk(folder, topdown=False):
            for d in dirs:
                dir_path = Path(root, d)
                try:
                    dir_path.rmdir()
                except PermissionError:
                    result.warnings.append(f"Skipped protected directory during partition wipe: {dir_path}")
        if remove_root:
            try:
                folder.rmdir()
            except PermissionError:
                result.warnings.append(f"Skipped protected partition root during cleanup: {folder}")
        return done
