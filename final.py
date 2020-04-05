import kivy
kivy.require('1.11.0')
from functools import partial

from kivy.app import App

from kivy.clock import Clock

from kivy.graphics import Line, Color, Rectangle

from kivy.properties import ListProperty

from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput

from random import randrange

BOARD_SIZE = 9
BLOCK_SIZE = int(BOARD_SIZE**0.5)
board = [
			[1,0,0,4,5,6,7,8,9],
			[1,0,3,4,5,6,7,8,9],
			[1,0,0,4,5,0,7,8,9],
			[1,2,3,4,5,6,7,8,9],
			[1,2,3,4,5,6,7,8,9],
			[1,2,3,4,5,6,7,8,9],
			[1,2,3,4,5,6,7,8,9],
			[1,2,3,4,5,6,7,8,9],
			[1,2,3,4,5,6,7,8,9]
		]

colorDict = {
				"red": (204/255, 139/255, 134/255, 1),
				"green": (102/255, 143/255, 128/255, 1),
				"blue": (42/255, 98/255, 143/255, 1),
				"yellow": (229/255, 224/255, 89/255)	}


class Board(GridLayout):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

class BoardLabel(Label):
	pass
class ButtonUI(Button):
	border_color = ListProperty()

class NumInput(TextInput):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def insert_text(self, substring, from_undo=False):
		if (self.text + substring).isdigit():
			if not int(self.text + substring) in range(1, BOARD_SIZE+1):
				substring = ""
		else:
			substring = ""
		TextInput.insert_text(self, substring, from_undo)


def cell_valid(index):
	BLOCK_SIZE = int(BOARD_SIZE**0.5)
	row, col = index//BOARD_SIZE, index%BOARD_SIZE
	cellNum = inputBoard[row][col]
	if inputBoard[row].count(cellNum) > 1 and cellNum > 0:
		return "Invalid1"
	for y in range(BOARD_SIZE):
		if inputBoard[y][col] == cellNum and cellNum > 0 and y != row:
			return "Invalid2"
	blockX, blockY = row//BLOCK_SIZE, col//BLOCK_SIZE

	for x in range(BLOCK_SIZE):
		for y in range(BLOCK_SIZE):
			currentBlock = inputBoard[blockX*BLOCK_SIZE+x][blockY*BLOCK_SIZE+y]
			if currentBlock == cellNum and cellNum > 0 and (blockX*BLOCK_SIZE+x, blockY*BLOCK_SIZE+y) != (row, col):
				return "Invalid3"
	return "Valid"

def cell_options (board, row, col):
	BLOCK_SIZE = int(BOARD_SIZE**0.5)
	num_list = [num for num in range(1,BOARD_SIZE+1)]
	if (row, col) in cells_filled:
		for elem in cells_filled[cells_filled.index((row, col))+1]:
			list_delete(num_list, elem)
	
	for i in range(BOARD_SIZE):
		list_delete(num_list, board[row][i])
		list_delete(num_list, board[i][col])

	blockX, blockY = row//BLOCK_SIZE, col//BLOCK_SIZE
	for x in range(BLOCK_SIZE):
		for y in range(BLOCK_SIZE):
			currentBlock = board[blockX*BLOCK_SIZE+x][blockY*BLOCK_SIZE+y]
			list_delete(num_list, currentBlock)
	return num_list

def check_board_validity(board, BOARD_SIZE: int):
	num_list = []
	BLOCK_SIZE = int(BOARD_SIZE**0.5)
	for row in board:
		for digit in row:
			if str(digit) not in "".join([str(number) for number in range(0,BOARD_SIZE+1)]):
				return "Not ValidR1"
			elif row.count(digit) > 1 and digit != 0:
				return "Not ValidR2"

	for index in range(BOARD_SIZE):	# Check the columns of the board
		num_list = []
		for row in board:
			num_list.append(row[index])
		for digit in num_list:
			if str(digit) not in "".join([str(number) for number in range(0,BOARD_SIZE+1)]):
				return "Not ValidC1"
			elif num_list.count(digit) > 1 and digit != 0:
				return "Not ValidC2"
	
	for row_index in range(0, BOARD_SIZE, BLOCK_SIZE):	# Check the individual block of the board
		for col_index in range(0, BOARD_SIZE, BLOCK_SIZE):
			num_list = []
			for row in range(BLOCK_SIZE):
				for col in range(BLOCK_SIZE):
					num_list.append(board[row_index+row][col_index+col])
			for digit in num_list:
				if str(digit) not in "".join([str(number) for number in range(0,BOARD_SIZE+1)]):
					return "Not ValidB1", 
				elif num_list.count(digit) > 1 and digit != 0:
					return "Not ValidB2"
	return "Valid"

def generate_board(game_type="Play"):
	global board
	boardArray = []
	boardFile = open(f"boards_{BOARD_SIZE}.txt", "r").read().split("\n")
	boardFile.pop(0)
	boardFile.remove('')
	boardCount = len(boardFile)//(BOARD_SIZE)
	for boards in range(boardCount):
		board = []
		for row in range(BOARD_SIZE):
			rowList = boardFile[boards*(BOARD_SIZE)+row].strip('[]').split(',')
			board.append([int(num) for num in rowList])
		boardArray.append(board[:])
	board = []
	if game_type == "Solve":
		board = [[0 for cell in range(BOARD_SIZE)] for row in range(BOARD_SIZE)]
	elif game_type == "Play":
		for elem in boardArray[randrange(1, boardCount)]:
			board.append(elem[:])

def isSolved():
	global screen_manager, inputBoard
	board_screen = final_app.root.ids.board_screen
	#print(board_screen.ids, board_screen.children)
	solvedLabel = final_app.root.ids.solvedLabel
	solvedLabel.text = "Not Solved"
	solvedLabel.color = (1, 0, 0, 1)
	inputBoard = []
	for row in range(BOARD_SIZE):
		inputBoard.append(list())
		for col in range(BOARD_SIZE):
			text = cellArray[row*BOARD_SIZE+col].text
			inputBoard[row].append(int(text) if text else 0)
	
	tilesLabel = final_app.root.ids.tilesLabel
	emptyCells = 0
	for row in inputBoard:
		emptyCells += row.count(0)
	tilesLabel.text = "Empty Cells: %d/%d" %(emptyCells, BOARD_SIZE**2)

	for row in inputBoard:
		if 0 in row:
			return False
	if check_board_validity(inputBoard, BOARD_SIZE) == "Valid":
		solvedLabel.text = "Solved"
		solvedLabel.color = (0, 0.85, 0, 1)
		return True
	else:
		return False

def list_delete(num_array, elem):
	try:
		num_array.remove(elem)
	except ValueError:
		pass

cells_filled = []
def solve(parent, dt=None):
	global index, cells_filled, board
#	print("Solving board...")
	index = 0
	cells_filled = []
	while index < BOARD_SIZE**2:
		if board[index//BOARD_SIZE][index%BOARD_SIZE] == 0:
			currentOptions = cell_options(board, index//BOARD_SIZE, index%BOARD_SIZE)
			if currentOptions != []:
				board[index//BOARD_SIZE][index%BOARD_SIZE] = currentOptions[0]
				cellArray[index].text = str(board[index//BOARD_SIZE][index%BOARD_SIZE])
				if (index//BOARD_SIZE, index%BOARD_SIZE) not in cells_filled:
					cells_filled.append((index//BOARD_SIZE, index%BOARD_SIZE))
					cells_filled.append([currentOptions[0]])
				else:
					cellIndex = cells_filled.index((index//BOARD_SIZE, index%BOARD_SIZE))
					cells_filled[cellIndex+1].append(currentOptions[0]) 
				index += 1
			else:
				if (index//BOARD_SIZE, index%BOARD_SIZE) in cells_filled:
					cells_filled.pop(-1)
					cells_filled.pop(-1)
				if not cells_filled == []:
					index = cells_filled[-2][0]*BOARD_SIZE + cells_filled[-2][1]
				else:
					print("Board not solvable")
					break
				board[index//BOARD_SIZE][index%BOARD_SIZE] = 0
				cellArray[index].text = str(board[index//BOARD_SIZE][index%BOARD_SIZE])
		else:
			index += 1
	print("Board solved")
	isSolved()

def validate(instance):
	global inputBoard
	
	instance.foreground_color = 0,0,0,1
	if instance.text == "":
		return
	if instance.text not in "".join([str(number) for number in range(1,BOARD_SIZE+1)]):
		#instance.text = ""
		instance.foreground_color = 1,0,0,1
	else:
		index = cellArray.index(instance)
		row, col = index//BOARD_SIZE, index%BOARD_SIZE
		inputBoard = []
		for row in range(BOARD_SIZE):
			inputBoard.append(list())
			for col in range(BOARD_SIZE):
				text = cellArray[row*BOARD_SIZE+col].text
				inputBoard[row].append(int(text) if text else 0)
#			print(board, inputBoard)
		if cell_valid(index) != "Valid":
			instance.foreground_color = 1,0,0,1
		isSolved()

def lostFocus(instance, value):
	if not value:
		isSolved()
		validate(instance)
	else:
		instance.foreground_color = 0,0,0,1

screen_manager = None
cellArray = []
inputBoard = []
remaining_time = -1

class Final(App):
	board_size = BOARD_SIZE
	def update_board(self, dt=None):
		global cellArray
		#print(board)
		#print("--------------", self.root.ids, final_app.root)
		for child in self.root.ids.board_screen.children:
			if isinstance(child, Board):
				self.root.ids.board_screen.remove_widget(child)
		boardLayout = Board()
		boardLayout.cols = BOARD_SIZE
		cellArray = []
		for row in range(BOARD_SIZE):
			for col in range(BOARD_SIZE):
				if board[row][col]:
					numButton = BoardLabel(text=str(board[row][col]) if board[row][col] else "")
				else:
					numButton = NumInput(text=str(board[row][col]) if board[row][col] else "")
					numButton.bind(on_text_validate = validate, focus = lostFocus)
					#numButton.padding_y =  #(blockSize-(400/BOARD_SIZE))/2
				boardLayout.add_widget(numButton)
				cellArray.append(numButton)
		self.root.ids.board_screen.add_widget(boardLayout)


	def build(self):
		global screen_manager
		screen_manager = ScreenManager()
		return screen_manager

	def load_game(self, game_type="Play"):
		global board
		global remaining_time
		generate_board(game_type)
		#print("____________", board)
		self.update_board()
		isSolved()
		Clock.schedule_once(partial(self.transition, "Board", "left"), 0.7)
		remaining_time = 5
		self.root.ids.timer_label.text= (" Time remaining: %2d:%02d" %(remaining_time//60, remaining_time%60))
		Clock.schedule_once(self.timerStart, 1.7)

	def on_start(self):
		pass

	def select_board_size(self, size, color):
		global BOARD_SIZE
		BOARD_SIZE = size
		self.board_size = BOARD_SIZE
		# for child in self.root.ids.main_screen.children:
		# 	if isinstance(child, ButtonUI):
		# 		child.border_color = colorDict[color]
		for child in self.root.ids.size_layout.children:
			if str(size) in child.text:
				child.disabled = True
			else:
				child.disabled = False

	def solve_board(self):
		global cellArray, board
		inputBoard = []
		for row in range(BOARD_SIZE):
			inputBoard.append([int(elem.text) if elem.text else 0 for elem in cellArray[row*BOARD_SIZE:(row+1)*BOARD_SIZE]])
		if check_board_validity(inputBoard, BOARD_SIZE) == "Valid":
			#self.children[5].disabled = True
			board = inputBoard.copy()
			solve(self)
			for row in range(BOARD_SIZE):
				for col in range(BOARD_SIZE):
					cellArray[row*BOARD_SIZE+col].text = str(board[row][col]) if board[row][col] else ""
		else:
			print("Invalid Board")		
#			print(check_board_validity(inputBoard, BOARD_SIZE))
	

	def timerStart(self, dt=None):
		global remaining_time
		remaining_time -= 1
		time_in_minutes = "%2d:%02d" %(remaining_time//60, remaining_time%60)
		timer_label = self.root.ids.timer_label
		timer_label.text= (" Time remaining: " + time_in_minutes)
		if remaining_time > 60:
			timer_label.color = (0, 0, 0, 1)
		else:
			timer_label.color = (1, 0, 0, 1)
		#print("Time remaining: " + time_in_minutes)
		if self.root.current == "Board":
			if remaining_time > 0:
				self.root.ids.solve_button.disabled = True
				Clock.schedule_once(self.timerStart, 1)
			else:
				self.root.ids.solve_button.disabled = False

	def transition(self, screen_name, direction, dt=None):
		screen_manager.transition.direction = direction
		self.root.current = screen_name

if __name__ == "__main__":
	final_app = Final()
	final_app.run()