import sys
import os


# Add src to the Python path to work around lambda package directory structure
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
