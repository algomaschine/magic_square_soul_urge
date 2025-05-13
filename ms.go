package main

import (
	"fmt"
	"math/rand"
	"sync"
	"time"
)

// Calculate the digital root of a number
func digitalValue(n int) int {
	for n >= 10 {
		sum := 0
		for n > 0 {
			sum += n % 10
			n /= 10
		}
		n = sum
	}
	return n
}

// Generate a random magic square, optionally embedding personal numbers
func generateRandomSquare(size int, personalNumbers []int) [][]int {
	allNumbers := make([]int, size*size)
	for i := 1; i <= size*size; i++ {
		allNumbers[i-1] = i
	}

	if len(personalNumbers) > 0 {
		validPersonalNumbers := make([]int, 0)
		for _, num := range personalNumbers {
			for j, n := range allNumbers {
				if n == num {
					validPersonalNumbers = append(validPersonalNumbers, num)
					allNumbers = append(allNumbers[:j], allNumbers[j+1:]...)
					break
				}
			}
		}

		rand.Shuffle(len(allNumbers), func(i, j int) { allNumbers[i], allNumbers[j] = allNumbers[j], allNumbers[i] })
		allNumbers = append(allNumbers, validPersonalNumbers...)
	}

	rand.Shuffle(len(allNumbers), func(i, j int) { allNumbers[i], allNumbers[j] = allNumbers[j], allNumbers[i] })

	square := make([][]int, size)
	for i := range square {
		square[i] = make([]int, size)
		for j := range square[i] {
			square[i][j] = allNumbers[i*size+j]
		}
	}
	return square
}

// Compute fitness of a magic square
func computeFitness(square [][]int, personalNumbers []int) int {
	size := len(square)
	targetSum := size * (size*size + 1) / 2
	fitness := 0

	for i := 0; i < size; i++ {
		rowSum := 0
		colSum := 0
		for j := 0; j < size; j++ {
			rowSum += square[i][j]
			colSum += square[j][i]
		}
		fitness += abs(rowSum-targetSum) + abs(colSum-targetSum)
	}

	diagSum1, diagSum2 := 0, 0
	for i := 0; i < size; i++ {
		diagSum1 += square[i][i]
		diagSum2 += square[i][size-i-1]
	}
	fitness += abs(diagSum1-targetSum) + abs(diagSum2-targetSum)

	if len(personalNumbers) > 0 {
		for _, num := range personalNumbers {
			found := false
			for i := 0; i < size; i++ {
				for j := 0; j < size; j++ {
					if square[i][j] == num {
						found = true
						break
					}
				}
				if found {
					break
				}
			}
			if !found {
				fitness += 10
			}
		}
	}

	return fitness
}

// Perform a boosting step by making small adjustments to improve the square
func boostingStep(square [][]int, size int, learningRate float64) [][]int {
	newSquare := make([][]int, size)
	for i := range newSquare {
		newSquare[i] = make([]int, size)
		copy(newSquare[i], square[i])
	}

	fitness := computeFitness(square, nil)

	for i := 0; i < size; i++ {
		for j := 0; j < size; j++ {
			for _, change := range []int{-1, 1} {
				newSquare[i][j] += change
				newFitness := computeFitness(newSquare, nil)

				if newFitness < fitness {
					fitness = newFitness
				} else {
					newSquare[i][j] -= change
				}
			}
		}
	}

	return newSquare
}

// Evaluate a single square, boosting its fitness
func evaluateSquare(square [][]int, personalNumbers []int, size int, learningRate float64) ([][]int, int) {
	newSquare := boostingStep(square, size, learningRate)
	fitness := computeFitness(newSquare, personalNumbers)
	return newSquare, fitness
}

// XGBoost-like approach to find a magic square with concurrency
func xgboostLikeAlgorithm(personalNumbers []int, size, populationSize, generations int, learningRate float64) [][]int {
	rand.Seed(time.Now().UnixNano())

	population := make([][][]int, populationSize)
	for i := 0; i < populationSize; i++ {
		population[i] = generateRandomSquare(size, personalNumbers)
	}

	var bestSquare [][]int
	bestFitness := int(^uint(0) >> 1)

	var wg sync.WaitGroup
	mu := &sync.Mutex{}

	for generation := 0; generation < generations; generation++ {
		wg.Add(populationSize)

		for i := 0; i < populationSize; i++ {
			go func(i int) {
				defer wg.Done()
				newSquare, fitness := evaluateSquare(population[i], personalNumbers, size, learningRate)

				mu.Lock()
				if fitness < bestFitness {
					bestFitness = fitness
					bestSquare = newSquare
				}
				population[i] = newSquare
				mu.Unlock()
			}(i)
		}

		wg.Wait()

		if bestFitness == 0 {
			break
		}
	}

	return bestSquare
}

func main() {
	/*
	       #name = "Maksim Tikhomirov"
	   #date_of_birth = "18/02/1983"
	*/
	name := "Sergey Kruchkov"
	dateOfBirth := "27/06/1954"

	fmt.Println(name, dateOfBirth)

	expressionNum := digitalValue(sumAsciiValues(name))
	soulUrgeNum := digitalValue(sumVowelAsciiValues(name))
	day, month, year := 18, 3, 1980

	personalNumbers := []int{expressionNum, soulUrgeNum, digitalValue(day), digitalValue(month), digitalValue(year)}

	for size := 3; size <= 30; size += 2 {
		fmt.Printf("\nSearching for a magic square of size %dx%d with personal numbers %v\n", size, size, personalNumbers)
		bestSquare := xgboostLikeAlgorithm(personalNumbers, size, 100, 1000, 0.1)
		if bestSquare != nil {
			fmt.Printf("Found a magic square of size %dx%d:\n%v\n", size, size, bestSquare)
		} else {
			fmt.Printf("Could not find a valid magic square of size %dx%d.\n", size, size)
		}
	}
}

func abs(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

func sumAsciiValues(s string) int {
	sum := 0
	for _, char := range s {
		if char >= 'A' && char <= 'Z' || char >= 'a' && char <= 'z' {
			sum += int(char)
		}
	}
	return sum
}

func sumVowelAsciiValues(s string) int {
	sum := 0
	for _, char := range s {
		if char == 'A' || char == 'E' || char == 'I' || char == 'O' || char == 'U' ||
			char == 'a' || char == 'e' || char == 'i' || char == 'o' || char == 'u' {
			sum += int(char)
		}
	}
	return sum
}
