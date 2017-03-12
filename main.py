import sys
import os
import re
import subprocess
from workflow import Workflow

DATE_BIN = '/usr/local/opt/coreutils/libexec/gnubin/date'

FORMATS = [
	"+%s",
	# 1937-01-01 12:00:27
	"+%Y-%m-%d %H:%M:%S",
	# 19 May 2002 15:21:36
	"+%d %b %Y %H:%M:%S",
	# Sun, 19 May 2002 15:21:36
	"+%a, %d %b %Y %H:%M:%S",
	# 1937-01-01T12:00:27
	"+%Y-%m-%dT%H:%M:%S",
	# 1996-12-19T16:39:57-0800
	"+%Y-%m-%dT%H:%M:%S%z",
]


def get_datetime(dt_format, input):
	if not input:
		input = 'now'
	command = "%s \"%s\" --date=\"%s\"" % (DATE_BIN, dt_format, input)
	return [i.strip() for i in subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()]


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
			formating_dt_str, err_msg = get_datetime(dt_format, input_str)
			if err_msg:
				break
			wf.add_item(
				title=formating_dt_str,
				subtitle=dt_format,
				valid=True,
				arg=formating_dt_str,
				uid=dt_format,
			)

	print >>sys.stderr, wf.alfred_env
	if len(wf._items) == 0:
		wf.add_item(
			title=u'Invalid input',
			subtitle=input_str,
			valid=False,
		)
	wf.send_feedback()


if __name__ == '__main__':
	wf = Workflow()
	sys.exit(wf.run(main))
