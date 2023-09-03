import customtkinter
import datetime
import math

class SmallClock:
	def __init__(self, center_point: tuple[int, int], hand_length: int) -> None:
		self.center_point = center_point
		self.hands_points = [center_point, center_point]
		self.hands_angles = [1, 1]
		self.hand_length = hand_length
		self._STEP = 1

		'''
		e = 0 / 360
		s = 90 / -270
		w = 180 / -180
		n = 270 / -90
		'''
		self.des_angles = [120, 350]

	def _tick(self, is_hand_2: bool, is_clock_wise: bool):
		'''
		each clock has 2 hands, is_hand_2 is used to select which hand
		to move, is_clock_wise is to select the direction of the rotation
		'''

		# update hand's angle
		self.hands_angles[int(is_hand_2)] = self.hands_angles[int(is_hand_2)] + self._STEP if is_clock_wise \
																				else self.hands_angles[int(is_hand_2)] - self._STEP
		
		# check bound
		if self.hands_angles[int(is_hand_2)] >= 360:
			self.hands_angles[int(is_hand_2)] = self.hands_angles[int(is_hand_2)] - 360
		elif self.hands_angles[int(is_hand_2)] < 0:
			self.hands_angles[int(is_hand_2)] = 360 + self.hands_angles[int(is_hand_2)]

		# update hand position
		x = self.center_point[0] + round(math.cos(math.radians(self.hands_angles[int(is_hand_2)])), 4)*self.hand_length
		y = self.center_point[1] + round(math.sin(math.radians(self.hands_angles[int(is_hand_2)])), 4)*self.hand_length
		self.hands_points[int(is_hand_2)] = (x, y)

	def set_des_angles(self, des_angles):
		self.des_angles = list(des_angles)

	def update(self):
		clock_wise = True
		if self.hands_angles[0] != self.des_angles[0]:
			self._tick(False, clock_wise)

		if self.hands_angles[1] != self.des_angles[1]:
			self._tick(True, clock_wise)

class Digit:
	def __init__(self, first_pos: tuple[int, int], radius: int, padding: int):

		# matrix
		self.matrix = [
			[
				[90, 0], [180, 90],
				[270, 90], [270, 90],
				[0, 270], [270, 180]
			],
			[
				[45, 45], [90, 90],
				[45, 45], [270, 90],
				[45, 45], [270, 270]
			],
			[
				[0, 0], [180, 90],
				[90, 0], [270, 180],
				[0, 270], [180, 180]
			],
			[
				[0, 0], [180, 90],
				[0, 0], [270, 180],
				[0, 0], [270, 180]
			],
			[
				[90, 90], [90, 90],
				[0, 270], [270, 90],
				[45, 45], [270, 270]
			],
			[
				[90, 0], [180, 180],
				[0, 270], [180, 90],
				[0, 0], [270, 180]
			],
			[
				[90, 0], [180, 180],
				[270, 90], [180, 90],
				[0, 270], [270, 180]
			],
			[
				[0, 0], [180, 90],
				[45, 45], [270, 90],
				[45, 45], [270, 270]
			],
			[
				[90, 0], [180, 90],
				[0, 270], [270, 180],
				[0, 270], [270, 180]
			],
			[
				[90, 0], [180, 90],
				[0, 270], [270, 180],
				[45, 45], [270, 180]
			]
		]
		self.clocks: list[SmallClock] = self._add_digit(first_pos=first_pos, padding=padding, hand_length=radius)

	def set_matrix(self, number: int):
		'''
		number is a single digit integer from 1 to 9
		'''
		if number < 0 or number > 9:
			return

		matrix = self.matrix[number]
		for idx, clock in enumerate(self.clocks):
			clock.set_des_angles(matrix[idx])

	def _add_digit(self, first_pos: tuple[int, int], padding: int, hand_length: int) -> list[SmallClock]:
		'''
		first_pos is the center coordinate of the first upper left clock,
		each digit is a combination of 6 small clocks arrange in a 2x3.
		return a list of @SmallClock objects
		'''
		padding = padding
		hand_length = hand_length
		digit_block: list[SmallClock] = []
		for i in range(3):
			# row = []
			for j in range(2):
				x = first_pos[0] + (hand_length*2+padding)*j
				y = first_pos[1] + (hand_length*2+padding)*i
				digit_block.append(SmallClock((x, y), hand_length))
			# digit_block.append(row)
		
		return digit_block

	def update(self):
		for clock in self.clocks:
			clock.update()

class App(customtkinter.CTk):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)

		self.canvas = customtkinter.CTkCanvas(self, width=800, height=400)
		self.canvas.grid(row=0, column=0, sticky="news")

		_first_pos = (100, 100)
		_radius = 30
		_padding = 5
		self.digits: list[Digit] = []
		for i in range(0, 8, 2):
			self.digits.append(Digit(first_pos=(_first_pos[0] + (_radius*2+_padding)*i, _first_pos[1]), 
									 radius=_radius,
									 padding=_padding))
		
		self.clock_ids = []
		for digit in self.digits:
			for clock in digit.clocks:
				center_point = clock.center_point
				hands_points = clock.hands_points
				self.clock_ids.append([
					self.canvas.create_line(center_point[0], center_point[1], hands_points[0][0], hands_points[0][1], width=3),
					self.canvas.create_line(center_point[0], center_point[1], hands_points[1][0], hands_points[1][1], width=3),
				])
				# self.canvas.create_oval(center_point[0]-30, center_point[1]-30, center_point[0]+30, center_point[1]+30)

		# set current time
		_data_time = datetime.datetime.now()
		self._time = _data_time.hour*60 + _data_time.minute
		_hour = int(self._time / 60) # 0 -> 24
		_minute = self._time % 60 # 0 -> 59

		self.digits[0].set_matrix(0 if _hour / 10 < 1 else int(_hour/10))
		self.digits[1].set_matrix(_hour if _hour / 10 < 1 else _hour%10)
		self.digits[2].set_matrix(0 if _minute / 10 < 1 else int(_minute/10))
		self.digits[3].set_matrix(_minute if _minute / 10 < 1 else _minute%10)
		
		# sync current time with computer time
		self.canvas.after(round(60 - _data_time.second, 3)*1000, self.update)
		# draw
		self.canvas.after(1, self.draw)

	def update(self):
		'''
		update current time very minute
		'''
		self._update_clock()
		# update every 60 minute
		self.canvas.after(60 * 1000, self.update)

	def _update_clock(self):
		'''
		update current time
		'''
		self._time += 1
		_hour = int(self._time / 60) # 0 -> 24
		_minute = self._time % 60 # 0 -> 59

		if _hour >= 24: 
			# new day hooray
			self._time = 0

		# update hour
		self.digits[0].set_matrix(0 if _hour / 10 < 1 else int(_hour/10))
		self.digits[1].set_matrix(_hour if _hour / 10 < 1 else _hour%10)
		self.digits[2].set_matrix(0 if _minute / 10 < 1 else int(_minute/10))
		self.digits[3].set_matrix(_minute if _minute / 10 < 1 else _minute%10)

	def draw(self):
		for digit in self.digits:
			digit.update()

		for i, digit in enumerate(self.digits):
			for j, clock in enumerate(digit.clocks):
				center_point = clock.center_point
				hands_points = clock.hands_points
				self.canvas.coords(self.clock_ids[j + i*6][0], center_point[0], center_point[1], hands_points[0][0], hands_points[0][1])
				self.canvas.coords(self.clock_ids[j + i*6][1], center_point[0], center_point[1], hands_points[1][0], hands_points[1][1])

		self.canvas.after(10, self.draw)

app = App()
app.mainloop()