import json
import os
import sys
from run_kotlin_kernel import run_kernel

def run_kernel_idea_impl(connection_file: str, jar_args_file: str = None, executables_dir: str = None)->None:
    origin_kernel_dir = os.path.dirname(os.path.abspath(run_kernel.__file__))
    if jar_args_file is None:
        jar_args_file = os.path.join(origin_kernel_dir, 'config', 'jar_args.json')
    if executables_dir is None:
        executables_dir = origin_kernel_dir
    jars_dir = os.path.join(executables_dir, 'jars')
    with open(jar_args_file, 'r') as fd:
        jar_args_json = json.load(fd)
        main_jar = jar_args_json['mainJar']
        cp = jar_args_json['classPath']
        class_path_arg = os.pathsep.join([os.path.join(jars_dir, jar_name) for jar_name in cp])
        main_jar_path = os.path.join(jars_dir, main_jar)
        jar_args = [
            main_jar_path,
            '-classpath=' + class_path_arg,
            connection_file,
            '-home=' + executables_dir
        ]
        import requests
        import time
        skykoma_agent_server_api_base = os.getenv('SKYKOMA_AGENT_SERVER_API')
        start_kernel_api = skykoma_agent_server_api_base + "/startJupyterKernel"
        payload = json.dumps(jar_args[1:])
        print('launch remote repl server, api: {}, args: {}'.format(start_kernel_api, payload))
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(start_kernel_api, data=payload, headers=headers, timeout=30)
        except requests.exceptions.RequestException as e:
            print('launch remote repl server failed: {}'.format(e))
            return
        response_body = response.json()
        print('launch remote repl server reply code:{}, body: {}'.format(response.status_code, response_body))
        if response_body['code'] == 'S00000':
            while True:
                query_kernel_status_api = skykoma_agent_server_api_base + "/queryJupyterKernelStatus"
                payload = json.dumps({})
                headers = {"Content-Type": "application/json"}
                try:
                    response = requests.post(query_kernel_status_api, data=payload, headers=headers, timeout=5)
                except requests.exceptions.RequestException as e:
                    print('query remote repl server failed: {}, retrying...'.format(e))
                    time.sleep(1)
                    continue
                response_body = response.json()
                if response_body['data'] == 'RUNNING':
                    time.sleep(1)
                else:
                    print('remote repl server stoppted, code:{}, body: {}'.format(response.status_code, response_body))
                    break
        print('Kernel interrupted, exiting')
        os._exit(0)


def run_kernel_idea(*args) -> None:
    print(args)
    skykoma_agent_idea = 'idea' in os.getenv('SKYKOMA_AGENT_TYPE', '')
    if skykoma_agent_idea:
        run_kernel_idea_impl(*args)
    else:
        run_kernel(*args)


if __name__ == '__main__':
    run_kernel_idea(*(sys.argv[1:]))