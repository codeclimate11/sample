import socket
import sys
import curses
import random
import pickle
import threading
import time

client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
address = sys.argv[1]
port = int(sys.argv[2])
add = (address,port)
client.connect(add)

player = [{}]
positions = []

def initialize_pos(data):
	received = client.recv(1024)
	player=(pickle.loads(received))
	print("Received from server: ", player)
	for myset in player:
		positions.append((myset['x_pos= '], myset['y_pos= ']))
		food = myset['food= ']

	return food, player


def change_direction(new_head,key):

	if key == curses.KEY_UP:
		new_head[0] -= 1
	if key == curses.KEY_DOWN:
		new_head[0] += 1
	if key == curses.KEY_RIGHT:
		new_head[1] += 1
	if key == curses.KEY_LEFT:
		new_head[1] -= 1

	return new_head

def play_snake(x, y, food, my_id):

	score = 0

	snake = [[y_pos,x_pos],[y_pos,x_pos - 1],[y_pos,x_pos - 2]] 
	
	# y_pos2 = y_pos + 3
	# x_pos2 = x_pos - 2
	# snake2 = [[y_pos2,x_pos2],[y_pos2,x_pos2 - 1],[y_pos2,x_pos2 - 2]] 
	
	win.addch(food[0],food[1],curses.ACS_DIAMOND)
	key = win.getch()

	while key!=27:

		win.border(0)
		win.addstr(0, 2, 'Score: ' + str(score) + ' ')
		win.addstr(0, int(sw/2 - 10), ' MULTIPLAYER SNAKE ')

		prevKey = key                                                 
		event = win.getch()
		key = key if event == -1 else event 

		if key not in [curses.KEY_LEFT, curses.KEY_RIGHT, curses.KEY_UP, curses.KEY_DOWN, 27]:     #If an invalid key is pressed
			key = prevKey

		new_head = [snake[0][0], snake[0][1]]
		new_head = change_direction(new_head,key)

		snake.insert(0, new_head)

		if snake[0][0] in [0,sh] or snake[0][1] in [0,sw]:				#border conditions
			break
		
		if snake[0] == food:                                           #When snake eats the food
			food = []
			score += 1
			while food == []:
				food = [random.randint(1, sh - 1), random.randint(1, sw - 1)]          #Calculating new food
				if food in snake: food = []
			win.addch(food[0], food[1], curses.ACS_DIAMOND)
		else:
			last = snake.pop()

		picles = pickle.dumps([snake[0][0], snake[0][1], last[0], last[1], food[0], food[1]])
		client.send(picles)

		try:
			received = client.recv(1024)
			playersPos=(pickle.loads(received))

		except EOFError:
				pass


		try:
			for position in playersPos:
				win.addch(position[0], position[1], curses.ACS_CKBOARD)
				win.addch(position[2], position[3], ' ')
		except curses.error:
			pass


	curses.endwin()
	print("The End!")
	print("\nScore - " + str(score))


if __name__ == '__main__':

	food, r = initialize_pos("Hello snake")
	screen = curses.initscr()
	sh,sw = screen.getmaxyx()
	win = curses.newwin(sh, sw, 0, 0)
	win.timeout(100)
	win.keypad(1)
	curses.noecho()
	curses.curs_set(0)
	win.border(0)

	my_id2 = " "

	(x_pos, y_pos) = positions[0]
	my_id1 = r[0]['id= ']

	t1 = threading.Thread(target=play_snake, args=(x_pos,y_pos,food,my_id1))

	t1.start()

	if len(positions) > 1:
		(x_pos,y_pos) = positions[1]
		my_id2 = r[1]['id= ']
		t2 = threading.Thread(target=play_snake, args=(x_pos,y_pos,food,my_id2))
		time.sleep(0.005)
		t2.start()
			
