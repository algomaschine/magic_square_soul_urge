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

def generate_report_prompt(name, date_of_birth, personal_numbers, magic_squares):
    """
    Generate an extended detailed life path report for an individual based on provided magic square matrices.
    The report should provide non-generalizable details, focusing on unique characteristics and events.
    """

    prompt_template = f"""
    ### **Extended Detailed Life Path Report for {name}**

    **Personal Information:**
    - **Name**: {name}
    - **Date of Birth**: {date_of_birth}
    - **Personal Numbers**: {personal_numbers}

    **Magic Square Matrices:**

    """

    matrices_str = ""
    for idx, square in enumerate(magic_squares):
        size = square.shape[0]
        matrices_str += f"\n{idx+1}. **{size}x{size} Magic Square**:\n{np.array_str(square)}\n"

    prompt_template += matrices_str

    prompt_template += f"""

    **Instructions for Detailed Analysis:**

    Please ensure that all interpretations and analyses are derived solely from the numbers and their positions within the provided magic square matrices. Do not generalize or bias your analysis based on the example interpretations below; these are for format illustration only, not for content inspiration.

    1. **Age-Based Analysis**:
       - Provide an age-by-age breakdown using the provided matrices.
       - For each age period, connect specific numbers in the matrices to unique life events, choices, or opportunities.
       - Example: "At age 30, the presence of the number 9 in the 3x3 matrix suggests a period of completion and transformation, likely associated with a career change."

    2. **Specific Life Events and Their Impact**:
       - Identify specific numbers that correspond to pivotal moments in the individual's life.
       - Example: "The number 22 in the 5x5 matrix represents significant decision points; at age 22, the individual may have faced a critical choice that shaped their future."

    3. **Health and Well-being**:
       - Analyze numbers relating to health and physical well-being.
       - Example: "Numbers 14 and 5 suggest periods of good health, with occasional stress points. At age 45, potential health challenges may emerge based on the positioning of numbers in the 7x7 matrix."

    4. **Relationship Dynamics**:
       - Examine numbers that relate to relationships, including family, friends, and romantic partnerships.
       - Example: "The presence of the number 8 in the 9x9 matrix during ages 40-49 suggests a strong focus on relationships and partnership harmony."

    5. **Unique Personality Traits and Characteristics**:
       - Use matrix numbers to highlight unique personality traits.
       - Example: "The repeated occurrence of the number 8 indicates strength and confidence, especially in professional endeavors."

    6. **Challenges and Opportunities**:
       - Identify challenges indicated by certain numbers and suggest potential opportunities.
       - Example: "The number 13 in the 5x5 matrix points to unforeseen obstacles; however, its placement alongside numbers like 20 and 25 indicates opportunities for growth through adversity."

    7. **Future Predictions and Focus Areas**:
       - Based on the analysis, suggest focus areas for the individual's future, covering personal growth, career, and relationships.
       - Example: "Future focus areas should include deepening personal relationships and considering a mentorship role, as indicated by numbers 44 and 47 in the 7x7 matrix."

    8. **Conclusion**:
       - Summarize the findings and suggest potential paths for the individual's personal and professional growth.

    """

    filename = f"{name}_extended_report.txt"

    # Write the prompt to a file
    with open(filename, "w", encoding="utf-8") as file:
        file.write(prompt_template)

    print(f"Generated extended report prompt saved to {filename}")

if __name__ == "__main__":
    # Input your personal details

    name = "Sergey Kryuchkov"
    date_of_birth = "27/06/1954"

    print(name, date_of_birth)

    # Convert name and date to numeric values
    expression_num = digital_value(sum(ord(char) for char in name if char.isalpha()))
    soul_urge_num = digital_value(sum(ord(char) for char in name if char in "AEIOUaeiou"))
    day, month, year = map(int, date_of_birth.split('/'))
    personal_numbers = [expression_num, soul_urge_num, digital_value(day), digital_value(month), digital_value(year)]

    # Run the algorithm for different sizes
    magic_squares = []
    for size in [3,5,7,9,13]: #15,17,19,21]:  # Can add more sizes if needed
        print(f"\nSearching for a magic square of size {size}x{size} with personal numbers {personal_numbers}")
        best_square = xgboost_like_algorithm(personal_numbers=personal_numbers, size=size, population_size=100, generations=1000, learning_rate=0.1)
        if best_square is not None:
            print(f"Found a magic square of size {size}x{size}:\n{best_square}")
            magic_squares.append(best_square)
        else:
            print(f"Could not find a valid magic square of size {size}x{size}.")

    # Only generate the extended report prompt
    generate_report_prompt(name, date_of_birth, personal_numbers, magic_squares)
