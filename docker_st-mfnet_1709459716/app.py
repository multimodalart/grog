import gradio as gr
from urllib.parse import urlparse
import requests
import time
import os

from utils.gradio_helpers import parse_outputs, process_outputs

inputs = []
inputs.append(gr.Video(
    label="Mp4"
))

inputs.append(gr.Dropdown(
    choices=[2, 4, 8, 16, 32], label="framerate_multiplier", info='''Determines how many intermediate frames to generate between original frames. E.g., a value of 2 will double the frame rate, and 4 will quadruple it, etc.''', value="2"
))

inputs.append(gr.Checkbox(
    label="Keep Original Duration", info='''Should the enhanced video retain the original duration? If set to `True`, the model will adjust the frame rate to maintain the video's original duration after adding interpolated frames. If set to `False`, the frame rate will be set based on `custom_fps`.''', value=True
))

inputs.append(gr.Slider(
    label="Custom Fps", info='''Set `keep_original_duration` to `False` to use this! Desired frame rate (fps) for the enhanced video. This will only be considered if `keep_original_duration` is set to `False`.''', value=None,
    minimum=1, maximum=240
))

names = ['mp4', 'framerate_multiplier', 'keep_original_duration', 'custom_fps']

outputs = []
outputs.append(gr.Video())
outputs.append(gr.Video())
outputs.append(gr.Video())

expected_outputs = len(outputs)
def predict(request: gr.Request, *args, progress=gr.Progress(track_tqdm=True)):
    headers = {'Content-Type': 'application/json'}

    payload = {"input": {}}
    
    
    base_url = "http://localhost:7860"
    for i, key in enumerate(names):
        value = args[i]
        if value and (os.path.exists(str(value))):
            value = f"{base_url}/file=" + value
        if value is not None and value != "":
            payload["input"][key] = value

    response = requests.post("http://localhost:5000/predictions", headers=headers, json=payload)

    
    if response.status_code == 201:
        follow_up_url = response.json()["urls"]["get"]
        response = requests.get(follow_up_url, headers=headers)
        while response.json()["status"] != "succeeded":
            if response.json()["status"] == "failed":
                raise gr.Error("The submission failed!")
            response = requests.get(follow_up_url, headers=headers)
            time.sleep(1)
    if response.status_code == 200:
        json_response = response.json()
        #If the output component is JSON return the entire output response 
        if(outputs[0].get_config()["name"] == "json"):
            return json_response["output"]
        predict_outputs = parse_outputs(json_response["output"])
        processed_outputs = process_outputs(predict_outputs)
        difference_outputs = expected_outputs - len(processed_outputs)
        # If less outputs than expected, hide the extra ones
        if difference_outputs > 0:
            extra_outputs = [gr.update(visible=False)] * difference_outputs
            processed_outputs.extend(extra_outputs)
        # If more outputs than expected, cap the outputs to the expected number
        elif difference_outputs < 0:
            processed_outputs = processed_outputs[:difference_outputs]
        
        return tuple(processed_outputs) if len(processed_outputs) > 1 else processed_outputs[0]
    else:
        raise gr.Error(f"The submission failed! Error: {response.status_code}")

title = "Demo for st-mfnet cog image by zsxkib"
model_description = "📽️ Increase Framerate 🎬 ST-MFNet: A Spatio-Temporal Multi-Flow Network for Frame Interpolation"

app = gr.Interface(
    fn=predict,
    inputs=inputs,
    outputs=outputs,
    title=title,
    description=model_description,
    allow_flagging="never",
)
app.launch(share=True)

