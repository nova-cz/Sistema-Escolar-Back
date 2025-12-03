import sys
import os

print("Executable:", sys.executable)
print("Path:")
for p in sys.path:
    print(p)

try:
    import django
    print("Django:", django.__file__)
except ImportError:
    print("Django not found")

try:
    import dj_database_url
    print("dj_database_url:", dj_database_url.__file__)
except ImportError as e:
    print("dj_database_url error:", e)
