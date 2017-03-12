import os
import sys
import datetime
import pytz
from workflow import Workflow


def get_offset_str(timezone):
	now = datetime.datetime.now()
	return pytz.timezone(timezone).fromutc(now).strftime('%z')


TIMEZONE_LIST = [(tz, get_offset_str(tz)) for tz in pytz.all_timezones]


def get_timezone_list(prefix=None):
	return [(tz, offset) for tz, offset in TIMEZONE_LIST if prefix is None or tz.startswith(prefix)]


def get_system_timezone():
	link = os.readlink("/etc/localtime")
	tzname = link[link.rfind("zoneinfo/") + 9:]
	return get_timezone_list(tzname)[0]


def main(wf):
	args = wf.args

	tzname, tzoffset = get_system_timezone()

	wf.add_item(
			title=tzname,
			subtitle=tzoffset,
			valid=False,
		)

	wf.send_feedback()

if __name__ == '__main__':
	wf = Workflow()
	sys.exit(wf.run(main))
