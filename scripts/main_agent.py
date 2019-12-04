import requests
import sys
import json
import logging
import subprocess
from base64 import b64decode
from concurrent.futures import ThreadPoolExecutor, wait

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

def _decrypt_message(msg):
    decrypt_process = subprocess.Popen(['openssl', 'rsautl', '-decrypt',
    '-inkey', 'private.pem'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE)
    b64_msg = b64decode(msg)

    decrypt_process.stdin.write(b64_msg)
    try:
        outs, err = decrypt_process.communicate(timeout=0.1)
        return json.loads(outs.decode('utf-8'))
    except subprocess.TimeoutExpired:
        raise ValueError("decryption process timedout")


def chunkify(lst, n):
    return (lst[i::n] for i in range(n))

def post_command_to_agent(miners, command , mc):
    logging.debug('sending {} miners to {}'.format(len(miners), mc))
    query_string = {"command": command}
    try:
        response = requests.post('http://{}:8080/process_command'.format(mc),
                                json={'miners': miners},
                                params=query_string)
        logging.debug(response.text)
    except Exception as e:
        logging.error(repr(e))

def main(json_line):
    '''This is a parser that dispatch orders to the sub_agents'''
    if json_line and "type" in json_line and "mccmd1" == json_line["type"]:
        # decrypt the cmd_payload
        try:
            cmd_payload = _decrypt_message(json_line["cmd_payload"])
        except ValueError as e:
            logging.error(repr(e))
            return

        miners = json_line["miners"]

        logging.debug("received orders to {} for {} miners".format(
            cmd_payload,
            len(miners)))

        mine_controllers = ['10.101.0.9', '10.101.0.14']
        available_mine_controllers = []

        # checks if mine_controller is online
        for mc in mine_controllers:
            try:
                r = requests.get('http://{}:8080/heart_beat'.format(mc))
                if r.status_code == 200:
                    available_mine_controllers.append(mc)
            except Exception as e:
                logging.debug(repr(e))

        executor = ThreadPoolExecutor()
        futures = []
        if len(available_mine_controllers) > 0:
            #split the list of miners into proportional chunks based on available MC
            miner_chunks = list(chunkify(miners, len(available_mine_controllers)))
            for idx, mc in enumerate(available_mine_controllers):
                futures.append(executor.submit(post_command_to_agent,
                                                miner_chunks[idx],
                                                cmd_payload['cmd'],
                                                mc))

            wait(futures)
            logging.info('done!')

if __name__ == '__main__':

    with ThreadPoolExecutor(max_workers=5) as executor:
        while True:
            line = sys.stdin.readline()
            try:
                json_line = json.loads(line)
            except json.decoder.JSONDecodeError:
                continue

            executor.submit(main, json_line)
