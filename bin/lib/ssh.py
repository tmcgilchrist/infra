import logging
import os
import subprocess

logger = logging.getLogger('ssh')

# TODO maybe use paramiko?


HYPERVISOR_UUID = "/sys/hypervisor/uuid"
RUNNING_ON_EC2 = os.path.exists(HYPERVISOR_UUID) and open(HYPERVISOR_UUID, "r").read().startswith("ec2")


def ssh_address_for(instance):
    if RUNNING_ON_EC2:
        return instance.instance.private_ip_address
    else:
        return instance.instance.public_ip_address


def run_remote_shell(args, instance):
    logger.debug(f"Running remote shell on {instance}")
    ssh_command = 'ssh -o ConnectTimeout=5 ' \
                  '-o UserKnownHostsFile=/dev/null ' \
                  '-o StrictHostKeyChecking=no -o ' \
                  'LogLevel=ERROR'
    if args['mosh']:
        ssh_command = f'mosh --ssh=\'{ssh_command}\''
    os.system(f'{ssh_command} ubuntu@{ssh_address_for(instance)}')


def exec_remote(instance, command):
    logger.debug(f"Running '{' '.join(command)}' on {instance}")
    return subprocess.check_output(ssh_args_for(command, instance)).decode('utf-8')


def exec_remote_to_stdout(instance, command):
    logger.debug(f"Running '{' '.join(command)}' on {instance}")
    subprocess.check_call(ssh_args_for(command, instance))


def ssh_args_for(command, instance):
    return ['ssh', '-o', 'ConnectTimeout=5', '-o', 'UserKnownHostsFile=/dev/null', '-o', 'StrictHostKeyChecking=no',
            '-o', 'LogLevel=ERROR',
            'ubuntu@' + ssh_address_for(instance), '--'] + [f"'{c}'" for c in command]


def exec_remote_all(instances, command):
    for instance in instances:
        result = exec_remote(instance, command)
        print(f'{instance}: {result or "(no output)"}')
