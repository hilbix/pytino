
"""
THIS IS A DOCSTRING
"""

def main():
	import json

	m	= __import__(__name__).__dict__
	for k,v in m.items():
		print(json.dumps((str(k),str(v))))

main()

