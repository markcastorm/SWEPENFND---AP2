# Orchestrator Guide - AP2 Scraper

The orchestrator is your control center for managing the AP2 scraper. It provides scheduling, retry logic, monitoring, and maintenance features.

## Quick Start

### Windows Users (Easy Way)

Just double-click these files:

- **`install.bat`** - First time setup (installs everything)
- **`run.bat`** - Run the scraper once
- **`status.bat`** - Check scraper status
- **`schedule_daily.bat`** - Run daily at 9:00 AM

### Command Line Users

```bash
# Run once
python orchestrator.py run

# Run with retry logic
python orchestrator.py run --retry

# Check status
python orchestrator.py status
```

## Orchestrator Commands

### 1. Run Once

Run the scraper a single time:

```bash
python orchestrator.py run
```

**Options:**
- `--retry` - Enable automatic retry on failure
- `--max-retries 3` - Maximum number of retry attempts (default: 3)
- `--retry-delay 60` - Seconds between retries (default: 60)

**Examples:**
```bash
# Simple run
python orchestrator.py run

# Run with retry (3 attempts)
python orchestrator.py run --retry

# Run with custom retry settings
python orchestrator.py run --retry --max-retries 5 --retry-delay 120
```

### 2. Scheduled Runs

Run the scraper automatically at regular intervals:

```bash
python orchestrator.py schedule --interval 24
```

**Options:**
- `--interval 24` - Hours between runs (default: 24)
- `--no-immediate` - Don't run immediately on start

**Examples:**
```bash
# Run every 24 hours
python orchestrator.py schedule --interval 24

# Run every 6 hours
python orchestrator.py schedule --interval 6

# Run every 12 hours, but not immediately
python orchestrator.py schedule --interval 12 --no-immediate
```

### 3. Daily at Specific Time

Run the scraper daily at a specific time:

```bash
python orchestrator.py daily --hour 9 --minute 0
```

**Options:**
- `--hour 9` - Hour of day (0-23, default: 9)
- `--minute 0` - Minute of hour (0-59, default: 0)

**Examples:**
```bash
# Run daily at 9:00 AM
python orchestrator.py daily --hour 9 --minute 0

# Run daily at 2:30 PM
python orchestrator.py daily --hour 14 --minute 30

# Run daily at midnight
python orchestrator.py daily --hour 0 --minute 0
```

### 4. Status

Check orchestrator status and run history:

```bash
python orchestrator.py status
```

Shows:
- Total runs (successful and failed)
- Last run timestamp
- Last successful run
- Recent run history (last 10)
- Current configuration

**Example output:**
```
================================================================================
AP2 SCRAPER ORCHESTRATOR - STATUS
================================================================================
Total runs:       15
Successful runs:  14
Failed runs:      1
Last run:         20251106_143022
Last success:     20251106_143022

Recent runs (last 10):
--------------------------------------------------------------------------------
  20251106_143022: ✓ SUCCESS
  20251106_090015: ✓ SUCCESS
  20251105_090012: ✗ FAILED - Connection timeout
  ...
```

### 5. Clean Old Runs

Remove old run folders to save disk space:

```bash
python orchestrator.py clean --keep-days 30
```

**Options:**
- `--keep-days 30` - Number of days to keep (default: 30)

Cleans:
- Old log folders
- Old download folders
- Old output folders (keeps "latest" folder)

**Examples:**
```bash
# Keep last 30 days
python orchestrator.py clean --keep-days 30

# Keep last 7 days
python orchestrator.py clean --keep-days 7

# Keep last 90 days
python orchestrator.py clean --keep-days 90
```

## Orchestrator Features

### 1. State Tracking

The orchestrator maintains a state file (`orchestrator_state.json`) that tracks:

- Last run timestamp
- Last successful run
- Total/successful/failed run counts
- Run history (last 100 runs)

### 2. Automatic Retry

When enabled with `--retry`, the orchestrator will:

1. Try to run the scraper
2. If it fails, wait the retry delay
3. Try again (up to max retries)
4. Log all attempts

### 3. Error Recovery

The orchestrator handles errors gracefully:

- Catches and logs all exceptions
- Updates state even on failure
- Continues scheduled runs after errors
- Provides detailed error information in logs

### 4. Logging

The orchestrator maintains its own log file:

- Location: `logs/orchestrator.log`
- Contains all orchestrator activity
- Separate from individual scraper run logs

### 5. Monitoring

Easy monitoring with the status command:

```bash
python orchestrator.py status
```

Check:
- Success rate
- Last run time
- Recent failures
- Current configuration

## Usage Scenarios

### Scenario 1: One-Time Manual Run

You want to run the scraper once manually:

```bash
python orchestrator.py run --retry
```

### Scenario 2: Daily Automated Runs

You want the scraper to run every morning at 9 AM:

```bash
python orchestrator.py daily --hour 9 --minute 0
```

Keep this terminal window open or run as a background service.

### Scenario 3: Frequent Updates

You want to check for updates every 6 hours:

```bash
python orchestrator.py schedule --interval 6
```

### Scenario 4: Check Status Before Running

Before running, check the last execution:

```bash
python orchestrator.py status
python orchestrator.py run --retry
```

### Scenario 5: Maintenance

Clean up old files monthly:

```bash
python orchestrator.py clean --keep-days 30
```

## Running as a Background Service

### Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily/weekly/at startup)
4. Action: Start a program
5. Program: `python`
6. Arguments: `"C:\Users\casto\Documents\SWEPENFND – AP2\orchestrator.py" run --retry`
7. Start in: `C:\Users\casto\Documents\SWEPENFND – AP2`

### Linux/Mac (cron)

Add to crontab:

```bash
# Run daily at 9 AM
0 9 * * * cd /path/to/project && python orchestrator.py run --retry

# Run every 6 hours
0 */6 * * * cd /path/to/project && python orchestrator.py run --retry
```

### Using nohup (Linux/Mac)

Run in background, survives logout:

```bash
nohup python orchestrator.py daily --hour 9 --minute 0 > orchestrator.out 2>&1 &
```

## Integration with Config

The orchestrator respects your [config.py](config.py) settings:

- `TARGET_YEAR` - Which year to scrape
- `REPORT_TYPES` - Which report types to download
- `OUTPUT_CONFIG` - Output format preferences

To change what gets scraped, edit [config.py](config.py), then run the orchestrator.

## Monitoring and Alerts

### Check Status Regularly

```bash
python orchestrator.py status
```

### Review Logs

- Orchestrator log: `logs/orchestrator.log`
- Individual run logs: `logs/YYYYMMDD_HHMMSS/scraper_*.log`

### Success Indicators

- Status shows recent successful runs
- `output/latest/` folder contains fresh data
- No error messages in logs

### Failure Indicators

- Status shows failed runs
- Error messages in `orchestrator.log`
- Missing or old data in `output/latest/`

## Best Practices

1. **Test First**: Run `python test_config.py` before scheduling

2. **Start Manual**: Run once manually before scheduling:
   ```bash
   python orchestrator.py run --retry
   ```

3. **Monitor Initially**: Check status after first few scheduled runs:
   ```bash
   python orchestrator.py status
   ```

4. **Regular Cleanup**: Clean old files monthly:
   ```bash
   python orchestrator.py clean --keep-days 30
   ```

5. **Review Logs**: Check logs if failures occur:
   ```bash
   cat logs/orchestrator.log
   ```

6. **Backup State**: The `orchestrator_state.json` file tracks history - back it up

## Troubleshooting

### Orchestrator won't start

**Problem**: Import errors or missing files

**Solution**:
```bash
python test_config.py
pip install -r requirements.txt
```

### Scheduled runs not working

**Problem**: Process stopped or system restarted

**Solution**: Use Task Scheduler (Windows) or cron (Linux) for persistence

### Status shows all failures

**Problem**: Configuration or connectivity issues

**Solution**:
1. Check `logs/orchestrator.log` for errors
2. Verify [config.py](config.py) settings
3. Test manually: `python orchestrator.py run`

### Disk space filling up

**Problem**: Too many old runs stored

**Solution**:
```bash
python orchestrator.py clean --keep-days 7
```

## Command Reference

```bash
# Run commands
python orchestrator.py run                                    # Run once
python orchestrator.py run --retry                            # Run with retry
python orchestrator.py run --retry --max-retries 5           # Custom retry

# Schedule commands
python orchestrator.py schedule --interval 24                 # Every 24 hours
python orchestrator.py schedule --interval 6 --no-immediate  # Every 6 hours, no immediate run
python orchestrator.py daily --hour 9 --minute 0             # Daily at 9:00 AM

# Maintenance commands
python orchestrator.py status                                 # Show status
python orchestrator.py clean --keep-days 30                  # Clean old files

# Help
python orchestrator.py --help                                # Show all commands
python orchestrator.py run --help                            # Help for specific command
```

## Examples

### Example 1: Daily Production Run

```bash
# Set configuration for latest year
# Edit config.py: TARGET_YEAR = "latest"

# Start daily scheduled runs at 9 AM
python orchestrator.py daily --hour 9 --minute 0
```

### Example 2: Backfill Historical Data

```bash
# Edit config.py: YEARS_TO_SCRAPE = [2024, 2023, 2022, 2021]
# Run once with retry
python orchestrator.py run --retry --max-retries 5 --retry-delay 120

# Check status
python orchestrator.py status

# View results
ls output/latest/
```

### Example 3: Monitoring Setup

```bash
# Check status before scheduling
python orchestrator.py status

# Start scheduled runs
python orchestrator.py schedule --interval 24

# In another terminal, check status periodically
python orchestrator.py status
```

---

**Pro Tip**: Use `run.bat` (Windows) for quick manual runs without typing commands!
