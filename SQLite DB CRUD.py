import sqlite3
import re
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from pandastable import Table, TableModel
import pandas as pd

#Close connection with a DB. Clear lists and destroy frames.
def closeConnection():
	try:
		connection.close()
		tables.clear()
		columns.clear()
		columnsType.clear()
		frameTables.destroy()
		frameButtons.destroy()
		frameConsole.destroy()
		frameResults.destroy()
		frameExecute.destroy()
	except:
		pass

#Get the primary key of a table
def getPrimaryKey(importedColumns):
	for c in importedColumns:
		if(c[5] == 1):
			return c[1]

#Open a table of an imported DB
def getTable(t):
	#Clear lists to avoid wrong mapping
	columns.clear()
	columnsType.clear()

	global actualTable

	actualTable = t
	#Query to get table information
	cursor.execute("PRAGMA table_info('" + t + "');")
	importedColumns = cursor.fetchall()

	pk = getPrimaryKey(importedColumns)
	#Save table information
	for c in importedColumns:
		columns.append(c[1])
		columnsType.append(c[2])
	
	i = 0
	#Print table info
	for k in columns:
		if(k == pk):
			l = Label(frameColumns, text = k + "(PK):")
		else:
			l = Label(frameColumns, text = k + ":")
		l1 = Label(frameColumns, text = columnsType[i])
		l.grid(row = i, column = 0, sticky = "e")
		l1.grid(row = i, column = 2, sticky = "w")
		i = i +1

#Import a Database
def importDB():
	global connection
	global cursor

	#Just in case
	closeConnection()
	dbFile = filedialog.askopenfilename(title = "Open")
	print (dbFile)

	#Connect with a DB
	connection = sqlite3.connect(dbFile)
	cursor = connection.cursor()
	init()


def newDB():
	global connection
	global cursor

	#Just in case
	closeConnection()
	connection = sqlite3.connect("DefaultDB")
	cursor = connection.cursor()
	init()
	
#Initialize GUI
def init ():
	global frameTables
	global frameExecute
	global frameConsole
	global frameButtons
	global frameResults
	global frameColumns
	frameTables = Frame(root, width = 100, height = 100)
	frameTables.grid(row = 0, column = 0)
	frameExecute = Frame(root, width = 100, height = 100)
	frameExecute.grid(row = 0, column = 1)
	frameConsole = Frame(frameExecute, width = 300, height = 100)
	frameConsole.grid(row = 1, column = 0)
	frameButtons = Frame(frameExecute, width = 100, height = 100)
	frameButtons.grid(row = 1, column = 1)
	frameResults = Frame(root, width = 500, height = 500)
	frameResults.grid(row = 0, column = 3)
	frameColumns = Frame(frameExecute)
	frameColumns.grid(row = 0, column = 0)
	console = Text(frameConsole, width = 70, height = 10)
	console.grid(row = 0, column = 0)
	execute = Button(frameButtons, text = "Execute", command = lambda: executeQuery(console.get("1.0", END)))
	execute.grid(row = 0, column = 0)
	read = Button(frameButtons, text = "Read All", command = lambda: readAll())
	read.grid(row = 1, column = 0)
	refresh = Button(frameButtons, text = "Refresh Tables", command = lambda: refreshTables(cursor))
	refresh.grid(row = 2, column = 0, sticky = "w")
	refreshTables(cursor)

def executeQuery(query):
	global actualTable
	#Get actual from query
	for t in tables:
		if t in query:
			getTable(t)
	#Clear actualTable variable in case a "DROP TABLE" query is executed while that table is "open"
	if ("drop table " + actualTable).lower() in query.lower():
		actualTable = " "
	#In case is a "SELECT" query
	elif "select " in query[0:7].lower():
		selectColumns = []

		if "*" in query:
			selectColumns = columns

		else:
			m = re.search('select(.*) from ', query.lower())
			subString = m.group(0)
			for c in columns:
				if c.lower() in subString:
					selectColumns.append(c)

		cursor.execute(query)
		result = cursor.fetchall()
		width = len(selectColumns)
		#Print result on a new window
		if len(result)==0:
			#Print table content
			for c in selectColumns:
				result.append("")
			results = []
			results.append(tuple(result))
			df = pd.DataFrame(results, columns = selectColumns)
			pt = Table(frameResults, dataframe = df, width = 500, height = 500, cols = width)
			pt.grid(row = 0, column = 0, sticky = "nsew")
			pt.show()
		else:
			height = len(result)
			#Print table content
			df = pd.DataFrame(result, columns = selectColumns)
			pt = Table(frameResults, dataframe = df, width = 500, height = 500, cols = width, rows = height)
			pt.grid(row = 0, column = 0, sticky = "nsew")
			pt.show()
	else:
		cursor.execute(query)
	connection.commit()

#Query to print all data of a table
def readAll():
	global pt
	global actualTable
	if actualTable == " ":
		messagebox.showinfo(title = "Warning", message = "Please, select a table.")
	else:
		executeQuery("SELECT * FROM " + actualTable)
		

def refreshTables(cursor):
	for widgets in frameTables.winfo_children():
		widgets.destroy()
	for widgets in frameResults.winfo_children():
		widgets.destroy()
	for widgets in frameColumns.winfo_children():
		widgets.destroy()
	#Query to get all tables from a DB
	cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
	importedTables = cursor.fetchall()
	#Save query result
	for t in importedTables:
		tables.append(t[0])
		b = Button(frameTables, text = t, command = lambda i = importedTables.index(t): getTable(tables[i]))
		b.grid(row = importedTables.index(t), column = 0, sticky = "w")	

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
actualTable = " "

#File menu options
file.add_command(label = "New Data Base", command = newDB)
file.add_command(label = "Import Data Base", command = importDB)
file.add_command(label = "Close Data Base", command = closeConnection)
file.add_command(label = "Exit", command = root.destroy)

root.mainloop()