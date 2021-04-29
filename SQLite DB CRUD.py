import sqlite3
from tkinter import *
from tkinter import filedialog

#Close connection with a DB. Clear lists and destroy frames.
def closeConnection():
	try:
		connection.close()
		tables.clear()
		columns.clear()
		columnsType.clear()
		frameTables.destroy()
		frameColumns.destroy()
		frameCRUD.destroy()
	except:
		pass

#Get the primary key of a table
def getPrimaryKey(importedColumns):
	for c in importedColumns:
		if(c[5] == 1):
			return c[1]

#Open a table of an imported DB
def openTable(t):
	#Clear lists to avoid wrong mapping
	col.clear()
	columnsType.clear()
	for widgets in frameColumns.winfo_children():
		widgets.destroy()
	#Variables that could be useful in the future
	global actualTable
	global keys

	actualTable = t
	#Query to get table information
	cursor.execute("PRAGMA table_info('" + t + "');")
	importedColumns = cursor.fetchall()
	print(importedColumns)

	pk = getPrimaryKey(importedColumns)
	print(pk)
	#Save table information
	for c in importedColumns:
		#col[c[1]] = ""
		columns.append(c[1])
		columnsType.append(c[2])
	
	print(columns)
	#keys = col.keys()
	i = 0
	#Print table info
	for k in columns:
		if(k == pk):
			l = Label(frameColumns, text = k + "(PK):")
		else:
			l = Label(frameColumns, text = k + ":")
		l1 = Label(frameColumns, text = columnsType[i])
		text = Entry(frameColumns)
		l.grid(row = i, column = 0, sticky = "e")
		l1.grid(row = i, column = 2, sticky = "w")
		text.grid(row = i, column = 1)
		i = i +1

#Import a Database
def importDB():
	
	global connection
	global cursor
	global frameTables
	global frameColumns
	global frameCRUD

	dbFile = filedialog.askopenfilename(title = "Open")
	print (dbFile)
	#Just in case
	closeConnection()
	#Connect with a DB
	connection = sqlite3.connect(dbFile)
	cursor = connection.cursor()
	#Frames for tables, colums and CRUD buttons
	frameTables = Frame(root, width = 100, height = 100)
	frameTables.grid(row = 0, column = 0)
	frameColumns = Frame(root, width = 100, height = 100)
	frameColumns.grid(row = 0, column = 1)
	frameCRUD = Frame(root, width = 100, height = 100)
	frameCRUD.grid(row = 1, column = 1)
	#Query to get all tables from a DB
	cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
	importedTables = cursor.fetchall()
	#Save query result
	for t in importedTables:
		tables.append(t[0])

	print(tables)
	#Print all tables
	for i in range(len(tables)):
		b = Button(frameTables, text = tables[i], command = lambda i=i: openTable(tables[i]))
		b.grid(row = i, column = 0, sticky = "w")

	create = Button(frameCRUD, text = "Create")	#To do
	create.grid(row = 0, column = 1)
	read = Button(frameCRUD, text = "Read All", command = lambda: readAll())
	read.grid(row = 0, column = 2)
	update = Button(frameCRUD, text = "Update")	#To do
	update.grid(row = 0, column = 3)
	delete = Button(frameCRUD, text = "Delete")	#To do
	delete.grid(row = 0, column = 4)

#Query to print all data of a table
def readAll():
	cursor.execute("SELECT * FROM " + actualTable)
	result = cursor.fetchall()
	#Print result on a new window
	window = Toplevel(root)
	window.title("Result")
	window.geometry("500x500")

	scrollbar = Scrollbar(window)
	scrollbar.pack(side = RIGHT, fill = Y)
	listbox = Listbox(window, width = 500, height = 500, yscrollcommand = scrollbar.set)
	listbox.pack(side = LEFT, fill = BOTH)
	scrollbar.config(command=listbox.yview)
	print(result)
	#List all result
	i = 0
	for r in result:
		listbox.insert(END, str(result[i]))
		i = i + 1		

#Gui
root = Tk()
root.title("SQLite DB CRUD")
#Create a toolbar
toolbar = Menu(root)
root.config(menu = toolbar)
#File menu for toolbar
file = Menu(toolbar, tearoff=0)
toolbar.add_cascade(label = "File", menu = file)

tables = []
columns = []
columnsType = []
col = {}
#File menu options
file.add_command(label = "Import Data Base", command = importDB)
file.add_command(label = "Close Data Base", command = closeConnection)
file.add_command(label = "Exit", command = root.destroy)

root.mainloop()