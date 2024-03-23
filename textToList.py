with open('taxDelinquentParcels.txt', 'r') as file:
    # Read lines from the file
    lines = file.readlines()
    # Strip newline characters from each line and store it in a list
    values_list = [line.strip() for line in lines]

print(len(values_list))
print(type(values_list))


    