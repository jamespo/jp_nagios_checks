#!/usr/bin/env python3
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
import os
import sys
import argparse

# Nagios exit codes
OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

import subprocess

def get_folder_size_kb(folder_path):
    """Calculates folder size in KB using the 'du' command to match original script."""
    try:
        # Original: du --max-depth=1 $folder|tail -1 |awk ...
        # We can just use du -sk which gives total in KB
        output = subprocess.check_output(["du", "-sk", folder_path], stderr=subprocess.DEVNULL)
        size_kb = int(output.split()[0])
        return size_kb
    except (subprocess.CalledProcessError, ValueError, IndexError) as e:
        print(f"ERROR: Could not get folder size: {e}")
        sys.exit(CRITICAL)

def main():
    parser = argparse.ArgumentParser(
        description="Check folder size and return Nagios status.",
        add_help=False
    )
    parser.add_argument("-f", "--folder", help="Folder to check")
    parser.add_argument("-s", "--scale", choices=["k", "m", "g", "K", "M", "G"], default="k", help="Scale (k, m, g)")
    parser.add_argument("-w", "--warning", type=float, default=0, help="Warning threshold")
    parser.add_argument("-c", "--critical", type=float, default=0, help="Critical threshold")
    parser.add_argument("-h", "--help", action="store_true", help="Show help")

    # Manual parsing to match the original script's behavior if needed, 
    # but argparse is cleaner and standard.
    args, unknown = parser.parse_known_args()

    usage = f"Usage {sys.argv[0]} -f dir [-s (k|m|g)] [-w (size)] [-c (size)]"

    if args.help or not args.folder:
        print(usage)
        sys.exit(UNKNOWN)

    if not os.path.isdir(args.folder):
        print("ERROR: Folder is invalid")
        sys.exit(1) # Original script exits 1 on invalid folder

    # Determine divisor and unit
    scale = args.scale.lower()
    if scale == "k":
        divisor = 1
        unit = "KB"
    elif scale == "m":
        divisor = 1024
        unit = "MB"
    elif scale == "g":
        divisor = 1024 * 1024
        unit = "GB"
    else:
        print("Please use:\nk for Kilobytes(KB) data\nm for Megabytes (MB) data\ng for Gigabytes (GB) data")
        sys.exit(UNKNOWN)

    # Get size in KB then convert
    size_kb = get_folder_size_kb(args.folder)
    size = size_kb / divisor

    # Validation: if both are set, critical must be > warning
    if args.warning > 0 and args.critical > 0 and args.warning >= args.critical:
        print(usage)
        sys.exit(UNKNOWN)
    
    status = OK
    status_text = "OK"

    # If critical is set and exceeded
    if args.critical > 0 and size > args.critical:
        status = CRITICAL
        status_text = "CRITICAL"
    # Else if warning is set and exceeded
    elif args.warning > 0 and size > args.warning:
        status = WARNING
        status_text = "WARNING"

    # The original script had logic for when warning > critical, 
    # but typically critical is the higher priority.
    
    print(f"{status_text}: The folder size is {size:.2f}{unit}|size={size:.2f}{unit}")
    sys.exit(status)

if __name__ == "__main__":
    main()
