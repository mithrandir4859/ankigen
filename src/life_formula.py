import datetime

from pydantic import BaseModel, confloat

BILLION = 1_000_000_000

class MultiverseStateMetric(BaseModel):
    name: str
    unit: str
    coefficient: confloat(gt=0, default=1)

MULTIVERSE_STATE_METRICS = [
    MultiverseStateMetric(name='intelligence', unit='trillions of approximately human-level intelligences'),
    MultiverseStateMetric(name='mass', unit='solar mass'),
    MultiverseStateMetric(name='description_size', unit='kylobyte'),
    MultiverseStateMetric(name='volume', unit='cubic kilometer'),
]

class MultiverseState:
    def get_metric_value(self, metric_name):
        # ??? extremely smart logic here
        return 100  # just a placeholder
    
    @property
    def transcendence_score(self):
        score = 0
        for metric in MULTIVERSE_STATE_METRICS:
            score += self.get_metric_value(metric.name) * metric.coefficient
        return score

class TimePeriod:
    start: int  # years in the future
    end: int  # years in the future

class Goal:
    target_state: MultiverseState
    target_time: TimePeriod
    prerequisite_goals: list['Goal']

    @property
    def likeliest_achievement_time(self):
        # ??? extremely smart logic here
        return 0.1 * BILLION  # just a placeholder
    
    @property
    def transcendence_score(self):
        score = self.target_state.transcendence_score * self.likeliest_achievement_time
        scores = [goal.transcendence_score for goal in self.prerequisite_goals]
        scores.append(score)
        
        # why max and not the sum?
        # because when calculating the transcendence score, we don't want to increase the score
        # for more detailed goals which contain many subgoals compared to less detailed goals which
        # still consider large Multiverse states far in the future
        return max(scores)
    


