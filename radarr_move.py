from moviefunc_radarr import arr_request
import threading
import time

def start_move(yaml_data: dict):
    # mock yaml data for now
    arr_request(f'/api/v3/movie/{yaml_data["id"]}?moveFiles=true', method="PUT", json=yaml_data)
    status = None
    while status != 'completed':
        commands = arr_request('/api/v3/command')
        command = next((cmd for cmd in commands if cmd['name'] == 'MoveMovie' and cmd['body']['destinationPath'] == yaml_data['path']), None)
        if command:
            status = command.get('status', 'unknown')
            result = command.get('result', 'unknown')
        time.sleep(5)
    if result != 'successful':
        raise Exception(f"Move failed with result: {result}")
    print("Move completed successfully.")

def move_movie(yaml_data: dict):
    """
    Threaded move operation with Timeout handling.
    """
    t = threading.Thread(target=start_move, args=(yaml_data,), daemon=True)
    t.start()
    t.join(timeout=600) # Wait for 10 minutes
    if t.is_alive():
        raise TimeoutError("Move operation is taking too long.")
    else:
        print("Move completed within the timeout period.")
