import sublime, sublime_plugin
import select

from .ssh_threads import ActiveThreadsPool, PiggyThread

class RunCommandUtil:
	@classmethod
	def run_async_command(cls, script):
		window = sublime.active_window()
		window.run_command("show_panel", {"panel": "console", "toggle": False})
		pool = ActiveThreadsPool()

		if (pool.active_threads_count() > 0):
			cancel_job = sublime.ok_cancel_dialog('Another job is currently running, do you wish to cancel it?')

			if cancel_job:
				window.run_command("cancel_job")
			else:
				return

		hostname, username, password = RunCommandUtil.load_settings()

		thread = PiggyThread(script, hostname, username, password)
		thread.start()
		pool.add_thread(thread)

	@classmethod
	def load_settings(cls):
		settings = sublime.load_settings("piggy_ssh.sublime-settings")
		hostname = settings.get("hostname")
		username = settings.get("username")
		password = settings.get("password")

		return hostname, username, password


class CancelJobCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		window = sublime.active_window()
		window.run_command("show_panel", {"panel": "console", "toggle": False})
		pool = ActiveThreadsPool()
		pool.remove_thread()

class PiggySshSelectionCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		pig_script = ''
		sels = self.view.sel()
		for sel in sels:
			pig_script += self.view.substr(sel)

		RunCommandUtil.run_async_command(pig_script)

class PiggySshScriptCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		view_region = sublime.Region(0, self.view.size())
		pig_script = self.view.substr(view_region)
		RunCommandUtil.run_async_command(pig_script)
