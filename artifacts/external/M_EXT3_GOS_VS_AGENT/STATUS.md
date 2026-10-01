# M-EXT3 GOS vs Agent — Status

**Status:** `PREREG_LOCKED_AWAITING_TASK_PIN`  
**Protocol:** `M-EXT3-GSA-v1`  
**Arms started:** `false`

## Sequence position

```text
M-EXT1 / EW2  IMMUTABLE   ROOT_CAUSE_CONFIRMED
M-EXT2 / EW1  CLOSED      INCONCLUSIVE
M-EXT3 / GSA  PREREG      awaiting external OSS task pin
```

## Next exact action

1. Select OSS incident under `TASK_SELECTION.md`  
2. Write `TASK_PIN.json`  
3. Freeze public pack  
4. Only then start Arm A / Arm B under equal budgets  

Do **not** polish M-EXT1 urllib3 for self-score. Do **not** M-EXT2-F2.
