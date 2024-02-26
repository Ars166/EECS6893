# EECS6893BigData
Before finetuning, please run the `preprocess.py`, which makes the .txt file to .json file, which is required by `datasets.load_dataset()`

To run the fine tuning process, please use the command.
```
python finetune.py --model_name_or_path Helsinki-NLP/opus-mt-en-zh\
--do_train True --do_eval False --source_lang en --target_lang zh --train_file translations.json --validation_file validation.json\
--output_dir checkpoint/ --per_device_train_batch_size=4 --per_device_eval_batch_size=4 --overwrite_output_dir True --predict_with_generate
```

The `test.py` returns the bertScore and a `.csv` file contain the corresponding referenced transaltion and generated translation, as well as the score.

To load from hugging face, replace the model name with `SFZheng7/MarianMT-Finetuned`

If you don't directly copy the repo, please pay attention to the file path.
