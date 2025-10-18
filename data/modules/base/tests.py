import functools
import traceback


def test(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		print(f"\n== Running test: {func.__name__} ==")
		try:
			func(*args, **kwargs)
		except Exception as e:
			print(f"!! Test failed with exception: {type(e).__name__}: {e}")
			print("Traceback (most recent call last):")
			traceback.print_exc()
			print("Arguments passed:")
			print(f"  args: {args}")
			print(f"  kwargs: {kwargs}")
		else:
			print("-- Test passed successfully --")

	return wrapper
