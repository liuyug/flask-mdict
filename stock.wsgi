import sys
import os.path


base_dir = os.path.abspath(os.path.dirname(__file__))

os.environ['APP_CONFIG_FILE'] = os.path.join(base_dir, 'config', 'release.py')
sys.path.insert(0, base_dir)


from server.app import app as application
