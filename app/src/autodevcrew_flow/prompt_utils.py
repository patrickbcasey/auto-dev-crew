class SwePrompts:
    stacktrace_function: str

    def __init__(self):
        self.stacktrace_function = r"""def print_stacktrace(e: Exception):\n
        import traceback
        import sys
        tb = traceback.extract_tb(e.__traceback__)\n
        print("Traceback (most recent call last):", file=sys.stderr)\n
        for frame in tb:\n
            line_number = frame.lineno\n
            code_context = frame.line.strip() if frame.line else "Unknown"\n
            print(f'  File \"{frame.filename}\"', file=sys.stderr)\n
            print(f"    {line_number}: {code_context}", file=sys.stderr)\n
        print(f"{e.__class__.__name__}: {e}", file=sys.stderr)\n"""
