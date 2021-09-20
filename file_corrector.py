import os

def correct_postcode(content):
    content = content.replace("ABC", "1AB")
    return content

def s251_replacer(content):
    content = content.replace("s251", "1")
    return content

if __name__ == "__main__":
    for filename in [filename for filename in os.listdir('.') if filename.split(".")[-1] == "csv"]:
        print(filename)

        f = open(filename, "r")
        content = f.read()
        f.close()
        print(content)

        output = s251_replacer(content)
        print(output)

        f = open(filename, "w")
        f.write(output)
        f.close()
    

    
    
