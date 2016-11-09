#!/usr/bin/python
#
# The vm should not be pinned on the fast-path core. To exclude this core, we
# use the vcpu_pin_set option in nova.conf.
#
# This small program generates the value for the vcpu_pin_set option by
# parsing the fast-path.env file or fp-conf-tool command output (if the
# file does not exist).
#
# vcpu_pin_set=$(python get_vcpu_pin_set.py)
# openstack-config --set /etc/nova/nova.conf DEFAULT vcpu_pin_set $vcpu_pin_set

import multiprocessing
import os
import re
import shlex
import subprocess
import sys


def error(msg):
    sys.stderr.write('%s: error: %s\n' % (sys.argv[0], msg))
    sys.exit(1)

def get_fp_config(conf_rootdir):
    """
    Retrieve fastpath config.
    Try first with zero conf tool and, in case of failures, return fastpath.env
    file content
    """
    fp_conf = run_fp_conf_tool(conf_rootdir)

    if fp_conf is None:
        return read_fp_conf_file(conf_rootdir)
    else:
        return fp_conf

def read_fp_conf_file(conf_rootdir):
    """
    Return fastpath.env file content
    """
    fast_path_conf_file = os.path.join(conf_rootdir, "fast-path.env")

    if os.path.exists(fast_path_conf_file):
        with open(fast_path_conf_file) as f:
            buf = f.read()
        return buf

    return None

def run_fp_conf_tool(conf_rootdir):
    """
    Exec fp-conf-tool command and return its output.

    If the file 6WIND_product is found use its content for the --product option
    else we use the default value (--product option not set)
    """
    fast_path_product_file = os.path.join(conf_rootdir, "6WIND_product")

    if os.path.exists(fast_path_product_file):
        with open(fast_path_product_file) as f:
            buf = f.read().rstrip()

        cmd = "fp-conf-tool --product={product} --dump --full --strip-comments"
        cmd = cmd.format(product=buf)
    else:
        cmd = "fp-conf-tool --dump --full --strip-comments"

    try:
        env = os.environ.copy()
        # check if PATH contains /usr/local/bin for fp-conf-tool
        if not '/usr/local/bin' in env['PATH']:
            env['PATH'] = '/usr/local/bin:' + env['PATH']
        process = subprocess.Popen(shlex.split(cmd),
                                   env=env,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
    except os.error as e:
        sys.stderr.write("'%s' has failed. Error: %s." % (cmd, e))
        return None

    stdout, _ = process.communicate()
    retcode = process.wait()

    if retcode != 0:
        sys.stderr.write("'%s' returned error status %d. Output:\n%s" % (cmd, retcode, stdout))
        return None

    return stdout

def fp_mask_to_list(fp_mask):
   """
   Parse a fp_mask, eg 1-4,2,3 or 0x202
   """
   if '0x' in fp_mask:
      fp_cpus = [ i for i in range(0, 64) if (1<< i) & int(fp_mask, 16)]
   else:
      fp_cpus = []
      for rule in fp_mask.split(','):
         if '-' in rule:
            # range of cpus
            start, end = rule.split('-', 1)
            try:
               fp_cpus += range(int(start), int(end)+1)
            except ValueError:
               raise exception("Invalid range expression %s" % rule)
         else:
            # single cpu
            try:
               fp_cpus.append(int(rule))
            except ValueError:
               raise exception("Invalid cpu number %s" % rule)
   return fp_cpus

def get_fp_mask(conf_rootdir):
    """
    Return FP_MASK content from fastpath configuration.
    This method is able to extract the FP_MASK value from both fp-conf-tool and
    fast-path.env file output
    """
    fp_conf = get_fp_config(conf_rootdir)

    if fp_conf is None:
        error("Unable to retrieve fastpath configuration")

    m = re.search('^FP_MASK=(?P<fp_mask>.*)$', fp_conf, re.MULTILINE)

    if m is None:
        m = re.search('^: \${FP_MASK:=(?P<fp_mask>.*)}', fp_conf, re.MULTILINE)
        if m is None:
            error("Cannot find FP_MASK")

    fp_mask = m.group('fp_mask')
    return fp_mask

conf_rootdir = os.getenv("CONF_ROOTDIR", "/usr/local/etc")
fp_mask = get_fp_mask(conf_rootdir)

list_fp_cpus = fp_mask_to_list(fp_mask)
no_fp_cpus = ',^'.join(map(str, list_fp_cpus))
nb_cpus = multiprocessing.cpu_count()
print '0-%d,^%s'%(nb_cpus-1, no_fp_cpus)
