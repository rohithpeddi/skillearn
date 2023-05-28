def parse_structure(filepath):
    result = {}
    stack = [result]
    indent_levels = [0]

    with open(filepath, 'r') as file:
        lines = file.readlines()

    for line in lines:
        indentation = len(line) - len(line.lstrip('|'))
        line = line.strip('|').strip()

        while len(indent_levels) > 0 and indentation <= indent_levels[-1]:
            indent_levels.pop()
            stack.pop()

        if line.startswith('+'):
            new_dict = {}
            stack[-1][line.strip('+').strip()] = new_dict
            stack.append(new_dict)
            indent_levels.append(indentation)
        elif line.startswith('-'):
            key_value = line.strip('-').strip().split('(', 1)
            if len(key_value) == 2:
                key, value = key_value[0].strip(), key_value[1].rstrip(')')
            else:
                key = key_value[0]
                value = None
            stack[-1][key] = value

    return result


structure_dict = parse_structure('folder_structure.txt')
print(structure_dict)
