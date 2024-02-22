from datatest import validate

letters = [["A"], ["B"], ["C"], ["D"], ["E"], ["F"], ["G"], ["H"], ["I"], ["J"]]
requirements = ["A", "B", "C"]
# validate(letters, requirement)

for letter in letters:
    for requirement in requirements:
        if letter[0] == requirement:
            print("Correct", letter[0], requirement)
            validate(letter, requirement)
        else:
            print("Incorrect", letter[0], requirement)
            validate(letter, requirement)
