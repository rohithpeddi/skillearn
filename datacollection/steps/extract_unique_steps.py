import os
import sys
from pprint import pprint

import yaml
from loguru import logger
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

file_directory = "./"
file_name = "activity_details.txt"

config = {
    "handlers": [
        {"sink": sys.stdout,
         "format": "<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | {module}.{function} | <level>{message}</level> "},
        {"sink": "logging/logger_{time}.log",
         "format": "<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | {module}.{function} | <level>{message}</level> "}
    ],
    "extra": {"user": "sva"}
}
logger.configure(**config)
def activity_info_text_to_dict(file_name, fileFolder=None):
    recipe_name = ""
    recipe_step_dict = {}
    all_steps = []
    with open(os.path.join(fileFolder, file_name), "r") as recipe_info_file:
        for line in recipe_info_file:
            word_list = line.split(":")
            recipe_details = word_list[0].replace("\n", "")
            if len(word_list) == 1:
                recipe_name = recipe_details
                recipe_step_dict[recipe_name] = {}
            else:
                step_details = word_list[1].replace("\n", "")
                recipe_step_dict[recipe_name][word_list[0]] = step_details
                all_steps.append(step_details)
    return recipe_step_dict, all_steps


def detect_similar_steps(all_steps):
    model_name = "bert-base-cased-finetuned-mrpc"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    same_steps = {}
    for idx1, step_1 in enumerate(tqdm(all_steps)):
        for idx2, step_2 in enumerate(all_steps):
            if idx1 >= idx2:
                continue
            tokens = tokenizer.encode_plus(step_1, step_2, return_tensors="pt")
            classification_logits = model(**tokens)[0]
            results = torch.softmax(classification_logits, dim=1).tolist()[0]
            paraphrase_prob = results[1]
            if paraphrase_prob > 0.90 and step_1 != step_2:
                same_steps[idx1] = idx2
                logger.info(f"{idx1} , {step_1}")
                logger.info(f"{idx2} , {step_2}")
                logger.info("\n")
    return same_steps
    # classes = ["not paraphrase", "is paraphrase"]
    # for i in range(len(classes)):
    #     print(f"{classes[i]}: {round(results[i] * 100)}%")


activity_step_dict, all_steps = activity_info_text_to_dict(file_name, file_directory)
same_steps = detect_similar_steps(list(all_steps))
print(same_steps)
with open('same_steps_gpu_10.yml', 'w') as yaml_file:
    yaml.dump(same_steps, stream=yaml_file, default_flow_style=False)