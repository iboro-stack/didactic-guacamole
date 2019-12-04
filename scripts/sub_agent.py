from flask import Flask, request as flask_request
import logging
import json
import time
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("werkzeug").setLevel(logging.WARNING)
app = Flask(__name__)


class MineControlAgent():

    def __init__(self, list_of_supports, leases, mine_controller, data_center):
        '''
        @logger python logger object
        @list_of_supports list of T1/S9 supports for the miners, note the
        supports are initialized at this point.
        @leases this is the dnsmasque info converted in dictionary format.
        @datacenter current datacenter
        @minecontroller current mine controller
        '''

    def execute_command(self, miners, command):
        msg = 'executing {command} for {miners}'.format(
                                                    command=command,
                                                    miners=len(miners))
        try:
            logging.debug(msg)
            time.sleep(5)
            return json.dumps({'status': 'done {} {} miners'.format(command, len(miners))}), 200
        except:
            return json.dumps({'status': 'error!'}), 500


@app.route('/process_command', methods=['POST'])
def process_command():
    agent = MineControlAgent([], [], 'mine-yl1_1', 'mine-ycl1_1')
    command = flask_request.args.get('command')
    json_rst = flask_request.get_json()
    miners = json_rst['miners']
    return agent.execute_command(miners=miners, command=command)


@app.route('/heart_beat')
def heart_beat():
    return json.dumps({'success': True}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
