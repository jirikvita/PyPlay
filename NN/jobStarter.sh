#!/bin/bash

# jobStarter.sh v1.0
# Script for concurrent job execution by Tomas Komarek
# 
# For accepted parameters, see printHelp function or run ./jobStarter.sh -h
#  A single job list text file parameter is mandatory.
# Every line in the job file is expected to be a single job for execution, it will be executed
#  like this: bash -c "line contents". Any bash one-liner can be used as a job.
#  Empty lines and lines starting with '#' are ignored.
# Whenever there are less jobs running than NUMPARAJOBS, the script launches next job.
# Execution can be interrupted by SIGINT or SIGTERM, in this case the skript kills all jobs before exiting.
#  Jobs should not create new process groups, otherwise this cleanup will fail. If they do this, they should implement
#  cleanup of their own (by handling SIGTERM).
#
# return values:
#   0 -> success, all jobs finished
#   1 -> invalid input or terminated before jobs finished
#   2 -> internal error
# 
# Usage: ./jobStarter.sh [flags] <joblist.txt>
# 


#defaults

#time to sleep between checks for jobs not running - defaults to 1s since some older sleep implementations don't support decimals
#use the -s flag to override
SLEEP="1s" 

#switch whether to suppress output from the started jobs (stdout & stderr) or not
#set by the -q or -qq fags
# 0 -> no supression
# 1 -> stdout is suppressed, but stderr not
# 2 -> both stdout and stderr are suppressed
#for custom output behavior, edit the lines starting with: setsid bash -c "${JOBS[$RUN_NEXT]}"
SUPPRESS_OUTPUT=0

#verbose mode off
VERBOSE=0
#progress reports off
PROGRESS=0

#set up some output functions
function printUsage {
	echo
	echo "Usage: ./jobStarter.sh [flags] <joblist.txt>"
}

function printHelp {
	echo "jobStarter.sh - a script for concurrent job execution."
	echo "Each line of the input file is considered to be one job."
	printUsage
	echo "Available flags:"
	echo "    -h, --help          Print this help"
	echo "    -j, --jobs <num>    Run at most <num> parallel jobs, otherwise autodetect"
	echo "    -p, --progress      Show progress (jobs started/remaining)"
	echo "    -q, --quiet         Suppress job's stdout"
	echo "    -qq, --qquiet       Suppress job's stdout and stderr"
	echo "    -s, --sleep <time>  Substitute the default sleep command parameter \"1s\","
	echo "                        this is the period of the finished job check loop"
	echo "                        starting next jobs, must be a valid sleep parameter."
	echo "    -v, --verbose       Verbose mode (prints started jobs info, their PGID)"
	echo "    --                  Treat all following parameters as an input file name" 
	echo "                        even if they start with a dash"
}

function tooManyPars {
	echo >&2 "Error: too many parameters (more than one input file)."
	printUsage >&2
	exit 1
}

#parse parameters
END_OF_PARS=0
while [ "$#" -gt 0 ]; do
	if [[ "$1"  == "-"* && $END_OF_PARS == 0 ]]; then
		case "$1" in
		"-h" | "--help")
			printHelp
			exit
			;;
		"-j" | "--jobs")
			PARAM_JOBS="$2"
			shift
			if [ "$PARAM_JOBS" -gt 0 ] >/dev/null 2>&1; then
				: #null command
			else
				echo >&2 "Warning: invalid parallel jobs value \"$PARAM_JOBS\", resorting to autodetection"
			fi
			;;
		"-p" | "--progress")
			PROGRESS=1
			;;
		"-q" | "--quiet")
			SUPPRESS_OUTPUT=1
			;;
		"-qq" | "--qquiet")
			SUPPRESS_OUTPUT=2
			;;
		"-s" | "--sleep")
			SLEEP="$2"
			shift
			;;
		"-v" | "--verbose")
			VERBOSE=1
			;;
		"--")
			END_OF_PARS=1
			;;
		*)
			echo >&2 "Error: unknown parameter \"$1\""
			exit 1
			;;
		esac
	else
		if [ -n "$JOBFILE" ]; then
			#TODO: multiple input file support?
			tooManyPars
		fi
		JOBFILE="$1"
	fi
	
	shift
done


TERM_IN_PROGRESS=0 #if termination is already underway and another terminate signal is received, resort to SIGKILLing instead of SIGTERMing

#function to terminate/kill all jobs, used when receiving SIGINT or SIGTERM to exit cleanly
function killAllJobs {
	if [ $TERM_IN_PROGRESS -eq 0 ]; then
		#send SIGTERM to all jobs
		TERM_IN_PROGRESS=1
		if [ -n "$1" -o "$1" != "quiet" ]; then echo -e >&2 "\nTermination signal received, terminating all running jobs..."; fi
		for KILLJOB in ${JOBPIDS[*]}; do
			if [ $KILLJOB -gt 0 ]; then
				#terminates all processes with this PGID (derived from PID of group leader)
				if kill -s SIGTERM -- "-${KILLJOB}" >/dev/null 2>&1; then
					if [ $VERBOSE -gt 0 ]; then echo >&2 "Terminating PGID ${KILLJOB}..."; fi
				else
					if [ $VERBOSE -gt 0 ]; then echo >&2 "Terminating PGID ${KILLJOB}: job has already finished"; fi
				fi
			fi
		done
		echo "Waiting for jobs to terminate, send termination signal again to SIGKILL them."
		wait &&
		echo >&2 "All jobs terminated." &&
		exit 1
	else
		#send SIGKILL to all jobs
		if [ -n "$1" -o  "$1" != "quiet" ]; then echo -e >&2 "\nSecond termination signal received before jobs finished terminating."
			echo >&2 "Killing running jobs..."; fi
		for KILLJOB in ${JOBPIDS[*]}; do
			if [ $KILLJOB -gt 0 ]; then
				#kills all processes with this PGID (derived from PID of group leader)
				if kill -s SIGKILL -- "-${KILLJOB}" >/dev/null 2>&1; then
					if [ $VERBOSE -gt 0 ]; then echo >&2 "Killing PGID ${KILLJOB}: job killed"; fi
				else
					if [ $VERBOSE -gt 0 ]; then echo >&2 "Killing PGID ${KILLJOB}: job has already finished"; fi
				fi
			fi
		done
		echo >&2 "All jobs killed."
		exit 1
	fi
}

#traps for SIGINT/SIGTERM to exit cleanly
trap "killAllJobs" SIGINT SIGTERM #trap for SIGINT (^C) and SIGTERM, cleans up jobs before exiting

#number of cores autodetection, fallback to 1 if nproc not present
NUMCPU=$(nproc 2>/dev/null)
if [ $NUMCPU -gt 0 ] >/dev/null 2>&1; then
	NUMPARAJOBS=$NUMCPU
else
	NUMPARAJOBS=1
fi

#check if value given by -j is valid int >0, if yes, replace the default NUMPARAJOBS
if [ "$PARAM_JOBS" -gt 0 ] >/dev/null 2>&1; then
	NUMPARAJOBS="$PARAM_JOBS"
fi

if [ $PROGRESS -gt 0 -a $VERBOSE -gt 0 ]; then
	echo >&2 "Info: Ignoring progress flag since verbose is on."
	PROGRESS=0
fi


#is string empty?
if [ -z "$JOBFILE" ]; then
	echo >&2 "Error: No file with job list specified."
	printUsage
	exit 1
fi

#does file exist?
if [ ! -e "$JOBFILE" ]; then
	echo >&2 "Error: File \"$JOBFILE\" does not exist."
	exit 1
fi

#is it a folder?
if [ -d "$JOBFILE" ]; then
	echo >&2 "Error: No valid file with job list specified (\"$JOBFILE\" is a directory)."
	exit 1
fi

#fill array JOBS with commands from JOBFILE
while read -r line; do
	if [ -z "$line" ]; then continue; fi #skip empty lines
	if [[ "$line" == \#* ]]; then continue; fi #skip lines beginning with '#' character
	JOBS+=("$line") #add job to array
done <"$JOBFILE"
#TODO alternative: read stdin if -c flag present

TOTJOBS="${#JOBS[*]}" #total jobs to run

#are there any commands at all?
if [ "$TOTJOBS" -lt 1 ]; then
	echo >&2 "File $JOBFILE does not contain any jobs."
	exit
fi

if [ $VERBOSE -gt 0 ]; then
	echo >&2 "Running with max $NUMPARAJOBS concurrent jobs"
	echo >&2 "Found $TOTJOBS jobs in file \"$JOBFILE\""
fi

#prepare array with job PIDs
for iJOB in $(seq 1 $NUMPARAJOBS); do
	JOBPIDS[$iJOB]=0 #PID=0 is used as indication no job was started yet
done

RUN_NEXT=0 #stores index of next job from JOBS[] to be run when slot becomes available

#loop starting jobs
while [ $RUN_NEXT -lt $TOTJOBS ]; do
	#loop over indexes of array JOBPIDS
	for iPID in ${!JOBPIDS[*]}; do
		THISPID=${JOBPIDS[$iPID]}
		#not empty and greater than 0?
		if [ -n $iPID -a $THISPID -gt 0 ]; then
			#check if process is still running
			if kill -0 $THISPID >/dev/null 2>&1; then
				continue
			fi
		fi
		
		#break if no more jobs in array JOBS
		if [ -z "${JOBS[$RUN_NEXT]}" ]; then
			break
		fi
		
		#three variants, with/without job output supression, based on SUPPRESS_OUTPUT
		#jobs started with new PGID (Process Group ID) via setsid to easily kill all children without affecting anything else
		case "$SUPPRESS_OUTPUT" in
		"0")
			setsid bash -c "${JOBS[$RUN_NEXT]}" &
			;;
		"1")
			setsid bash -c "${JOBS[$RUN_NEXT]}" >/dev/null &
			;;
		"2")
			setsid bash -c "${JOBS[$RUN_NEXT]}" >/dev/null 2>&1 &
			;;
		*)
			echo >&2 "Internal error: Unknown SUPPRESS_OUTPUT setting \"$SUPPRESS_OUTPUT\", exiting."
			exit 2
			;;
		esac
		
		JOBPIDS[$iPID]=$! #store new job PID
		RUN_NEXT=$(($RUN_NEXT+1)) #increment counter, to start next job next time there is slot available
		if [ $PROGRESS -gt 0 ]; then echo -en >&2 "\rProgress: started $RUN_NEXT/$TOTJOBS jobs  "; fi
		if [ $VERBOSE -gt 0 ]; then echo >&2 "Starting job $RUN_NEXT of $TOTJOBS (PGID=$!)"; fi
	done
	
	#avoid sleeping when not necessary
	if [ ! $RUN_NEXT -lt $TOTJOBS ]; then
		break
	fi
	
	sleep "$SLEEP"
	if [ $? -ne 0 ]; then
		#rely on sleep to provide error message
		killAllJobs quiet
		exit 1
	fi
done

if [ $VERBOSE -gt 0 ]; then echo >&2 "No more jobs in queue, waiting for running jobs to finish..."; fi
wait && #wait for all jobs to finish (unless interrupted by SIGTERM/SIGINT)
if [ $PROGRESS -gt 0 ]; then echo >&2; fi
if [ $VERBOSE -gt 0 ]; then echo >&2 "All jobs finished."; fi &&
exit || killAllJobs

