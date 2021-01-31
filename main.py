import sys
import os
import re
import subprocess
from workflow import Workflow3
from timezone import get_timezone

DATE_BIN = '/usr/local/opt/coreutils/libexec/gnubin/date'

FORMATS = [
		"+'%s'",
		# 1937-01-01 12:00:27
		"+'%Y-%m-%d %H:%M:%S'",
		# 19 May 2002 15:21:36
		"+'%d %b %Y %H:%M:%S'",
		# Sun, 19 May 2002 15:21:36
		"+'%a, %d %b %Y %H:%M:%S'",
		# 1937-01-01T12:00:27
		"+'%Y-%m-%dT%H:%M:%S'",
		# 19370101120027
		"+'%Y%m%d%H%M%S'",
		# 1996-12-19T16:39:57-0800
		"+'%Y-%m-%dT%H:%M:%S%z'",
		"+'%Y-%m-%d %H:%M:%S %Z'",
]

def exec_cmd(timezone, from_format="now", to_format=""):
	command = "TZ={tz} {command} {to_format} --date=\"{from_format}\"".format(
			tz=timezone,
			command=DATE_BIN,
			to_format=to_format,
			from_format=from_format,
	)
	return [i.strip() for i in subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()]

def get_datetime(wf, dt_format, input_str):
	timezone, tzoffset = get_timezone(wf)

	# Unify input_str
	input_str = input_str and input_str.strip() or 'now'
	input_str = input_str.replace('tmr', 'tomorrow').replace('ytd', 'yesterday')
	if input_str.isdigit():
		input_str = "@{}".format(input_str)

	rc = re.findall(r'^(@\d+)(\s.*){0,1}', input_str)
	if rc:
		timestamp, successor = rc[0]
		rc, _ = exec_cmd(timezone, '{}'.format(timestamp))
		input_str = "{} {}".format(rc, successor)

	return exec_cmd(timezone, input_str, dt_format)


def check_datetime_bin():
	return os.path.isfile(DATE_BIN)


def is_valid_input(input):
	return re.match(r'[0-9A-Za-z :+-]*', input) is not None


def main(wf):
	args = wf.args

	if not check_datetime_bin():
		wf.add_item(
			title=u'Please install GNU date tool',
			subtitle=u'brew install coreutils',
			valid=True,
			arg=u'brew install coreutils',
		)
		wf.send_feedback()
		return

	input_str = ' '.join(args)

	if is_valid_input(input_str):
		for dt_format in FORMATS:
			formating_dt_str, err_msg = get_datetime(wf, dt_format, input_str)
			if err_msg:
				break
			wf.add_item(
				title=formating_dt_str,
				subtitle=dt_format,
				valid=True,
				arg=formating_dt_str,
				uid=dt_format,
			)

	if len(wf._items) == 0:
		wf.add_item(
			title=u'Invalid input',
			subtitle=input_str,
			valid=False,
		)
	wf.send_feedback()


if __name__ == '__main__':
	wf = Workflow3()
	sys.exit(wf.run(main))
