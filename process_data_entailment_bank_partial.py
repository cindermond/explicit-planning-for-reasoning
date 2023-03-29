import pickle
import jsonlines
import random
import math

train_percentage = 0.001
dataset_num = '1'
dataset_split = 'train'
path = f'data/entailment-bank/dataset/task_{dataset_num}/{dataset_split}.jsonl'
selector_data = []
inference_data = []
total_data = []
no_label_data = []
with jsonlines.open(path, 'r') as file:
    lines = [line for line in file.iter()]
    random.Random(42).shuffle(lines)
    train_data_num = math.ceil(len(lines) * train_percentage)
    for line in lines[:train_data_num]:
        stat_dict = {}
        stat_dict.update(line["meta"]["triples"])
        stat_dict.update(line["meta"]["intermediate_conclusions"])
        splited_proof = [a.strip() for a in line["meta"]["step_proof"].split(";") if a.strip()]
        current_context = [t for t in line["meta"]["triples"].values()]
        to_add_to_total_data = []
        for proof in splited_proof:
            words = [w.strip() for w in proof.split(':')[0].split(' ') if w.strip()]
            current_list = []
            is_end = False
            for word in words:
                if word == "->":
                    is_end = True
                    continue
                if word == "&":
                    continue
                if is_end and word == "hypothesis":
                    result = stat_dict[line["meta"]["hypothesis_id"]]
                    continue
                if is_end:
                    result = stat_dict[word]
                    continue
                current_list.append(stat_dict[word])
            selector_data.append(
                {
                    "hypothesis": line["hypothesis"],
                    "context": current_context.copy(), 
                    "selection": current_list.copy(),
                    "selection_index": [current_context.index(x) for x in current_list]#for easier training
                }
            )
            inference_data.append(
                {
                    "input": current_list.copy(),
                    "target": result
                }
            )
            to_add_to_total_data.append(
                {
                    "selection": current_list.copy(),
                    "target": result
                }
            )
            current_context.append(result)

        selector_data.append(
            {
                "hypothesis": line["hypothesis"],
                "context": current_context.copy(), 
                "selection": ["<qed>"],
                "selection_index": [50] #<qed> is fixed as the 51th choice since there is at most 25+17 normal choices in entailment bank.
            }
        )

        total_data.append(
            {
                "hypothesis": line["hypothesis"],
                "context": [t for t in line["meta"]["triples"].values()],
                "proof": to_add_to_total_data.copy()
            }
        )


    for line in lines[train_data_num:]:
        no_label_data.append(
            {
                "hypothesis": line["hypothesis"],
                "context": [t for t in line["meta"]["triples"].values()],
            }
        )






with open(f'data/modified/{dataset_split}set-entailment-bank-task-{dataset_num}-sel-{train_data_num}.pickle', 'wb') as handle:
    pickle.dump(selector_data, handle)

with open(f'data/modified/{dataset_split}set-entailment-bank-task-{dataset_num}-inf-{train_data_num}.pickle', 'wb') as handle:
    pickle.dump(inference_data, handle)

with open(f'data/modified/{dataset_split}set-entailment-bank-task-{dataset_num}-tot-{train_data_num}.pickle', 'wb') as handle:
    pickle.dump(total_data, handle)

with open(f'data/modified/{dataset_split}set-entailment-bank-task-{dataset_num}-nolab-{train_data_num}.pickle', 'wb') as handle:
    pickle.dump(no_label_data, handle)