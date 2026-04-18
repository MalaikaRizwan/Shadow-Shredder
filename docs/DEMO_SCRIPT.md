# Classroom Demo Script

## Objective
Demonstrate forensic-aware secure sanitization safely, with emphasis on artifact minimization and technical limitations.

## Live Demo Flow (10-15 minutes)
1. Open Dashboard and explain lawful-use banner.
2. Show detected drives and system-drive warning behavior.
3. Open File/Folder Shredder:
   - Select sample file.
   - Analyze target metadata.
   - Enable Dry Run + Demo Safe Mode.
   - Run with Random or XOR method.
4. Open Partition/Free-space tab:
   - Show typed confirmation requirement (`WIPE`).
   - Demonstrate free-space wipe dry run.
5. Open Reports tab:
   - Show JSON, CSV, and HTML report outputs.
   - Explain forensic notes and limitations section.

## Safe Demo Plan
- Use only `samples/demo_files`.
- Keep destructive modes disabled.
- Use Dry Run for partition actions.

## Forensic Talking Points
- NTFS MFT and USN journal persistence.
- FAT directory entry semantics.
- SSD wear leveling and TRIM caveats.
- Why secure deletion is probabilistic in real-world systems.

## Possible Viva Q&A
- **Q:** Why not guarantee irrecoverability?  
  **A:** User-space tools cannot fully control journaling layers, firmware remapping, snapshots, or all metadata structures.

- **Q:** Why include Quick Forensic mode?  
  **A:** It demonstrates speed-optimized transformation wipes and practical trade-offs.

- **Q:** Why typed confirmation?  
  **A:** It enforces explicit human intent before destructive actions.
