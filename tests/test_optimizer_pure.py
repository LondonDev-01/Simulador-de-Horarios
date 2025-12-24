from src.models import ClassBlock, Section, CourseCombination
from src.optimizer import generate_schedules
from datetime import time

def test_optimizer_pure():
    # Setup some fake data without parser
    # Course 1: Algoritmos
    # Comb 1: Mon 10-12
    # Comb 2: Mon 11-13 (overlaps with Mon 10-12 if checked diff, but this is one course)
    
    # We need two COURSES to test collision.
    
    # Course A: Math
    # Opt A1: Mon 08:00-10:00
    # Opt A2: Mon 12:00-14:00
    
    # Course B: Physics
    # Opt B1: Mon 09:00-11:00 (Collides with A1)
    # Opt B2: Mon 14:00-16:00 (Safe)
    
    sec_a1 = Section("Math", "T01", "L1", "TEO", [ClassBlock("Lunes", time(8,0), time(10,0))])
    comb_a1 = CourseCombination("Math", [sec_a1])
    
    sec_a2 = Section("Math", "T02", "L2", "TEO", [ClassBlock("Lunes", time(12,0), time(14,0))])
    comb_a2 = CourseCombination("Math", [sec_a2])
    
    sec_b1 = Section("Physics", "T01", "L1", "TEO", [ClassBlock("Lunes", time(9,0), time(11,0))])
    comb_b1 = CourseCombination("Physics", [sec_b1])
    
    sec_b2 = Section("Physics", "T02", "L2", "TEO", [ClassBlock("Lunes", time(14,0), time(16,0))])
    comb_b2 = CourseCombination("Physics", [sec_b2])
    
    courses_map = {
        "Math": [comb_a1, comb_a2],
        "Physics": [comb_b1, comb_b2]
    }
    
    print("Testing Optimizer...")
    results = generate_schedules(courses_map)
    print(f"Found {len(results)} valid schedules.")
    
    for i, res in enumerate(results):
        print(f"Schedule {i+1}:")
        for c in res.combinations:
            print(f"  - {c.course_name} {c.sections[0].section_code} ({c.sections[0].blocks[0]})")
        print(f"  Early Score: {res.score_early_starts}")

    # Expected:
    # A1 (Mon 8-10) + B1 (Mon 9-11) -> COLLISION (Should not exist)
    # A1 (Mon 8-10) + B2 (Mon 14-16) -> VALID
    # A2 (Mon 12-14) + B1 (Mon 9-11) -> VALID
    # A2 (Mon 12-14) + B2 (Mon 14-16) -> VALID
    
    # Total 3 valid schedules.
    assert len(results) == 3

if __name__ == "__main__":
    test_optimizer_pure()
