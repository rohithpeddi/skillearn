import logging
import asyncio
import os
import sys
import signal
import functools

from datacollection.error.backend.Recording import Recording
from datacollection.error.backend.firebase_service import FirebaseService
from datacollection.error.backend.hololens_service import HololensService

logging.basicConfig(filename='std.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
logging.warning('This message will get logged on to a file')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def update_recipe_recording_interrupt_handler(db_service, recording_instance, recording_service, signum, frame):
	logger.log(logging.INFO, "Received interrupt signal {}".format(signum))

	recording_service.stop_recording()
	logger.log(logging.INFO, "Stopped all threads related to recording")

	db_service.update_activity_recording_details(is_start=False, recording_instance=recording_instance)
	logger.log(logging.INFO, "Updated activity recording end time in Firebase Database")

	sys.exit(0)


async def long_running_task(recording_instance: Recording):
	# Create a DB service attached to the new child process
	db_service = FirebaseService()
	db_service.update_activity_recording_details(is_start=True, recording_instance=recording_instance)

	recording_service = HololensService()

	# Set the interrupt handler
	# Code that will be executed when signalled to stop
	signal.signal(signal.SIGINT,
				  functools.partial(update_recipe_recording_interrupt_handler, db_service, recording_instance, recording_service))

	# Starts necessary things for recording from hololens service
	recording_service.start_recording(recording_instance)


def create_async_subprocess(recording_instance):
	pid = os.fork()
	if pid == 0:
		# This is the child process
		child_subprocess_pid = os.getpid()
		print("Child process with PID - {}".format(child_subprocess_pid))

		loop = asyncio.new_event_loop()
		asyncio.set_event_loop(loop)
		loop.run_until_complete(long_running_task(recording_instance))

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
