#!/usr/bin/env python3
import os
import sys
import subprocess as sb
#import operator # operator.indexOf(a, b)
from pathlib import Path

first_run = True
debug =  True
loaded = False
usr = os.environ['USER']
notes_file = "notes.txt"
notes_path = "/home/" + usr + "/.notes/"
whole_path = notes_path + notes_file
sep = "---------------"
argc = len(sys.argv)
note_array = []
#f = None#open(whole_path, "a")	# the file object
opt_dict = {'l': 'List notes', 'a': 'Add a note', 'd': 'Delete a note', 'p': 'Purge notes', 'h': 'Show this help menu', 'e': 'Exit'}
# open the file for appending and reading
filemode = 'a+'

def main():
	def create_file():
		"""Creates and returns the file object for the program."""
		if not isfile():
			try:
				if debug or first_run:
					print("[i] Created path to file.")
				sb.run(['mkdir', '-p', notes_path])
			except IOError as e:
				print("[!!] I/O Error in creating filepath: " + str(e))
				del e
			except Exception as e:
				print("[!!] Error in creating filepath: " + str(e))
				del e
			finally:
				try:
					# Open the file.
					f = open(whole_path, filemode)
					return f
				except Exception as e:
					print("[!!] Error in opening file: " + str(e))
					del e
					return None
		else:
			if debug:
				print("[i] File exists.")
			f = open(whole_path, filemode)
			return f
	def list_notes(f):
		"""Prints the notes to the screen."""
		if not isfile():
			print("[!!] File error in list_notes()")
		else:
			if len(note_array) == 0:
				print("[*] There are no notes to show.")
				return
			count = 0
			for n in note_array:
				print("{} -- {}".format(count, n.to_string()))
				count += 1
	def load_notes(f):
		"""Loads the notes from file into the array."""
		out = []
		if not isfile():
			print("[!!] File error in load_notes()")
			return None
		try:
			f.seek(0)
			line = f.readlines()
			line = [x.strip() for x in line]
			for l in line:
				name = l.split(":")[0]
				desc = l.split(":")[1]
				note_array.append(Note(name, desc))
		except IOError as e:
			print("[!!] I/O Error loading notes: " + str(e))
			del e
		except Exception as e:
			print("[!!] Error loading notes: " + str(e))
			del e
		finally:
			global loaded
			loaded = True
	def add_note(f):
		"""Adds a note to the array and appends it to the notes.txt file."""
		if not isfile():
			print("[!!] File error while adding a note")
		else:
			if not loaded:
				load_notes(f);
			in_content = input("Enter the new note:\n")
			if not in_content:
				print("[i] No content given, no note created.")
				return
			print()
			in_title = input("Enter the title of the note: ")
			addition = Note(in_title, in_content)
			print(addition.to_string(), file=f)
			note_array.append(addition)
			print()
	def purge_notes(f, quiet):
		"""Purges all notes.
		f: the file object
		quiet: whether or not to print confirmation dialogues."""
		answer = ""
		global note_array
		if not quiet:
			if len(note_array) == 0:
				print("[*] There are no notes to purge. Delete anyway? (y/N)")
			else:
				print("[*] Are you sure you want to purge your notes? This cannot be undone. (y/N)")
			answer = input("> ")
		else:
			answer = "yes"
		if answer == "y" or answer == "ye" or answer == "yes":
			print()
			if not isfile() and not quiet:
				print("[!!] File error in purgeNotes")
			else:
				note_array = []
				try:
					rm_cmd = ["rm", '-rf', whole_path]
					rm_bak = ["rm", '-rf', notes_path + "." + notes_file + ".bak"]
					sb.run(rm_cmd)
					if not quiet:
						sb.run(rm_bak)
					loaded = False
					load_notes(f)
					return
				except Exception as e:
					print("[!!] General error in purge_notes: " + str(e))
					del e
		else:
			print()
			return
	def delete_note(f):
		"""Deletes a note from the array and file.
		f: the file object"""
		if len(note_array) == 0:
			print("[*] There are no notes to delete.")
			return
		if not isfile():
			print("[!!] File error in delete_note")
		else:
			if not loaded:
				load_notes(f)
			for n in note_array:
				print("%d -- %s:%s" % (note_array.index(n), n.get_title(), n.get_content()))
			try:
				choice = int(input("Which to delete? (-1 for none)\n> "))
				if choice == -1:
					return
				deletion = note_array[choice]
				lookup = deletion.get_title() + ":" + deletion.get_content()
				print("\nRemove note:\n>> %s <<\nat index: %d" % (deletion.to_string(), note_array.index(deletion)))
				# TODO: Add a confirmation dialogue
				try:
					str_in = None
					line = f.readlines()
					content = [x.strip() for x in line]
					for l in content:
						if l is lookup:
							del l
					if len(note_array) == 0:
						purge_notes(True)
					# Creates and stores a backup of the current notes before deleting
					sb.run(['cp', whole_path, whole_path + '.bak'])
					i = 0
					for n in note_array:
						if i == 0:
							# The first iteration should not append the file, thus wiping it.
							print_to_file(f, True, n)
							# In this case, the bool is True because that means the file is cleared.
						else:
							# The subsequent iterations SHOULD append, adding data to the file.
							print_to_file(f, False, n)
							# The bool is False here in order to not wipe the whole file.
						i += 1
				except IOError as e:
					print("[!!] I/O Error deleting note: " + str(e))
					return
				except Exception as e:
					print("[!!] Error deleting note: " + str(e))
					return
				finally:
					# in Java, the input stream was closed.
					pass
			except:
				print("[!!] Invalid answer.")
				return
	def print_to_file(f, clear, note_in):
		"""Prints the information to the notes.txt file.
		f: the file object
		clear: whether or not to clear the file
		note_in: the Note to add"""
		if not isfile():
			print("[!!] File error in printing to file")
			return
		try:
			if clear:
				f.close()
				f = open(whole_path, 'w').close()
				f = open(whole_path, filemode)
			f.write(note_in.to_string() + "\n")
		except Exception as e:
			print("[!!] General error in printing to file: " + str(e))
		finally:
			# In Java, the output stream was closed.
			pass
	def cleanup(f):
		"""Closes the file.
		f: the file object"""
		if isfile():
			try:
				f.close()
			except IOError as e:
				print("[!!] I/O Error in cleanup: " + str(e))
				del e
			except Exception as e:
				print("[!!] Error in cleanup: " + str(e))
				del e
		else:
			print("[!!] No file to close")
	# The file object used for the program
	f = create_file()
	load_notes(f)
	# TODO: Replace this with argparse
	if argc > 1:
		if sys.argv[1].lower() == "-l":
			list_notes(f)
		elif sys.argv[1].lower() == "-a":
			add_note(f)
		elif sys.argv[1].lower() == "-d":
			delete_note(f)
		elif sys.argv[1].lower() == "-p":
			purge_notes(f, 1)
		elif sys.argv[1].lower() == "-h":
			list_help(0)
		else:
			print("[!!] Invalid answer.")
			list_help(1)
		cleanup(f)
		return
	else:
		first_run = False
		while 1:
			choice = int(list_menu())
			print()	# add a space between the selection and the text
			if choice == 1:
				list_notes(f)
			elif choice == 2:
				add_note(f)
			elif choice == 3:
				delete_note(f)
			elif choice == 4:
				purge_notes(f, 0)
			elif choice == 0:
				cleanup(f)
				print("[*] Goodbye!")
				break
			else:
				print("[!!] Invalid answer.")
			print()	# add a space between last selection and the new one

def list_help(usage):
	"""Lists the help menu for command-line purposes.
	usage: if True, print 'usage', if False, print 'Help'"""
	msg = "Usage" if usage else "Help"
	print()
	print(msg +
	""":
	  -a\t{;
	  -l\t{}
	  -d\t{}
	  -p\t{}
	  -h\t{}\n""".format(opt_dict['a'], opt_dict['l'], opt_dict['d'], opt_dict['p'], opt_dict['h']))

def list_menu():
	"""Lists the menu for interactive purposes."""
	answer = -1
	print("""Menu:
	1.\t{}
	2.\t{}
	3.\t{}
	4.\t{}
	0.\t{}""".format(opt_dict['l'], opt_dict['a'], opt_dict['d'], opt_dict['p'], opt_dict['e']))
	while not answer >= 0 and answer <= 4:
		answer = input("> ")
		if int(answer) >= 0 and int(answer) <= 4:
			return answer
		else:
			print("[!!] Invalid response.")
			answer = -1

def isfile():
	"""Return whether or not the file (f) exists on the system."""
	fpath = Path(whole_path)
	return fpath.is_file()

class Note:
	def __init__(self, title="(untitled)", content=""):
		self.set_title(title)
		self.set_content(content)

	def get_title(self):
		return self.__name

	def set_title(self, title):
		if not title:
			self.__name = "(untitled)"
		else:
			self.__name = str(title)

	def get_content(self):
		return self.__desc

	def set_content(self, content):
		self.__desc = content

	def to_string(self):
		return self.get_title() + ":" + self.get_content()

# Enter the program.
main()
