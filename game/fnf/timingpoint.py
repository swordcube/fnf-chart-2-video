import game.game
import game.fnf.conductor

from typing import Self

class TimingPoint:
	def __init__(self, time: float = 0.0, step: float = 0.0, beat: float = 0.0, measure: float = 0.0, bpm: float = 100.0, time_signature: list[int] = [4, 4]):
		self.time = time
		self.step = step
		self.beat = beat
		self.measure = measure
		self.bpm = bpm
		self.time_signature = time_signature

	@staticmethod
	def from_dict(le_dict: dict) -> Self:
		tp: TimingPoint = TimingPoint()
		tp.time = le_dict["time"]
		tp.step = le_dict["step"] if "step" in le_dict else 0.0
		tp.beat = le_dict["beat"] if "beat" in le_dict else 0.0
		tp.measure = le_dict["measure"] if "measure" in le_dict else 0.0
		tp.bpm = le_dict["bpm"]
		tp.time_signature = le_dict["time_signature"]
		return tp

	def get_beat_length(self) -> float:
		return game.fnf.conductor.Conductor.seconds_to_ms(60.0 / self.bpm)

	def get_step_length(self) -> float:
		return self.get_beat_length() / game.fnf.conductor.Conductor.get_denominator(self.time_signature)

	def get_measure_length(self) -> float:
		return self.get_beat_length() * game.fnf.conductor.Conductor.get_numerator(self.time_signature)
