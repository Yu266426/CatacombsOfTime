import cProfile
import functools

is_profiling = False
profiler = cProfile.Profile()


def profile(func):
	global is_profiling
	is_profiling = True

	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		profiler.enable()
		result = func(*args, **kwargs)
		profiler.disable()
		return result

	return wrapper


def save_profile_data(filename=None):
	if is_profiling:
		profiler.dump_stats(filename or "stats.prof")
