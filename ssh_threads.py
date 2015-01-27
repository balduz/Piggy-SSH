import paramiko, threading

class ActiveThreadsPool (object):
	instance = None
	threads = []

	def __new__(cls, *args, **kargs): 
		if cls.instance is None:
			cls.instance = object.__new__(cls, *args, **kargs)
		return cls.instance

	def active_threads_count(self):
		return len(self.threads)

	def add_thread(self, thread):
		self.threads.append(thread)

	def contains_thread(self, thread):
		return (thread in self.threads);

	def thread_finished(self, thread):
		self.threads.remove(thread)

	def remove_thread(self):
		threads_before_removal = threading.active_count()

		if (len(self.threads) == 0):
			print('WARN: No threads running in the current session.')
			return

		self.threads[0].stop_thread()
		if (threads_before_removal == threading.active_count()):
			self.threads.pop(0)
		else:
			print('ERROR: The job could not be cancelled.')

class PiggyThread(threading.Thread):
	def __init__(self, script, hostname, username, password):
		self.script = script
		self.hostname = hostname
		self.username = username
		self.password = password
		self.stopper = threading.Event()
		self.ssh_handler = None
		threading.Thread.__init__(self)

	def run(self):
		try:
			self.ssh_handler = SSHHandler(self.hostname, self.username, self.password, self.stopper)
			self.ssh_handler.connect()
			self.ssh_handler.run_cmd('echo $$; exec pig -e "' + self.script + '"')
		except Exception as e:
			print('ERROR: ' + str(e))
		finally:
			pool = ActiveThreadsPool()
			if pool.contains_thread(self):
				pool.thread_finished(self)

	def stop_thread(self):
		self.ssh_handler.cancel_command()

class SSHHandler(paramiko.SSHClient):
	def __init__(self, hostname, username, password, stopper):
		self.pid = None
		self.hostname = hostname
		self.username = username
		self.password = password
		self.stopper = stopper
		super(SSHHandler, self).__init__()

	def connect(self, timeout=None):
		self.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		paramiko.SSHClient.connect(self, self.hostname, username=self.username, password=self.password,
				allow_agent=False, look_for_keys=False, timeout=timeout)

	def run_cmd(self, cmd):
		try:
			transport = self.get_transport()
			# transport.set_keepalive(1)
			channel = transport.open_session()
			channel.exec_command(cmd)
			
			# PID
			self.pid = channel.recv(16).decode('utf-8')

			stderr_buffer = TextBuffer()
			stdout_buffer = TextBuffer()

			while not self.stopper.is_set() and not channel.exit_status_ready():
				if channel.recv_ready():
					next_stdout_message = channel.recv(128).decode('utf-8')
					stdout_buffer.append(next_stdout_message)

				if channel.recv_stderr_ready():
					next_stderr_message = channel.recv_stderr(128).decode('utf-8')
					stderr_buffer.append(next_stderr_message)		

				std_out_msg = stdout_buffer.read_lines()
				std_err_msg = stderr_buffer.read_lines()

				if (std_out_msg is not None and std_out_msg != ''):
					print(std_out_msg)
				if (std_err_msg is not None and std_err_msg != ''):
					print(std_err_msg)

			if not self.stopper.is_set():
				print('Script ended successfully!')
			else:
				print('Script cancelled!')

		except Exception as e:
			print('ERROR: ' + str(e))
		finally:
			self.close_session()

	def close_session(self):
		self.stopper.set()
		self.close()

	def cancel_command(self, timeout=None):
		aux_client = paramiko.SSHClient()
		aux_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		aux_client.connect(self.hostname, username=self.username, password=self.password,
				allow_agent=False, look_for_keys=False, timeout=timeout)

		aux_client.get_transport().open_session().exec_command('kill -SIGINT %s' % self.pid)

		aux_client.close()
		self.close_session()


# This class will be used as a buffer for the bytes received through the channel
class TextBuffer:
	def __init__(self):
		self.text = None

	def append(self, text):
		if self.text is None or self.text == '':
			self.text = text
		else:
			self.text += text

	def read_lines(self):
		if self.text is None:
			return
		pos_new_line = self.text.rfind('\n')
		if pos_new_line != -1:
			output = self.text[:pos_new_line]
			self.text = self.text[pos_new_line+1:]
			return output
		else:
			return None
