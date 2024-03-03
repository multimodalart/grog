import gradio as gr
from urllib.parse import urlparse
import requests
import os
import time

from utils.gradio_helpers import parse_outputs, process_outputs

inputs = []
inputs.append(gr.Textbox(
    label="Prompt", info='''Input prompt'''
))

inputs.append(gr.Dropdown(
    choices=['announcer', 'de_speaker_0', 'de_speaker_1', 'de_speaker_2', 'de_speaker_3', 'de_speaker_4', 'de_speaker_5', 'de_speaker_6', 'de_speaker_7', 'de_speaker_8', 'de_speaker_9', 'en_speaker_0', 'en_speaker_1', 'en_speaker_2', 'en_speaker_3', 'en_speaker_4', 'en_speaker_5', 'en_speaker_6', 'en_speaker_7', 'en_speaker_8', 'en_speaker_9', 'es_speaker_0', 'es_speaker_1', 'es_speaker_2', 'es_speaker_3', 'es_speaker_4', 'es_speaker_5', 'es_speaker_6', 'es_speaker_7', 'es_speaker_8', 'es_speaker_9', 'fr_speaker_0', 'fr_speaker_1', 'fr_speaker_2', 'fr_speaker_3', 'fr_speaker_4', 'fr_speaker_5', 'fr_speaker_6', 'fr_speaker_7', 'fr_speaker_8', 'fr_speaker_9', 'hi_speaker_0', 'hi_speaker_1', 'hi_speaker_2', 'hi_speaker_3', 'hi_speaker_4', 'hi_speaker_5', 'hi_speaker_6', 'hi_speaker_7', 'hi_speaker_8', 'hi_speaker_9', 'it_speaker_0', 'it_speaker_1', 'it_speaker_2', 'it_speaker_3', 'it_speaker_4', 'it_speaker_5', 'it_speaker_6', 'it_speaker_7', 'it_speaker_8', 'it_speaker_9', 'ja_speaker_0', 'ja_speaker_1', 'ja_speaker_2', 'ja_speaker_3', 'ja_speaker_4', 'ja_speaker_5', 'ja_speaker_6', 'ja_speaker_7', 'ja_speaker_8', 'ja_speaker_9', 'ko_speaker_0', 'ko_speaker_1', 'ko_speaker_2', 'ko_speaker_3', 'ko_speaker_4', 'ko_speaker_5', 'ko_speaker_6', 'ko_speaker_7', 'ko_speaker_8', 'ko_speaker_9', 'pl_speaker_0', 'pl_speaker_1', 'pl_speaker_2', 'pl_speaker_3', 'pl_speaker_4', 'pl_speaker_5', 'pl_speaker_6', 'pl_speaker_7', 'pl_speaker_8', 'pl_speaker_9', 'pt_speaker_0', 'pt_speaker_1', 'pt_speaker_2', 'pt_speaker_3', 'pt_speaker_4', 'pt_speaker_5', 'pt_speaker_6', 'pt_speaker_7', 'pt_speaker_8', 'pt_speaker_9', 'ru_speaker_0', 'ru_speaker_1', 'ru_speaker_2', 'ru_speaker_3', 'ru_speaker_4', 'ru_speaker_5', 'ru_speaker_6', 'ru_speaker_7', 'ru_speaker_8', 'ru_speaker_9', 'tr_speaker_0', 'tr_speaker_1', 'tr_speaker_2', 'tr_speaker_3', 'tr_speaker_4', 'tr_speaker_5', 'tr_speaker_6', 'tr_speaker_7', 'tr_speaker_8', 'tr_speaker_9', 'zh_speaker_0', 'zh_speaker_1', 'zh_speaker_2', 'zh_speaker_3', 'zh_speaker_4', 'zh_speaker_5', 'zh_speaker_6', 'zh_speaker_7', 'zh_speaker_8', 'zh_speaker_9'], label="history_prompt", info='''history choice for audio cloning, choose from the list''', value="None"
))

inputs.append(gr.File(
    label="Custom History Prompt"
))

inputs.append(gr.Number(
    label="Text Temp", info='''generation temperature (1.0 more diverse, 0.0 more conservative)''', value=0.7
))

inputs.append(gr.Number(
    label="Waveform Temp", info='''generation temperature (1.0 more diverse, 0.0 more conservative)''', value=0.7
))

inputs.append(gr.Checkbox(
    label="Output Full", info='''return full generation as a .npz file to be used as a history prompt''', value=False
))

names = ['prompt', 'history_prompt', 'custom_history_prompt', 'text_temp', 'waveform_temp', 'output_full']

outputs = []
outputs.append(gr.Audio(type='filepath'))

expected_outputs = len(outputs)
def predict(request: gr.Request, *args, progress=gr.Progress(track_tqdm=True)):
    headers = {"Content-Type": "application/json", }

    payload = {"input": {}}
    
    
    base_url = "http://localhost:7860"
    for i, key in enumerate(names):
        value = args[i]
        if value and os.path.exists(str(value)):
            value = f"{base_url}/file=" + value
        if value:
            payload["input"][key] = value

    response = requests.post("http://localhost:5000/predictions", headers=headers, json=payload)
    if response.status_code not in [200, 201]:
        raise gr.Error(f"The submission failed! Error: {response.status_code}")

    if response.status_code == 201:
        follow_up_url = response.json()["urls"]["get"]
        while True:
            response = requests.get(follow_up_url, headers=headers)
            if response.json()["status"] == "succeeded":
                break
            elif response.json()["status"] == "failed":
                raise gr.Error("The submission failed!")
            time.sleep(1)

    json_response = response.json()
    if outputs[0].get_config()["name"] == "json":
        return json_response["output"]

    predict_outputs = parse_outputs(json_response["output"])
    processed_outputs = process_outputs(predict_outputs)
    difference_outputs = expected_outputs - len(processed_outputs)

    if difference_outputs > 0:
        processed_outputs.extend([gr.update(visible=False)] * difference_outputs)
    elif difference_outputs < 0:
        processed_outputs = processed_outputs[:expected_outputs]

    # If multiple outputs, return as a tuple so Gradio can unpack
    return tuple(processed_outputs) if len(processed_outputs) > 1 else processed_outputs[0]

title = "Demo for bark cog image by suno-ai"
model_description = "🔊 Text-Prompted Generative Audio Model"

app = gr.Interface(
    fn=predict,
    inputs=inputs,
    outputs=outputs,
    title=title,
    description=model_description,
    allow_flagging="never",
)
app.launch(share=True)
