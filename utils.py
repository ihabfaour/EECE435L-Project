import cProfile
import pstats
from line_profiler import LineProfiler
import os
from functools import wraps

PROFILE_OUTPUT_FILE = "route_profile.prof"

def profile_route(func):
    """
    A decorator to profile specific Flask route handlers.
    Captures and saves cumulative execution stats for visualization.

    :param func: The Flask route handler to profile.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Initialize the profiler
        profiler = cProfile.Profile()
        profiler.enable()
        
        # Call the actual route function
        result = func(*args, **kwargs)
        
        profiler.disable()

        # Save profiling stats for only the current route to a file
        if os.path.exists(PROFILE_OUTPUT_FILE):
            # Append to existing file
            with open(PROFILE_OUTPUT_FILE, "a") as file:
                stats = pstats.Stats(profiler, stream=file)
                stats.strip_dirs().sort_stats("cumulative")
                stats.print_stats(2)  # Only print the top 2 lines (relevant stats)
        else:
            # Create a new file
            with open(PROFILE_OUTPUT_FILE, "w") as file:
                stats = pstats.Stats(profiler, stream=file)
                stats.strip_dirs().sort_stats("cumulative")
                stats.print_stats(2)

        return result

    return wrapper


LINE_PROFILE_OUTPUT_FILE = "line_profile_output.txt"

def line_profile(func):
    """
    Decorator to enable line profiling for the given function.
    Requires the 'line_profiler' tool.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Initialize the line profiler
        profiler = LineProfiler()
        profiler.add_function(func)  # Add the function to the profiler
        
        # Profile the function call
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        
        # Save profiling stats to a text file
        with open(LINE_PROFILE_OUTPUT_FILE, "a") as file:
            file.write(f"\nProfiling results for function: {func.__name__}\n")
            profiler.print_stats(stream=file)
        
        return result

    return wrapper

