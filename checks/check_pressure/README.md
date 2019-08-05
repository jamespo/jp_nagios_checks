# check_pressure

*Nagios / Icinga monitor for /proc/pressure on 4.2+ kernels*

## Intro

/proc/pressure aka Pressure Stall Information (PSI) is a new-ish interface in the linux kernel to see if tasks are waiting on CPU, IO or memory. Think of it as load++

For more details see https://facebookmicrosites.github.io/psi/docs/overview

## Usage

     check_pressure.py [options]
           
     Options:
          -h, --help   show this help message and exit
          -w WARNING   warning thresholds [default:
               "somecpu10>0.2,fullio10>0.2,fullmemory10>0.2"]
          -c CRITICAL  critical thresholds [default:
               "somecpu10>0.5,fullio10>0.5,fullmemory10>0.5"]


## Requirements

Python 2 or Python 3 (recommended)
