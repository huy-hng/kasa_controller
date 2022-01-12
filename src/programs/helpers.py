import datetime

def convert_datetime_to_time(with_date: datetime.datetime):
	without_date = datetime.time(
		with_date.hour,
		with_date.minute,
		with_date.second,
		with_date.microsecond)
	return without_date


