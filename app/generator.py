import random
from typing import Any
import numpy as np

# (set_name, time_minutes, stroke_rate, resistance_level)
WorkoutSet = tuple[str, float, int, int] 

INTERVAL_MINUTES = 5 
INTERVAL_SECONDS = INTERVAL_MINUTES * 60

WORKOUT_TYPES = [
    'Cardio 🫀',
    'Interval ⏳',
    'Pyramid-SPM 📶',
    'Pyramid-Time ⏱️',
    'Strength 💪',
    'Surprise 🎱'
]

DIFFICULTIES = [
    'Easy 🥱',
    'Medium 😎',
    'Hard 😖'
]


def get_intensity_params(difficulty: str) -> dict[str, Any]:
    """Returns base parameters (SPM, Resistance) based on difficulty."""
    match difficulty:
        case 'Easy 🥱':
            return {'spm': 22, 'resistance': 4}
        case 'Medium 😎':
            return {'spm': 24, 'resistance': 5}
        case 'Hard 😖':
            return {'spm': 26, 'resistance': 6}
        case _:
            return {'spm': 24, 'resistance': 5} # Default


def generate_endurance_workout(
    main_time: int | float,
    difficulty: str
) -> list[WorkoutSet]:
    """Generates a steady-state endurance workout."""
    params = get_intensity_params(difficulty)
    spm = params['spm']
    resistance = params['resistance']
    return [("Steady State Row", main_time*60, spm, resistance)]


def generate_interval_workout(
    main_time: int | float,
    difficulty: str
) -> list[WorkoutSet]:
    """Generates a high-intensity interval training (HIIT) workout."""
    params = get_intensity_params(difficulty)
    work_spm = params['spm'] + 4 # Higher SPM for max effort
    rest_spm = 20
    base_resistance = params['resistance']
    
    # Adjust work/rest ratio based on difficulty
    work_duration = 1.0 # 1 minute
    
    match difficulty:
        case 'Easy 🥱':
            rest_duration = 1.5 # Longer rest period
        case 'Medium 😎':
            work_duration = 1.5 # Longer work period
        case 'Hard 😖':
            rest_duration = 0.5 # Shorter rest for hard

    num_cycles = int(main_time // (work_duration + rest_duration))
    
    workout = []
    for i in range(num_cycles):
        workout.append(
            (f"Work Interval {i+1}", work_duration*60, work_spm, base_resistance)
        )
        workout.append(
            (f"Rest Interval {i+1}", rest_duration*60, rest_spm, base_resistance)
        )

    # Account for any time left over
    remaining_time = main_time - sum(set_[1] for set_ in workout)
    if remaining_time < (rest_duration + work_duration):
         workout.append(("Final Easy Row", remaining_time*60, rest_spm, 5))

    return workout


def generate_rate_pyramid_workout(
    main_time: int | float,
    difficulty: str,
) -> list[WorkoutSet]:
    """Generates a pyramid workout that increases, then decreses in intensity"""
    if main_time < 20:
        pattern = '12321'
    else:
        pattern = '1234321'

    match difficulty:
        case 'Easy 🥱':
            multiplier = 1.5
        case 'Medium 😎':
            multiplier = 1.7
        case 'Hard 😖':
            multiplier = 1.9

    n_segments = len(pattern) * 2
    segment_time = main_time / n_segments
    base = get_intensity_params(difficulty)
    rest_period = ('Rest', int(segment_time*60), base['spm'], base['resistance'])

    workout = []
    for i, interval in enumerate(pattern):

        if i < len(pattern)//2:
            section = 'Climbing'
        elif i > len(pattern)//2:
            section = 'Descending'
        else:
            section = 'Peak'

        interval_num = int(interval)
        work_period = (f'Work Period {i+1}: {section}', int(segment_time*60),
                       int(base['spm'] + interval_num*multiplier), base['resistance'])
        workout.append(work_period)
        workout.append(rest_period)

    return workout


def generate_time_pyramid_workout(
    main_time: int | float,
    difficulty: str,
) -> list[WorkoutSet]:
    """Generates a pyramid workout that increases, then decreses in intensity"""
    if main_time < 24:
        pattern = '12321'
    else:
        pattern = '1234321'

    match difficulty:
        case 'Easy 🥱':
            rest_duration = 0.75
        case 'Medium 😎':
            rest_duration = 0.5
        case 'Hard 😖':
            rest_duration = 0.5

    base = get_intensity_params(difficulty)
    rest_period = ('Rest', rest_duration*60, base['spm']-2, base['resistance'])
    nonrest_time = main_time - rest_duration * len(pattern)
    pattern_num = np.array(list(pattern)).astype(int)
    interval_times = pattern_num/pattern_num.sum() * nonrest_time

    workout = []
    for i, time in enumerate(interval_times):

        if i < len(pattern)//2:
            section = 'Climbing'
        elif i > len(pattern)//2:
            section = 'Descending'
        else:
            section = 'Peak'

        work_period = (f'Work Period {i+1}: {section}', int(time*60),
                       base['spm'] + 3, base['resistance'])
        workout.append(work_period)
        workout.append(rest_period)

    return workout


def generate_strength_workout(
    main_time: int | float,
    difficulty: str
) -> list[WorkoutSet]:
    """Generates a low-rate, high-force strength workout."""
    power_spm = 20
    
    match difficulty:
        case 'Easy 🥱':
            high_resistance = 6 # Slightly lower resistance for easier adaptation
            rep_duration, rest_duration = 0.5, 1.0
        case 'Medium 😎':
            high_resistance = 7
            rep_duration, rest_duration = 0.5, 1.0
        case 'Hard 😖':
            high_resistance = 8
            rep_duration, rest_duration = 1.0, 1.0

    num_sets = int(main_time // (rep_duration + rest_duration))
    
    workout = []
    for i in range(num_sets):
        workout.append(
            (f"Power Pull {i+1}", rep_duration*60, power_spm, high_resistance)
        )
        workout.append(
            (f"Active Recovery {i+1}", rest_duration*60, 18, 5)
        )

    return workout


def generate_surprise_workout(
    main_time: int | float,
    difficulty: str
) -> list[WorkoutSet]:
    """Generates a random mix of endurance, interval, and cardio sets."""
    workouts_available = [generate_endurance_workout, generate_interval_workout, generate_strength_workout]
    
    # Split the main time into 3-5 segments and assign a random workout type
    num_segments = random.randint(3, 6)
    segment_time = main_time / num_segments
    
    workout = []
    for i in range(num_segments):
        generator = random.choice(workouts_available)
        segment_sets = generator(segment_time, difficulty)
        # Rename segments to reflect the overall 'Surprise' theme
        for set_name, time, spm, res in segment_sets:
             workout.append((f"Surprise Segment {i+1}: {set_name}", time, spm, res))

    return workout


def generate_rowing_workout(
    workout_type: str,
    difficulty: str,
    total_time_minutes: int
) -> list[WorkoutSet]:
    """
    Generates a structured rowing workout pattern using dedicated functions 
    and returns a list of tuples.
    """
    # 1. Input Validation and Time Allocation
    if total_time_minutes < 15:
        raise ValueError("Total workout time must be at least 15 minutes.")
    
    warmup_time = 5.0
    cooldown_time = 5.0
    main_time = total_time_minutes - warmup_time - cooldown_time
    if main_time < 0: # Handle cases where total_time is too small
        main_time = total_time_minutes / 2
        warmup_time = total_time_minutes / 4
        cooldown_time = total_time_minutes / 4

    # 2. Main Workout Generation using match/case
    match workout_type:
        case 'Cardio 🫀':
            main_sets = generate_endurance_workout(main_time, difficulty)
        case 'Interval ⏳':
            main_sets = generate_interval_workout(main_time, difficulty)
        case 'Pyramid-SPM 📶':
            main_sets = generate_rate_pyramid_workout(main_time, difficulty)
        case 'Pyramid-Time ⏱️':
            main_sets = generate_time_pyramid_workout(main_time, difficulty)
        case 'Strength 💪':
            main_sets = generate_strength_workout(main_time, difficulty)
        case 'Surprise 🎱':
            main_sets = generate_surprise_workout(main_time, difficulty)
        case _:
            raise ValueError(f"Unknown workout type: {workout_type}.")
    
    # Warm-up (Low SPM, Low Resistance)
    warmup_set = ("Warm-up", warmup_time*60, 20, 3)
    
    # Cool-down (Low SPM, Low Resistance)
    main_set_times = sum([x[1] for x in main_sets])
    extra_cooldown_time = int(total_time_minutes*60 - main_set_times - warmup_time*60)
    cooldown_set = ("Cool-down", extra_cooldown_time, 18, 2)
    
    return [warmup_set] + main_sets + [cooldown_set]

