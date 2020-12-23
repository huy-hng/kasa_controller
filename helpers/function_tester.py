def pad(num):
	return str(num).rjust(3)

def create_fn(exp, offset, print_details=False):
	div = round(((100+offset)**exp) / 100)
	if print_details:
		print(f'{exp=} {offset=} {div=}')
	return lambda x: pad(round(((x+offset)**exp) / div))
  
def get_offset(exp):
	val1 = 0
	val2 = 0

	offset = 0
	while True:
		offset += 1
		test_fn = create_fn(exp, offset)
		val1 = int(test_fn(5))
		val2 = int(test_fn(6))

		if val1 == 2 and val2 == 3:
			return offset
	

def get_fn(exp):
	offset = get_offset(exp)
	return create_fn(exp, offset, True)

functions = [
	create_fn(2, 0, True),
	get_fn(2),
	get_fn(3),
	get_fn(4),
]

fn = create_fn(3, 33)

for val in range(101):
	value = round(( (val + 33)**3 ) / 23526)
	internal_value = round( ((23526*value)**(1/3)) - 33 )
	print(val, internal_value, value)

# for i in range(100, 0, -1):
# 	print(pad(i), fn(i))
	# line = f'{pad(i)}'
	# for fn in functions:
	# 	line += f' {fn(i)}'
	# print(line), 

