import gradio as gr
from urllib.parse import urlparse
import requests
import time
from PIL import Image
import base64
import io
import uuid
import os


def extract_property_info(prop):
    combined_prop = {}
    merge_keywords = ["allOf", "anyOf", "oneOf"]

    for keyword in merge_keywords:
        if keyword in prop:
            for subprop in prop[keyword]:
                combined_prop.update(subprop)
            del prop[keyword]

    if not combined_prop:
        combined_prop = prop.copy()

    for key in ["description", "default"]:
        if key in prop:
            combined_prop[key] = prop[key]

    return combined_prop


def detect_file_type(filename):
    audio_extensions = [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"]
    image_extensions = [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".tiff",
        ".svg",
        ".webp",
    ]
    video_extensions = [
        ".mp4",
        ".mov",
        ".wmv",
        ".flv",
        ".avi",
        ".avchd",
        ".mkv",
        ".webm",
    ]

    # Extract the file extension
    if isinstance(filename, str):
        extension = filename[filename.rfind(".") :].lower()

        # Check the extension against each list
        if extension in audio_extensions:
            return "audio"
        elif extension in image_extensions:
            return "image"
        elif extension in video_extensions:
            return "video"
        else:
            return "string"
    elif isinstance(filename, list):
        return "list"


def build_gradio_inputs(ordered_input_schema, example_inputs=None):
    inputs = []
    input_field_strings = """inputs = []\n"""
    names = []
    for index, (name, prop) in enumerate(ordered_input_schema):
        names.append(name)
        prop = extract_property_info(prop)
        if "enum" in prop:
            input_field = gr.Dropdown(
                choices=prop["enum"],
                label=prop.get("title"),
                info=prop.get("description"),
                value=prop.get("default"),
            )
            input_field_string = f"""inputs.append(gr.Dropdown(
    choices={prop["enum"]}, label="{prop.get("title")}", info={"'''"+prop.get("description")+"'''" if prop.get("description") else 'None'}, value="{prop.get("default")}"
))\n"""
        elif prop["type"] == "integer":
            if prop.get("minimum") and prop.get("maximum"):
                input_field = gr.Slider(
                    label=prop.get("title"),
                    info=prop.get("description"),
                    value=prop.get("default"),
                    minimum=prop.get("minimum"),
                    maximum=prop.get("maximum"),
                    step=1,
                )
                input_field_string = f"""inputs.append(gr.Slider(
    label="{prop.get("title")}", info={"'''"+prop.get("description")+"'''" if prop.get("description") else 'None'}, value={prop.get("default")},
    minimum={prop.get("minimum")}, maximum={prop.get("maximum")}, step=1,
))\n"""
            else:
                input_field = gr.Number(
                    label=prop.get("title"),
                    info=prop.get("description"),
                    value=prop.get("default"),
                )
                input_field_string = f"""inputs.append(gr.Number(
    label="{prop.get("title")}", info={"'''"+prop.get("description")+"'''" if prop.get("description") else 'None'}, value={prop.get("default")}
))\n"""
        elif prop["type"] == "number":
            if prop.get("minimum") and prop.get("maximum"):
                input_field = gr.Slider(
                    label=prop.get("title"),
                    info=prop.get("description"),
                    value=prop.get("default"),
                    minimum=prop.get("minimum"),
                    maximum=prop.get("maximum"),
                )
                input_field_string = f"""inputs.append(gr.Slider(
    label="{prop.get("title")}", info={"'''"+prop.get("description")+"'''" if prop.get("description") else 'None'}, value={prop.get("default")},
    minimum={prop.get("minimum")}, maximum={prop.get("maximum")}
))\n"""
            else:
                input_field = gr.Number(
                    label=prop.get("title"),
                    info=prop.get("description"),
                    value=prop.get("default"),
                )
                input_field_string = f"""inputs.append(gr.Number(
    label="{prop.get("title")}", info={"'''"+prop.get("description")+"'''" if prop.get("description") else 'None'}, value={prop.get("default")}
))\n"""
        elif prop["type"] == "boolean":
            input_field = gr.Checkbox(
                label=prop.get("title"),
                info=prop.get("description"),
                value=prop.get("default"),
            )
            input_field_string = f"""inputs.append(gr.Checkbox(
    label="{prop.get("title")}", info={"'''"+prop.get("description")+"'''" if prop.get("description") else 'None'}, value={prop.get("default")}
))\n"""
        elif (
            prop["type"] == "string" and prop.get("format") == "uri" and example_inputs
        ):
            input_type_example = example_inputs.get(name, None)
            if input_type_example:
                input_type = detect_file_type(input_type_example)
            else:
                input_type = None
            if input_type == "image":
                input_field = gr.Image(label=prop.get("title"), type="filepath")
                input_field_string = f"""inputs.append(gr.Image(
    label="{prop.get("title")}", type="filepath"
))\n"""
            elif input_type == "audio":
                input_field = gr.Audio(label=prop.get("title"), type="filepath")
                input_field_string = f"""inputs.append(gr.Audio(
    label="{prop.get("title")}", type="filepath"
))\n"""
            elif input_type == "video":
                input_field = gr.Video(label=prop.get("title"))
                input_field_string = f"""inputs.append(gr.Video(
    label="{prop.get("title")}"
))\n"""
            else:
                input_field = gr.File(label=prop.get("title"))
                input_field_string = f"""inputs.append(gr.File(
    label="{prop.get("title")}"
))\n"""
        else:
            input_field = gr.Textbox(
                label=prop.get("title"),
                info=prop.get("description"),
            )
            input_field_string = f"""inputs.append(gr.Textbox(
    label="{prop.get("title")}", info={"'''"+prop.get("description")+"'''" if prop.get("description") else 'None'}
))\n"""
        inputs.append(input_field)
        input_field_strings += f"{input_field_string}\n"

    input_field_strings += f"names = {names}\n"

    return inputs, input_field_strings, names


def build_gradio_outputs_replicate(output_types):
    outputs = []
    output_field_strings = """outputs = []\n"""
    if output_types:
        for output in output_types:
            if output == "image":
                output_field = gr.Image()
                output_field_string = "outputs.append(gr.Image())"
            elif output == "audio":
                output_field = gr.Audio(type="filepath")
                output_field_string = "outputs.append(gr.Audio(type='filepath'))"
            elif output == "video":
                output_field = gr.Video()
                output_field_string = "outputs.append(gr.Video())"
            elif output == "string":
                output_field = gr.Textbox()
                output_field_string = "outputs.append(gr.Textbox())"
            elif output == "json":
                output_field = gr.JSON()
                output_field_string = "outputs.append(gr.JSON())"
            elif output == "list":
                output_field = gr.JSON()
                output_field_string = "outputs.append(gr.JSON())"
            outputs.append(output_field)
            output_field_strings += f"{output_field_string}\n"
    else:
        output_field = gr.JSON()
        output_field_string = "outputs.append(gr.JSON())"
        outputs.append(output_field)

    return outputs, output_field_strings


def build_gradio_outputs_cog():
    pass


def process_outputs(outputs):
    output_values = []
    for output in outputs:
        if not output:
            continue
        if isinstance(output, str):
            if output.startswith("data:image"):
                base64_data = output.split(",", 1)[1]
                image_data = base64.b64decode(base64_data)
                image_stream = io.BytesIO(image_data)
                image = Image.open(image_stream)
                output_values.append(image)
            elif output.startswith("data:audio"):
                base64_data = output.split(",", 1)[1]
                audio_data = base64.b64decode(base64_data)
                audio_stream = io.BytesIO(audio_data)
                filename = f"{uuid.uuid4()}.wav"  # Change format as needed
                with open(filename, "wb") as audio_file:
                    audio_file.write(audio_stream.getbuffer())
                output_values.append(filename)
            elif output.startswith("data:video"):
                base64_data = output.split(",", 1)[1]
                video_data = base64.b64decode(base64_data)
                video_stream = io.BytesIO(video_data)
                # Here you can save the audio or return the stream for further processing
                filename = f"{uuid.uuid4()}.mp4"  # Change format as needed
                with open(filename, "wb") as video_file:
                    video_file.write(video_stream.getbuffer())
                output_values.append(filename)
            else:
                output_values.append(output)
        else:
            output_values.append(output)
    return output_values


def parse_outputs(data):
    if isinstance(data, dict):
        # Handle case where data is an object
        dict_values = []
        for value in data.values():
            extracted_values = parse_outputs(value)
            # For dict, we append instead of extend to maintain list structure within objects
            if isinstance(value, list):
                dict_values += [extracted_values]
            else:
                dict_values += extracted_values
        return dict_values
    elif isinstance(data, list):
        # Handle case where data is an array
        list_values = []
        for item in data:
            # Here we extend to flatten the list since we're already in an array context
            list_values += parse_outputs(item)
        return list_values
    else:
        # Handle primitive data types directly
        return [data]


def create_dynamic_gradio_app(
    inputs,
    outputs,
    api_url,
    api_id=None,
    replicate_token=None,
    title="",
    model_description="",
    names=[],
    local_base=False,
):
    expected_outputs = len(outputs)

    def predict(request: gr.Request, *args, progress=gr.Progress(track_tqdm=True)):
        # Construct payload with optional version and inputs
        payload = {"input": {key: value for key, value in zip(names, args) if value}}
        if api_id:
            payload["version"] = api_id

        # Determine base URL
        base_url = (
            "http://localhost:7860"
            if local_base
            else f"{request.url.scheme}://{request.url.netloc}"
        )

        # Update file paths in payload inputs
        for key, value in payload["input"].items():
            if os.path.exists(str(value)):
                payload["input"][key] = f"{base_url}/file=" + value

        # Prepare request headers
        headers = {
            "Content-Type": "application/json",
            **(
                {"Authorization": f"Token {replicate_token}"} if replicate_token else {}
            ),
        }

        # Send initial POST request
        response = requests.post(api_url, headers=headers, json=payload)
        if response.status_code not in [200, 201]:
            raise gr.Error(f"The submission failed! Error: {response.status_code}")

        # Handle 201 Created response
        if response.status_code == 201:
            follow_up_url = response.json()["urls"]["get"]
            while True:
                response = requests.get(follow_up_url, headers=headers)
                if (
                    response.status_code == 200
                    and response.json()["status"] == "succeeded"
                ):
                    break
                elif response.json()["status"] == "failed":
                    raise gr.Error("The submission failed!")
                time.sleep(1)  # Delay before retrying

        # At this point, response.status_code must be 200
        json_response = response.json()

        # Direct JSON output handling
        if outputs[0].get_config()["name"] == "json":
            return json_response["output"]

        # Parse and process outputs
        predict_outputs = parse_outputs(json_response["output"])
        processed_outputs = process_outputs(predict_outputs)
        difference_outputs = expected_outputs - len(processed_outputs)

        # Adjust visibility for mismatched output counts
        if difference_outputs > 0:
            processed_outputs.extend([gr.update(visible=False)] * difference_outputs)
        elif difference_outputs < 0:
            processed_outputs = processed_outputs[:expected_outputs]

        # If multiple outputs, return as a tuple so Gradio can unpack
        return (
            tuple(processed_outputs)
            if len(processed_outputs) > 1
            else processed_outputs[0]
        )

    app = gr.Interface(
        fn=predict,
        inputs=inputs,
        outputs=outputs,
        title=title,
        description=model_description,
        allow_flagging="never",
    )
    return app


def create_gradio_app_script(
    inputs_string,
    outputs_string,
    api_url,
    api_id=None,
    replicate_token=None,
    title="",
    model_description="",
    local_base=False,
):
    # Simplify headers construction
    auth_header = (
        f'"Authorization": "Token {replicate_token}",' if replicate_token else ""
    )
    headers_string = (
        f"""headers = {{"Content-Type": "application/json", {auth_header}}}\n"""
    )

    # Simplify base URL construction
    base_url_logic = (
        'base_url = "http://localhost:7860"'
        if local_base
        else """parsed_url = urlparse(str(request.url))
    base_url = parsed_url.scheme + "://" + parsed_url.netloc"""
    )

    # Optional API versioning
    api_id_string = f'payload["version"] = "{api_id}"' if api_id else ""

    # Function definition
    definition_string = """expected_outputs = len(outputs)
def predict(request: gr.Request, *args, progress=gr.Progress(track_tqdm=True)):"""

    # Payload construction with dynamic inputs
    payload_string = f"""payload = {{"input": {{}}}}
    {api_id_string}
    
    {base_url_logic}
    for i, key in enumerate(names):
        value = args[i]
        if value and os.path.exists(str(value)):
            value = f"{{base_url}}/file=" + value
        if value:
            payload["input"][key] = value\n"""

    # Request handling
    request_handling_string = f"""response = requests.post("{api_url}", headers=headers, json=payload)
    if response.status_code not in [200, 201]:
        raise gr.Error(f"The submission failed! Error: {{response.status_code}}")

    if response.status_code == 201:
        follow_up_url = response.json()["urls"]["get"]
        while True:
            response = requests.get(follow_up_url, headers=headers)
            if response.json()["status"] == "succeeded":
                break
            elif response.json()["status"] == "failed":
                raise gr.Error("The submission failed!")
            time.sleep(1)\n"""

    # Response processing and Gradio interface setup
    interface_setup_string = f"""json_response = response.json()
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

title = "{title}"
model_description = "{model_description}"

app = gr.Interface(
    fn=predict,
    inputs=inputs,
    outputs=outputs,
    title=title,
    description=model_description,
    allow_flagging="never",
)
app.launch(share=True)"""

    # Assemble the full script
    app_script = f"""import gradio as gr
from urllib.parse import urlparse
import requests
import os
import time

from utils.gradio_helpers import parse_outputs, process_outputs

{inputs_string}
{outputs_string}
{definition_string}
    {headers_string}
    {payload_string}
    {request_handling_string}
    {interface_setup_string}
"""
    return app_script
