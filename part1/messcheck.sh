#!/usr/bin/env bash
# Check the environment before a MESS memory benchmark.
# This script only reports system state; it does not change any settings.

echo '=== 1. POWER PROFILE ==='
if command -v powerprofilesctl >/dev/null 2>&1; then
    powerprofilesctl get
else
    echo 'powerprofilesctl unavailable'
fi

echo
echo '=== 2. AC POWER ==='
found_adapter=false
for supply in /sys/class/power_supply/*; do
    [[ -f "$supply/type" ]] || continue
    if [[ $(<"$supply/type") == Mains ]]; then
        printf '%s: ' "$(basename "$supply")"
        cat "$supply/online"
        found_adapter=true
    fi
done
if [[ $found_adapter == false ]]; then
    echo 'AC adapter information unavailable'
fi

echo
echo '=== 3. CPU ENERGY PERFORMANCE PREFERENCE ==='
epp=/sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference
if [[ -r "$epp" ]]; then
    cat "$epp"
else
    echo 'EPP information unavailable'
fi

echo
echo '=== 4. PERF PERMISSION ==='
if [[ -r /proc/sys/kernel/perf_event_paranoid ]]; then
    cat /proc/sys/kernel/perf_event_paranoid
else
    echo 'perf_event_paranoid unavailable'
fi

echo
echo '=== 5. PERF PATH ==='
command -v perf || echo 'perf not found in PATH'

echo
echo '=== 6. GUI PROCESS CHECK ==='
ps -eo pid,comm | awk '
    $2 ~ /^(firefox|gnome-shell|Xorg|Xwayland)$/ { print; found=1 }
    END { if (!found) print "No matching GUI processes detected" }
'

echo
echo '=== 7. CURRENT CPU USAGE (SECOND SAMPLE) ==='
# Use the second top snapshot instead of ps lifetime-average CPU percentages.
LC_ALL=C top -b -d 1 -n 2 | awk '/^top -/ { sample++ } sample == 2' | head -20
