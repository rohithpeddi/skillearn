import yaml

with open('activity_dict_with_step_index.yml', 'r') as file:
    all_recipe = yaml.safe_load(file)
    for recipe in all_recipe:
        print(recipe)
        for step in all_recipe[recipe]:
            print("<Label value=\"%s: %s\"  background=\"#FF0000\"/>" % (step,all_recipe[recipe][step]['text']))

