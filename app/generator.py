import random
from typing import Any

# (set_name, time_minutes, stroke_rate, resistance_level)
WorkoutSet = tuple[str, float, int, int] 

INTERVAL_MINUTES = 5 
INTERVAL_SECONDS = INTERVAL_MINUTES * 60

WORKOUT_TYPES = [
    'Cardio 🫀',
    'Endurance 🕓',
    'Interval ⚡',
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
    match difficulty.lower():
        case 'Easy 🥱':
            return {'spm': 22, 'resistance': 4, 'effort_mult': 0.8}
        case 'Medium 😎':
            return {'spm': 26, 'resistance': 6, 'effort_mult': 1.0}
        case 'Hard 😖':
            return {'spm': 30, 'resistance': 8, 'effort_mult': 1.2}
        case _:
            return {'spm': 24, 'resistance': 5, 'effort_mult': 1.0} # Default

def generate_endurance_workout(
    main_time: int,
    difficulty: str
) -> list[WorkoutSet]:
    """Generates a steady-state endurance workout."""
    params = get_intensity_params(difficulty)
    spm = int(params['spm'] * 0.9)  # Endurance is slightly lower rate
    resistance = params['resistance']
    
    return [
        (
            "Steady State Row", 
            main_time*60, 
            spm, 
            resistance
        )
    ]

def generate_interval_workout(
    main_time: int,
    difficulty: str
) -> list[WorkoutSet]:
    """Generates a high-intensity interval training (HIIT) workout."""
    params = get_intensity_params(difficulty)
    work_spm = params['spm'] + 4 # Higher SPM for max effort
    rest_spm = 20
    base_resistance = params['resistance']
    
    # Adjust work/rest ratio based on difficulty
    work_duration = 1.0 # 1 minute
    rest_duration = 1.0
    
    match difficulty.lower():
        case 'Hard 😖':
            rest_duration = 0.5 # Shorter rest for hard
        case 'Medium 😎':
            work_duration = 1.5 # Longer work period
        case 'Easy 🥱':
            rest_duration = 1.5 # Longer rest period

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
    if remaining_time > 0.1:
         workout.append(("Final Easy Row", remaining_time*60, 22, 5))

    return workout

def generate_strength_workout(
    main_time: int,
    difficulty: str
) -> list[WorkoutSet]:
    """Generates a low-rate, high-force strength workout."""
    params = get_intensity_params(difficulty)
    power_spm = 20
    high_resistance = 8 if params['resistance'] < 8 else 10 # Force a high damper setting
    
    # Use short, intense bursts followed by rest
    rep_duration = 0.5 # 30 seconds
    rest_duration = 1.5 # 90 seconds (more rest needed for max force)
    
    match difficulty.lower():
        case 'Hard 😖':
            rep_duration = 1.0 # Longer work period
            rest_duration = 1.0
        case 'Easy 🥱':
            high_resistance = 7 # Slightly lower resistance for easier adaptation
            
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
    main_time: int,
    difficulty: str
) -> list[WorkoutSet]:
    """Generates a random mix of endurance, interval, and cardio sets."""
    workouts_available = [generate_endurance_workout, generate_interval_workout, generate_strength_workout]
    
    # Split the main time into 2-3 segments and assign a random workout type
    num_segments = random.randint(2, 3)
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
        case 'Endurance 🕓' | 'Cardio 🫀':
            main_sets = generate_endurance_workout(main_time, difficulty)
        case 'Interval ⚡':
            main_sets = generate_interval_workout(main_time, difficulty)
        case 'Strength 💪':
            main_sets = generate_strength_workout(main_time, difficulty)
        case 'Surprise 🎱':
            main_sets = generate_surprise_workout(main_time, difficulty)
        case _:
            raise ValueError(f"Unknown workout type: {workout_type}.")
    
    # Warm-up (Low SPM, Low Resistance)
    warmup_set = ("Warm-up", warmup_time*60, 20, 3)
    
    # Cool-down (Low SPM, Low Resistance)
    cooldown_set = ("Cool-down", cooldown_time*60, 18, 2)
    
    return [warmup_set] + main_sets + [cooldown_set]

