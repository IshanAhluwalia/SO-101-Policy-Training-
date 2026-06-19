# Open Decisions

## Hardware
- [ ] wrist_flex (motor 4) on leader arm has faulty encoder randomly resetting to 0 — needs motor replacement or cable reseating
- [ ] shoulder_lift (motor 2) and wrist_flex (motor 4) calibrated to full range 0–4095 on both arms — redo calibration carefully stopping before hard stops
- [ ] wrist_roll (motor 5) on follower had overload event — monitor for recurrence

## Software
- [ ] GitHub auth not yet set up via SSH — currently using gh CLI with HTTPS
- [ ] `max_relative_target=5` in teleop.sh is a workaround for missing calibration — once arms are properly calibrated this can be removed or increased

## Next Steps
- [ ] Properly recalibrate both arms (wrist_flex and shoulder_lift especially)
- [ ] Verify teleop runs stably after recalibration
- [ ] Set up data recording pipeline for policy training
