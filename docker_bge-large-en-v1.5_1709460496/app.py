import gradio as gr
from urllib.parse import urlparse
import requests
import os
import time

from utils.gradio_helpers import parse_outputs, process_outputs

inputs = []
inputs.append(gr.File(
    label="Path"
))

inputs.append(gr.Textbox(
    label="Texts", info='''text to embed, formatted as JSON list of strings (e.g. ["hello", "world"])'''
))

inputs.append(gr.Number(
    label="Batch Size", info='''Batch size to use when processing text data.''', value=32
))

inputs.append(gr.Checkbox(
    label="Normalize Embeddings", info='''Whether to normalize embeddings.''', value=True
))

inputs.append(gr.Checkbox(
    label="Convert To Numpy", info='''When true, return output as npy file. By default, we return JSON''', value=False
))

names = ['path', 'texts', 'batch_size', 'normalize_embeddings', 'convert_to_numpy']

outputs = []
outputs.append(gr.JSON())

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

title = "Demo for bge-large-en-v1.5 cog image by nateraw"
model_description = "BAAI's bge-en-large-v1.5 for embedding text sequences"

app = gr.Interface(
    fn=predict,
    inputs=inputs,
    outputs=outputs,
    title=title,
    description=model_description,
    allow_flagging="never",
)
app.launch(share=True)
