# Test Cases

## 1. File Dry Run
- Input: small text file in `tests/sample_test_data`
- Mode: dry run ON
- Expected: no deletion; report status success; bytes estimated > 0

## 2. File Real Wipe (safe temp file)
- Input: temporary file
- Mode: dry run OFF
- Expected: file removed; verification `deleted`

## 3. Folder Dry Run
- Input: folder with nested files
- Expected: file/folder counts shown; no real deletion

## 4. Free-space Dry Run
- Input: selected drive mount
- Expected: simulation completes; report generated

## 5. Method Validation
- Check each wipe method returns transformed bytes of same length.

## 6. Reporting Validation
- Ensure JSON/CSV/HTML/TXT files generated after operation.

## 7. Safety Validation
- Partition action requires typed confirmation.
- Demo Safe Mode blocks destructive partition/free-space wipe.
