import math

import game.game
import game.gameobject
import game.signal

import game.fnf.timingpoint

from typing import Self

class Conductor(game.gameobject.GameObject):
	current: Self = None

	step_hit = game.signal.Signal()
	beat_hit = game.signal.Signal()
	measure_hit = game.signal.Signal()

	def __init__(self):
		super().__init__(0, 0)

		self.offset: float = 0.0
		self._rate: float = 1.0

		self.auto_increment: bool = True
		self.has_metronome: bool = False

		## The raw time, usually set EXACTLY to the music time.
		## [br]
		## Use [code]visual_time[/code] for a smoother representation
		## of this value.
		self.raw_time: float = 0.0

		## This is similar to [code]time[/code], except smoothed out
		## for better use for visual objects like notes.
		self.visual_time: float = 0.0

		## Used ONLY for positioning notes.
		## [br]
		## [br]
		## For the most part, this matches what [code]visual_time[/code] represents,
		## however, this can be modified with scripts for cool note effects.
		self.playhead: float = 0.0

		self.cur_dec_step: float = 0.0
		self.cur_dec_beat: float = 0.0
		self.cur_dec_measure: float = 0.0

		self.cur_step: int = 0
		self.cur_beat: int = 0
		self.cur_measure: int = 0

		self.timing_points: list[game.fnf.timingpoint.TimingPoint] = [game.fnf.timingpoint.TimingPoint()]
		self._latest_timing_point: game.fnf.timingpoint.TimingPoint

	@staticmethod
	def seconds_to_ms(secs: float) -> float:
		return secs * 1000.0
		
	@staticmethod
	def ms_to_seconds(secs: float) -> float:
		return secs / 1000.0

	@staticmethod
	def get_numerator(time_signature: list[int]) -> int:
		return time_signature[0]

	@staticmethod
	def get_denominator(time_signature: list[int]) -> int:
		return time_signature[1]
	
	def get_bpm(self):
		return self._latest_timing_point.bpm
	
	def get_step_length(self):
		return self._latest_timing_point.get_step_length()

	def get_beat_length(self):
		return self._latest_timing_point.get_beat_length()

	def get_measure_length(self):
		return self._latest_timing_point.get_measure_length()
	
	def get_rate(self):
		return self._rate
	
	def set_rate(self, value: float):
		rate = value
	
	## Similar to [code]raw_time[/code], but with [code]offset[/code] applied to it.
	def get_time(self):
		return self.raw_time - self.offset
	
	def set_time(self, value: float):
		self.raw_time = value

	def reset(self, bpm: float = 100.0, time_signature: list[int] = [4, 4]):
		timing_points = [
			game.fnf.timingpoint.TimingPoint.from_dict({
				"time": 0.0,
				
				"step": 0.0,
				"beat": 0.0,
				"measure": 0.0,
				
				"bpm": bpm,
				"time_signature": time_signature,
			})
		]
		self._latest_timing_point = timing_points[0]
		
		self.cur_dec_step = -1.0
		self.cur_dec_beat = -1.0
		self.cur_dec_measure = -1.0
		
		self.cur_step = -1
		self.cur_beat = -1
		self.cur_measure = -1
		
		self.time = 0.0
		self.visual_time = 0.0
		self.playhead = 0.0

	def setup_timing_points(self, new_timing_points: list[game.fnf.timingpoint.TimingPoint]):
		time_offset: float = 0.0
		step_offset: float = 0.0
		beat_offset: float = 0.0
		measure_offset: float = 0.0
		
		last_top_number: int = self.get_numerator(new_timing_points[0].time_signature)
		last_bottom_number: int = self.get_denominator(new_timing_points[0].time_signature)
		
		last_bpm: float = new_timing_points[0].bpm
		new_timing_points.sort(reverse=False, key=lambda x: x.time)
		
		self.timing_points.clear()
		for i in range(1, len(new_timing_points)):
			point: game.fnf.timingpoint.TimingPoint = new_timing_points[i]
			beat_diff: float = (point.time - time_offset) / ((60.0 / last_bpm) * 1000.0)
			
			step_offset += beat_diff * last_bottom_number
			beat_offset += beat_diff
			measure_offset += beat_diff / last_top_number
			
			self.timing_points.append(game.fnf.timingpoint.TimingPoint.from_dict({
				"time": point.time,
				
				"step": step_offset,
				"beat": beat_offset,
				"measure": measure_offset,
				
				"bpm": point.bpm,
				"time_signature": point.time_signature
			}))
			time_offset = point.time
		
		self._latest_timing_point = self.timing_points[0]

	def get_timing_point_at_time(self, time: float) -> game.fnf.timingpoint.TimingPoint:
		output: game.fnf.timingpoint.TimingPoint = self.timing_points[0]
		for i in range(1, len(self.timing_points)):
			point:game.fnf.timingpoint.TimingPoint = self.timing_points[i]
			if time < point.time: break
			output = point
		return output

	def get_timing_point_at_step(self, step: float) -> game.fnf.timingpoint.TimingPoint:
		output: game.fnf.timingpoint.TimingPoint = self.timing_points[0]
		for i in range(1, len(self.timing_points)):
			point:game.fnf.timingpoint.TimingPoint = self.timing_points[i]
			if step < point.step: break
			output = point
		return output

	def get_timing_point_at_beat(self, beat: float) -> game.fnf.timingpoint.TimingPoint:
		output: game.fnf.timingpoint.TimingPoint = self.timing_points[0]
		for i in range(1, len(self.timing_points)):
			point:game.fnf.timingpoint.TimingPoint = self.timing_points[i]
			if beat < point.beat: break
			output = point
		return output

	def get_timing_point_at_measure(self, measure: float) -> game.fnf.timingpoint.TimingPoint:
		output: game.fnf.timingpoint.TimingPoint = self.timing_points[0]
		for i in range(1, len(self.timing_points)):
			point:game.fnf.timingpoint.TimingPoint = self.timing_points[i]
			if measure < point.measure: break
			output = point
		return output

	def get_step_at_time(self, time: float, latest_timing_point: game.fnf.timingpoint.TimingPoint = None) -> float:
		if not latest_timing_point:
			latest_timing_point = self.get_timing_point_at_time(time)
		
		return latest_timing_point.step + (time - latest_timing_point.time) / latest_timing_point.get_step_length()

	def get_beat_at_time(self, time: float, latest_timing_point: game.fnf.timingpoint.TimingPoint = None) -> float:
		if not latest_timing_point:
			latest_timing_point = self.get_timing_point_at_time(time)
		
		return latest_timing_point.beat + (time - latest_timing_point.time) / latest_timing_point.get_beat_length()

	def get_measure_at_time(self, time: float, latest_timing_point: game.fnf.timingpoint.TimingPoint = None) -> float:
		if not latest_timing_point:
			latest_timing_point = self.get_timing_point_at_time(time)
		
		return latest_timing_point.measure + (time - latest_timing_point.time) / latest_timing_point.get_measure_length()

	def update(self, delta: float):
		if self.auto_increment:
			self.raw_time += (delta * 1000.0) * self.get_rate()
			self.visual_time = self.get_time()
		
		self.playhead = self.visual_time
		
		cur_timing_point: game.fnf.timingpoint.TimingPoint = self.get_timing_point_at_time(self.get_time())
		self._latest_timing_point = cur_timing_point
		
		_last_step = self.cur_step
		_last_beat = self.cur_beat
		_last_measure = self.cur_measure
		
		self.cur_dec_step = self.get_step_at_time(self.get_time(), cur_timing_point)
		self.cur_step = math.floor(self.cur_dec_step)
		
		if self.cur_step > _last_step:
			for i in range(_last_step, self.cur_step):
				Conductor.step_hit.emit(i + 1)
		
		self.cur_dec_beat = self.get_beat_at_time(self.get_time(), cur_timing_point)
		self.cur_beat = math.floor(self.cur_dec_beat)
		
		if self.cur_beat > _last_beat:
			for i in range(_last_beat, self.cur_beat):
				Conductor.beat_hit.emit(i + 1)
		
		self.cur_dec_measure = self.get_measure_at_time(self.get_time(), cur_timing_point)
		self.cur_measure = math.floor(self.cur_dec_measure)
		
		if self.cur_measure > _last_measure:
			for i in range(_last_beat, self.cur_measure):
				Conductor.measure_hit.emit(i + 1)

		super().update(delta)
