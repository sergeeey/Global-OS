# EW2 repro

```bash
# from urllib3 worktree at pin SHA, editable install, then:
python3 repro_matrix.py
python3 -m pytest test_regression_blocksize_zero.py -q
```
