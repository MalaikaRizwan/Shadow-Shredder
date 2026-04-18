# Architecture

## High-Level Design
ForensiWipe follows layered architecture:

1. **GUI Layer (`app/gui`)**
   - PySide6 tabs and widgets.
   - Worker threads for non-blocking operations.
   - Progress/status handling and user confirmations.

2. **Core Layer (`app/core`)**
   - `wipe_methods.py`: strategy implementations.
   - `wipe_engine.py`: orchestrates file/folder/free-space workflows.
   - `analyzer.py`: target metadata enumeration.
   - `metadata_sanitizer.py`: rename/truncate and artifact-aware notes.
   - `partition_wiper.py`: drive discovery and system-drive checks.
   - `free_space_wiper.py`: temporary-file based free-space sanitization.
   - `verifier.py`: deletion/hash verification helpers.

3. **Reporting Layer (`app/reporting`)**
   - Structured operation record model.
   - JSON/CSV/HTML/TXT output generation.
   - Templated HTML forensic report.

## Wipe Engine Flow
1. Build request from GUI.
2. Analyze target and detect filesystem.
3. Attach forensic notes and limitation warnings.
4. Execute selected workflow (file/folder/free-space).
5. Verify outcome where possible.
6. Return result payload for reporting.

## GUI Threading Flow
1. Main window creates `QThread`.
2. `OperationWorker` runs engine in background.
3. Progress signals update progress bar and live console.
4. Completion signal triggers report generation and dashboard update.

## Reporting Flow
1. Operation completion returns structured dictionary.
2. `OperationRecord` is built in GUI layer.
3. `ReportGenerator.save_reports()` writes:
   - JSON full report
   - CSV operation row
   - HTML human-readable summary
   - TXT compact summary
