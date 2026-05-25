import os
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForQuestionAnswering,
    TrainingArguments,
    Trainer,
    default_data_collator
)

# =========================
# CONFIGURAÇÃO
# =========================

MODEL_NAME = "deepset/roberta-base-squad2"
OUTPUT_DIR = "modelos/qa_finetuned"

MAX_LENGTH = 384


# =========================
# MAIN
# =========================

def main():

    print("\nA carregar dataset SQuAD...\n")
    dataset = load_dataset("squad")
    print("Dataset carregado!")

    print("\nA carregar tokenizer...\n")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    print("\nA carregar modelo...\n")
    model = AutoModelForQuestionAnswering.from_pretrained(MODEL_NAME)

    # =========================
    # REDUZIR DATASET (IMPORTANTE) - usar subconjunto para treino rápido
    # =========================
    train_dataset = dataset["train"].select(range(5000))
    eval_dataset = dataset["validation"].select(range(500))

    print("\nA preparar dataset...\n")

    def preprocess(examples):

        # Tokenize with overflow to handle long contexts and keep offset mappings
        tokenized_examples = tokenizer(
            examples["question"],
            examples["context"],
            truncation="only_second",
            max_length=MAX_LENGTH,
            stride=128,
            return_overflowing_tokens=True,
            return_offsets_mapping=True,
            padding="max_length",
        )

        # Map from feature to example index
        sample_mapping = tokenized_examples.pop("overflow_to_sample_mapping")
        offset_mapping = tokenized_examples.pop("offset_mapping")

        start_positions = []
        end_positions = []

        for i, offsets in enumerate(offset_mapping):
            input_ids = tokenized_examples["input_ids"][i]

            # which example does this feature come from
            sample_index = sample_mapping[i]
            answers = examples["answers"][sample_index]

            # default to CLS (0) when no answer
            if len(answers["answer_start"]) == 0:
                start_positions.append(0)
                end_positions.append(0)
                continue

            # take first answer
            start_char = answers["answer_start"][0]
            end_char = start_char + len(answers["text"][0])

            # find the start and end token indices in this feature
            sequence_ids = tokenized_examples.sequence_ids(i)

            # find the token indices that correspond to the context
            token_start_index = 0
            while sequence_ids[token_start_index] != 1:
                token_start_index += 1

            token_end_index = len(input_ids) - 1
            while sequence_ids[token_end_index] != 1:
                token_end_index -= 1

            # If answer is out of the span, label as CLS (0)
            if not (offsets[token_start_index][0] <= start_char and offsets[token_end_index][1] >= end_char):
                start_positions.append(0)
                end_positions.append(0)
            else:
                # otherwise find the exact token indices
                while token_start_index < len(offsets) and offsets[token_start_index][0] <= start_char:
                    token_start_index += 1
                start_positions.append(token_start_index - 1)

                while offsets[token_end_index][1] >= end_char:
                    token_end_index -= 1
                end_positions.append(token_end_index + 1)

        tokenized_examples["start_positions"] = start_positions
        tokenized_examples["end_positions"] = end_positions

        return tokenized_examples

    # map with batching and remove original columns to avoid duplication
    train_dataset = train_dataset.map(preprocess, batched=True, remove_columns=dataset["train"].column_names)

    train_dataset.set_format(
        type="torch",
        columns=["input_ids", "attention_mask", "start_positions", "end_positions"]
    )

    print("\nA definir treino...\n")

    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        num_train_epochs=3,
        weight_decay=0.01,
        save_strategy="epoch",
        evaluation_strategy="epoch",
        logging_steps=100,
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="loss",
    )

    # preparar dataset de validação
    eval_dataset = eval_dataset.map(preprocess, batched=True, remove_columns=dataset["validation"].column_names)
    eval_dataset.set_format(
        type="torch",
        columns=["input_ids", "attention_mask", "start_positions", "end_positions"]
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        data_collator=default_data_collator
    )

    print("\nA iniciar fine-tuning...\n")
    trainer.train()

    print("\nTreino concluído!")

    print(f"\nA guardar modelo em {OUTPUT_DIR}...\n")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    print("\nModelo guardado com sucesso!")


if __name__ == "__main__":
    main() 