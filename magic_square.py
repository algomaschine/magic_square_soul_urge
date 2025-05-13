import numpy as np
import random
from multiprocessing import Pool, cpu_count

def digital_value(n):
    """Calculate the digital root of a number."""
    while n >= 10:
        n = sum(int(digit) for digit in str(n))
    return n

def generate_random_square(size, personal_numbers=None):
    """Generate a random magic square, optionally embedding personal numbers."""
    all_numbers = list(range(1, size**2 + 1))
    
    if personal_numbers:
        # Ensure all personal numbers are within the valid range and handle duplicates
        valid_personal_numbers = []
        for num in personal_numbers:
            if num in all_numbers and num not in valid_personal_numbers:
                valid_personal_numbers.append(num)
                all_numbers.remove(num)
        
        random.shuffle(all_numbers)
        square = np.array(all_numbers + valid_personal_numbers).reshape(size, size)
    else:
        random.shuffle(all_numbers)
        square = np.array(all_numbers).reshape(size, size)
    
    return square

def compute_fitness(square, personal_numbers=None):
    """Compute fitness of a magic square based on row, column, diagonal sums, and personalized constraints."""
    size = square.shape[0]
    target_sum = sum(range(1, size**2 + 1)) // size
    fitness = 0
    
    # Row and column fitness
    for i in range(size):
        row_sum = sum(square[i, :])
        col_sum = sum(square[:, i])
        fitness += abs(row_sum - target_sum) + abs(col_sum - target_sum)
    
    # Diagonal fitness
    diag_sum1 = sum(square[i, i] for i in range(size))
    diag_sum2 = sum(square[i, size - i - 1] for i in range(size))
    fitness += abs(diag_sum1 - target_sum) + abs(diag_sum2 - target_sum)

    # Penalty for missing or misplaced personal numbers
    if personal_numbers:
        for num in personal_numbers:
            if num not in square:
                fitness += 10  # Penalty for missing number
    
    return fitness

def boosting_step(square, size, learning_rate=0.1):
    """Perform a boosting step by making small adjustments to improve the square."""
    new_square = square.copy()
    fitness = compute_fitness(square)
    
    for i in range(size):
        for j in range(size):
            for change in [-1, 1]:  # Try reducing or increasing by 1
                new_square[i, j] += change
                new_fitness = compute_fitness(new_square)
                
                if new_fitness < fitness:
                    fitness = new_fitness
                else:
                    new_square[i, j] -= change  # Revert change if no improvement
    
    return new_square

def evaluate_square(square, personal_numbers, size, learning_rate):
    """Evaluate a single square, boosting its fitness."""
    new_square = boosting_step(square, size, learning_rate)
    fitness = compute_fitness(new_square, personal_numbers)
    return new_square, fitness

def xgboost_like_algorithm(personal_numbers, size=3, population_size=100, generations=500, learning_rate=0.1):
    """XGBoost-like approach to find a magic square with multiprocessing."""
    population = [generate_random_square(size, personal_numbers) for _ in range(population_size)]
    best_square = None
    best_fitness = float('inf')

    pool = Pool(processes=cpu_count()-4)

    for generation in range(generations):
        results = pool.starmap(
            evaluate_square,
            [(square, personal_numbers, size, learning_rate) for square in population]
        )

        population = [result[0] for result in results]
        fitness_scores = [result[1] for result in results]
        
        min_fitness = min(fitness_scores)
        if min_fitness < best_fitness:
            best_fitness = min_fitness
            best_square = population[fitness_scores.index(min_fitness)]
            #print(f"Generation {generation}, New Best Fitness: {best_fitness}")
            #print(f"Best Square:\n{best_square}")

        if best_fitness == 0:
            break
    
    pool.close()
    pool.join()
    
    return best_square

def get_unique_consonants(name):
    consonants = [c for c in name.upper() if c.isalpha() and c not in "AEIOU"]
    return list(dict.fromkeys(consonants))  # preserves order, removes duplicates

def get_wirth_base_consonants(name):
    # Example mapping, adjust as needed for your Wirth system
    base_map = {
        'B': 'B', 'P': 'B', 'F': 'B', 'V': 'B',
        'D': 'D', 'T': 'D', 'TH': 'D',
        'G': 'G', 'K': 'G', 'Q': 'G', 'C': 'G',
        'L': 'L', 'R': 'L', 'N': 'L', 'M': 'L',
        'S': 'S', 'Z': 'S', 'X': 'S', 'H': 'H', 'J': 'J', 'Y': 'Y', 'W': 'W'
    }
    name = name.upper()
    result = []
    for c in name:
        if c in base_map and base_map[c] not in result:
            result.append(base_map[c])
    return result

def generate_report_prompt(name, date_of_birth, personal_numbers_angel, magic_squares_angel,
                          personal_numbers_hebrew, magic_squares_hebrew,
                          personal_numbers_wirth, magic_squares_wirth, sizes):
    prompt_template = f"""
### **Extended Life Path Report and Comparison for {name}**

**Personal Information:**
- **Name**: {name}
- **Date of Birth**: {date_of_birth}

**Systems Compared:**
1. **Angel/Soul Urge** (Western, vowels)
2. **Hebrew-style** (unique consonants)
3. **Wirth Base Consonants** (mapped base consonants)

**Personal Numbers:**
- Angel/Soul Urge: {personal_numbers_angel}
- Hebrew: {personal_numbers_hebrew}
- Wirth: {personal_numbers_wirth}

**Magic Square Matrices:**

| Size | Angel/Soul Urge | Hebrew | Wirth |
|------|-----------------|--------|-------|
"""
    for i, size in enumerate(sizes):
        a = np.array_str(magic_squares_angel[i]) if magic_squares_angel[i] is not None else "N/A"
        h = np.array_str(magic_squares_hebrew[i]) if magic_squares_hebrew[i] is not None else "N/A"
        w = np.array_str(magic_squares_wirth[i]) if magic_squares_wirth[i] is not None else "N/A"
        prompt_template += f"| {size}x{size} | {a} | {h} | {w} |\n"

    prompt_template += """

**Instructions for Analysis:**
Please ensure that all interpretations and analyses are derived solely from the numbers and their positions within the provided magic square matrices. Do not generalize or bias your analysis based on the example interpretations below; these are for format illustration only, not for content inspiration.

For each system, provide:
- Age-based analysis
- Unique challenges and opportunities
- Relationship dynamics and health
- Unique personality traits and characteristics
- Challenges and opportunities
- Future predictions and focus areas
- Conclusion

**Comparison Table:**
Summarize the similarities and differences between the three systems, focusing on how the different methods of deriving personal numbers and matrices may lead to different interpretations.

"""

    filename = f"{name}_comparison_report.txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(prompt_template)
    print(f"Generated comparison report prompt saved to {filename}")

if __name__ == "__main__":
    # Input your personal details

    name = "Sergey Kryuchkov"
    date_of_birth = "27/06/1954"

    print(name, date_of_birth)

    # Angel/Soul Urge (vowels)
    expression_num = digital_value(sum(ord(char) for char in name if char.isalpha()))
    soul_urge_num = digital_value(sum(ord(char) for char in name if char in "AEIOUaeiou"))
    day, month, year = map(int, date_of_birth.split('/'))
    personal_numbers_angel = [expression_num, soul_urge_num, digital_value(day), digital_value(month), digital_value(year)]

    # Hebrew (unique consonants)
    hebrew_consonants = get_unique_consonants(name)
    hebrew_num = digital_value(sum(ord(c) for c in hebrew_consonants))
    personal_numbers_hebrew = [hebrew_num, digital_value(day), digital_value(month), digital_value(year)]

    # Wirth (base consonants)
    wirth_consonants = get_wirth_base_consonants(name)
    wirth_num = digital_value(sum(ord(c) for c in wirth_consonants))
    personal_numbers_wirth = [wirth_num, digital_value(day), digital_value(month), digital_value(year)]

    # Run the algorithm for different sizes
    sizes = [3, 5, 7, 9, 13]  # or whatever sizes you want

    magic_squares_angel = []
    magic_squares_hebrew = []
    magic_squares_wirth = []

    for size in sizes:
        magic_squares_angel.append(xgboost_like_algorithm(personal_numbers=personal_numbers_angel, size=size, population_size=100, generations=1000, learning_rate=0.1))
        magic_squares_hebrew.append(xgboost_like_algorithm(personal_numbers=personal_numbers_hebrew, size=size, population_size=100, generations=1000, learning_rate=0.1))
        magic_squares_wirth.append(xgboost_like_algorithm(personal_numbers=personal_numbers_wirth, size=size, population_size=100, generations=1000, learning_rate=0.1))

    # Only generate the extended report prompt
    generate_report_prompt(
        name, date_of_birth,
        personal_numbers_angel, magic_squares_angel,
        personal_numbers_hebrew, magic_squares_hebrew,
        personal_numbers_wirth, magic_squares_wirth,
        sizes
    )