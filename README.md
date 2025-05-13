# Magic Square Life Path Analyzer

## White Paper: Personalized Magic Square Generation and Life Path Analysis

### Abstract
This document describes an algorithmic approach to generating personalized magic squares and using them for detailed life path analysis. The system leverages a hybrid evolutionary and boosting algorithm, embedding personal numerological data into the construction of magic squares of various sizes. The resulting matrices are then used as the basis for AI-generated life path reports, offering unique, non-generalizable insights for individuals.

### Introduction
Magic squares have long been associated with mysticism, numerology, and personal insight. This project automates the generation of magic squares that incorporate personal data (such as name and date of birth), and uses these squares as a foundation for AI-driven life path analysis.

### Algorithm Overview
1. **Personal Number Extraction**:  
   - The individual's name and date of birth are converted into a set of "personal numbers" using digital root calculations and character encoding.
2. **Magic Square Generation**:  
   - For each desired size (e.g., 3x3, 7x7, 9x9, 13x13), a population of random squares is generated, embedding the personal numbers where possible.
   - A fitness function evaluates each square based on how closely its rows, columns, and diagonals sum to the magic constant, and how well it incorporates the personal numbers.
   - A boosting step iteratively tweaks the squares to improve their fitness.
   - Multiprocessing is used to accelerate the search.
3. **Output**:  
   - The best magic squares found for each size are saved.
   - AI prompt templates are generated, embedding the squares and personal data, to guide the creation of detailed, individualized life path reports.

### Applications
- **Personalized Numerology Reports**:  
  The generated prompts can be fed into large language models (LLMs) to produce highly individualized life path analyses.
- **Self-Discovery Tools**:  
  Users can explore unique patterns and insights based on their own numerological data.

### Limitations
- The algorithm does not guarantee a perfect magic square for all sizes and personal number combinations.
- The interpretive value of the output depends on the quality of the AI prompt and the LLM used.

### Future Work
- Improved embedding of personal numbers.
- Support for larger square sizes and more complex numerological systems.
- Integration with web interfaces for broader accessibility.

---

## Usage Instructions

### Requirements
- Python 3.x
- numpy

### Installation
1. Clone or download this repository.
2. Install numpy if not already installed:
   ```
   pip install numpy
   ```

### How to Run
1. **Edit Personal Details**  
   Open `magic_square.py` and set your name and date of birth in the `__main__` section:
   ```python
   name = "Your Name"
   date_of_birth = "DD/MM/YYYY"
   ```
2. **Run the Script**  
   In your terminal, navigate to the project directory and run:
   ```
   python magic_square.py
   ```
3. **Output**  
   - The script will print progress and results to the console.
   - It will generate several text files in the same directory:
     - `<Your Name>-BRIEF.txt`
     - `<Your Name>_extended_report.txt`
     - `<Your Name>_detailed_report.txt`

### How to Use the Output for AI Prompts
- Each generated `.txt` file contains a prompt template with your personal information and the generated magic squares.
- Copy the content of any of these files and paste it into your preferred AI language model (such as ChatGPT, Claude, or Gemini).
- The AI will use the prompt to generate a detailed, personalized life path report based on your unique magic squares.

#### Example
1. Open `<Name Surname>_extended_report.txt` (or your own output file).
2. Copy the entire contents.
3. Paste into ChatGPT or another LLM and ask it to generate a life path report.

### Customization
- You can adjust the sizes of the magic squares by modifying the `for size in [3,7,9,13]:` line in `magic_square.py`.
- To analyze different people, simply change the `name` and `date_of_birth` variables and rerun the script.

### Notes
- The algorithm may take several minutes to run, especially for larger square sizes.
- The quality and uniqueness of the AI-generated report depend on the prompt and the capabilities of the language model used. 
