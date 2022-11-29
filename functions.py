from cgitb import text
import numpy as np

# Source: https://www.datacamp.com/tutorial/fuzzy-string-python
def levenshtein_ratio_and_distance(s, t, ratio_calc = False):
    """ levenshtein_ratio_and_distance:
        Calculates levenshtein distance between two strings.
        If ratio_calc = True, the function computes the
        levenshtein distance ratio of similarity between two strings
        For all i and j, distance[i,j] will contain the Levenshtein
        distance between the first i characters of s and the
        first j characters of t
    """
    # Initialize matrix of zeros
    rows = len(s)+1
    cols = len(t)+1
    distance = np.zeros((rows,cols),dtype = int)

    # Populate matrix of zeros with the indeces of each character of both strings
    for i in range(1, rows):
        for k in range(1,cols):
            distance[i][0] = i
            distance[0][k] = k

    # Iterate over the matrix to compute the cost of deletions,insertions and/or substitutions    
    for col in range(1, cols):
        for row in range(1, rows):
            if s[row-1] == t[col-1]:
                cost = 0 # If the characters are the same in the two strings in a given position [i,j] then the cost is 0
            else:
                # In order to align the results with those of the Python Levenshtein package, if we choose to calculate the ratio
                # the cost of a substitution is 2. If we calculate just distance, then the cost of a substitution is 1.
                if ratio_calc == True:
                    cost = 2
                else:
                    cost = 1
            distance[row][col] = min(distance[row-1][col] + 1,      # Cost of deletions
                                 distance[row][col-1] + 1,          # Cost of insertions
                                 distance[row-1][col-1] + cost)     # Cost of substitutions
    if ratio_calc == True:
        # Computation of the Levenshtein Distance Ratio
        Ratio = ((len(s)+len(t)) - distance[row][col]) / (len(s)+len(t))
        return Ratio
    else:
        # print(distance) # Uncomment if you want to see the matrix showing how the algorithm computes the cost of deletions,
        # insertions and/or substitutions
        # This is the minimum number of edits needed to convert string a to string b
        return "The strings are {} edits away".format(distance[row][col])

def bf_string_match(str1, str2):
    # Use ternary to identify Text and substring
    # Text = Longer string, substring = shorter string
    text =  str1 if len(str1) >= len(str2) else str2
    substring = str2 if len(str1) >= len(str2) else str1
    for i in range(len(text)):
        for j in range(len(substring)):
            if i + j >= len(text):
                break
            if text[i + j] != substring[j]:
                break
        else:
            return True
    return False

# As defined from: https://anhaidgroup.github.io/py_stringmatching/v0.3.x/PartialRatio.html
# It finds the fuzzy wuzzy ratio similarity measure between the shorter string 
# and every substring of length m of the longer string, 
# and returns the maximum of those similarity measures. 

def partial_ratio(str1, str2):
    # Use ternary to identify Text and substring
    # Text = Longer string, substring = shorter string
    text =  str1.lower() if len(str1) >= len(str2) else str2.lower()
    substring = str2.lower() if len(str1) >= len(str2) else str1.lower()
    best_ratio = 0
    for i in range(len(text)):
        if i+len(substring)-1 >= len(text):     
            break
        current_ratio = levenshtein_ratio_and_distance(substring, text[i:i+len(substring)], ratio_calc=True)
        if current_ratio > best_ratio:
            best_ratio = current_ratio
    return(best_ratio)
