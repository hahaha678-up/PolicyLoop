# Task Utility Scripts

These scripts generate metadata and statistics for task libraries.
They work with any task directory — point `--tasks-folder` at your own library the same way PolicyLoop uses them internally.

For full documentation and usage examples, see [Task Libraries](../../../docs/task_libraries.md).

### Generate task metadata (JSON, CSV, README table)

```bash
python policyloop/tasks/_utils/generate_task_metadata.py \
    --tasks-folder /path/to/your/tasks \
    --output-folder /path/to/your/tasks/_metadata \
    --subfolders pick_place stacking
```

If `--tasks-folder` is omitted, defaults to `TASK_DIR` (the built-in task library).
If `--subfolders` is omitted, scans all subfolders.

### View task statistics

```bash
python policyloop/tasks/_utils/compute_task_statistics.py \
    --metadata-file /path/to/your/tasks/_metadata/task_metadata.json

# Full comprehensive report
python policyloop/tasks/_utils/compute_task_statistics.py --verbose

# Individual sections
python policyloop/tasks/_utils/compute_task_statistics.py --objects     # Object frequency
python policyloop/tasks/_utils/compute_task_statistics.py --subtasks    # Subtask complexity
python policyloop/tasks/_utils/compute_task_statistics.py --episodes    # Episode length analysis
python policyloop/tasks/_utils/compute_task_statistics.py --difficulty   # Difficulty scoring
python policyloop/tasks/_utils/compute_task_statistics.py --by-scene    # Tasks grouped by scene

# Save report to file
python policyloop/tasks/_utils/compute_task_statistics.py --verbose --save
```

### Programmatic access

`load_task_info.py` provides importable helpers for extracting metadata from task classes:

```python
from policyloop.tasks._utils.load_task_info import extract_task_metadata
```
