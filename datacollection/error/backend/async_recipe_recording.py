import logging
import asyncio
import os
import sys
import signal
import functools

from datacollection.error.backend.firebase_service import FirebaseDatabaseService

logging.basicConfig(filename='std.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.warning('This message will get logged on to a file')
logger=logging.getLogger()
logger.setLevel(logging.INFO)

def update_recipe_recording_interrupt_handler(db_service, recording_instance, signum, frame):
    logger.log(logging.INFO, "Received interrupt signal {}".format(signum))
    db_service.updateRecipeRecordingDetails(is_start=False, recording_instance=recording_instance)
    logger.log(logging.INFO, "Updated Recipe recording end time in Firebase Database")
    sys.exit(0)

# TODO : Can use this method for uploading the video to box folder
def update_recipe_uploading_interrupt_handler(db_service, recording_instance, signum, frame):
    pass


async def long_running_task(recording_instance):
    # Create a DB service attached to the new child process
    db_service = FirebaseDatabaseService()
    db_service.updateRecipeRecordingDetails(is_start=True, recording_instance=recording_instance)

    # Set the interrupt handler
    # Code that will be executed when signalled to stop
    signal.signal(signal.SIGINT, functools.partial(update_recipe_recording_interrupt_handler, db_service, recording_instance))

    # TODO: Add code related to Hololens for capturing frames and storing locally
    counter = 0
    logger.log(logging.INFO, "Starting Child process with PID {}".format(os.getpid()))
    while counter<100:
        logger.log(logging.INFO,"{}".format(counter))
        counter += 1
        await asyncio.sleep(1)

def run_async_task(recording_instance):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(long_running_task(recording_instance))

def create_async_subprocess(recording_instance):
    pid = os.fork()
    if pid == 0:
        # This is the child process
        child_subprocess_pid = os.getpid()
        print("Child process with PID - {}".format(child_subprocess_pid))

        run_async_task(recording_instance)
        return child_subprocess_pid
    else:
        # This is the parent process
        print("Parent process with PID", os.getpid())
        # Return the PID of the child process
        return pid

# if __name__ == '__main__':
#     process_id = create_async_subprocess()
#     print("Started new asynchronous subprocess with PID", process_id)
#     # Exit the parent process
#     sys.exit(0)

