# Define Main Function
def main():
    test_list = [
        {'Course': "C++", 'Author': "Jerry"},
        {'Course': "Python", 'Author': "Mark"},
        {'Course': "Java", 'Author': "Paul"}]

    # Find dictionary matching value in list
    res = next((sub for sub in test_list if sub['Course'] == "Java"), None)
    res["Author"] = "Thomas"

    # printing result
    # print(id(res))
    print(test_list[2])
    print(str(res))

# Define Additional Functions


# Main Function
if __name__ == '__main__':
    main()
