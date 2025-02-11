# Helper script for the Tiltfile's apply cmd. Not intended to be called independently.
#
# Usage:
# python3 helm-apply-helper.py ... [image config keys in order]

import os
import subprocess
import sys

flags = sys.argv[1:]

image_count = int(os.environ['TILT_IMAGE_COUNT'])
for i in range(image_count):
  image = os.environ['TILT_IMAGE_%s' % i]
  key = os.environ.get('TILT_IMAGE_KEY_%s' % i, '')
  if key:
    flags.extend(['--set', '%s=%s' % (key, image)])
    continue

  key1 = os.environ.get('TILT_IMAGE_KEY_REPO_%s' % i, '')
  key2 = os.environ.get('TILT_IMAGE_KEY_TAG_%s' % i, '')
  parts = image.split(':')
  repo = ':'.join(parts[:len(parts)-1])
  tag = ':'.join(parts[len(parts)-1:])
  flags.extend(['--set', '%s=%s' % (key1, repo),
                '--set', '%s=%s' % (key2, tag)])
install_cmd = ['helm', 'upgrade', '--install']
install_cmd.extend(flags)

get_cmd = ['helm', 'get', 'manifest']
kubectl_cmd = ['kubectl', 'get']

release_name = os.environ['RELEASE_NAME']
chart = os.environ['CHART']
namespace = os.environ.get('NAMESPACE', '')
if namespace:
  install_cmd.extend(['--namespace', namespace])
  get_cmd.extend(['--namespace', namespace])
  kubectl_cmd.extend(['--namespace', namespace])

install_cmd.extend([release_name, chart])
get_cmd.extend([release_name])
kubectl_cmd.extend(['-oyaml', '-f', '-'])

print("Running cmd: %s" % install_cmd, file=sys.stderr)
subprocess.check_call(install_cmd, stdout=sys.stderr)

print("Running cmd: %s" % get_cmd, file=sys.stderr)
out = subprocess.check_output(get_cmd)

print("Running cmd: %s" % kubectl_cmd, file=sys.stderr)
completed = subprocess.run(kubectl_cmd, input=out)
completed.check_returncode()
