import os
import sys
import datetime
import re

import pytz
import optparse
from workflow import Workflow3

TIMEZONE_FILE = 'timezone'


def get_offset_str(timezone):
	now = datetime.datetime.now()
	return pytz.timezone(timezone).fromutc(now).strftime('%z')


TIMEZONE_LIST = [(tz, get_offset_str(tz)) for tz in pytz.all_timezones]


def get_timezone_list(pattern=None):
	return [(tz, offset) for tz, offset in TIMEZONE_LIST if pattern is None or re.search(pattern, tz, re.IGNORECASE)]


def get_system_timezone():
	link = os.readlink("/etc/localtime")
	tzname = link[link.rfind("zoneinfo/") + 9:]
	return get_timezone_list(tzname)[0]


def get_timezone(wf):
	if wf.stored_data('timezone') is None:
		return get_system_timezone()
	return wf.stored_data('timezone'), wf.stored_data('tzoffset')


def set_timezone(wf, timezone):
	tzname, tzoffset = get_timezone_list(timezone)[0]
	wf.store_data('timezone', tzname)
	wf.store_data('tzoffset', tzoffset)


def main(wf):
	parser = optparse.OptionParser('')
	parser.add_option("--set-timezone", action='store', default=None, dest="timezone")
	(options, args) = parser.parse_args(args=wf.args)

	if options.timezone:
		set_timezone(wf, options.timezone)
		return

	tzname, tzoffset = get_timezone(wf)

	if not args[0]:
		wf.add_item(
			title="%s (%s)" % (tzname, tzoffset),
			subtitle="Please enter a new timezone",
			valid=False,
			icon='4A0D7DE9-2E5C-4521-A8E0-9EF0F7592F26.png',
		)
	else:
		for tzname, tzoffset in get_timezone_list(args[0]):
			wf.add_item(
				title=tzname,
				subtitle=tzoffset,
				uid=tzname,
				valid=True,
				arg=tzname,
			)

	wf.send_feedback()


if __name__ == '__main__':
	wf = Workflow3()
	sys.exit(wf.run(main))
