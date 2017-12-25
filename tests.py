import unittest

all_tests = unittest.defaultTestLoader.discover('./test')
results = unittest.TestResult()
all_tests.run(results)

print(results)
