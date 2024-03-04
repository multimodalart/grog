# Grog 🖖

## Gradio 🤝 Cog

**Experimental: things are work in progress and can break** 

[Cog](https://github.com/replicate/cog) is an open source tool that aims to package machine learning models into a reproducible docker container that creates an API and can be used locally, hosted in the cloud or on [Replicate](https://replicate.com).

[Gradio](https://gradio.app) is an open source tool that aims to create easy demos and web UIs for machine learning models, with few lines of code and pure python. Such UIs can be used locally, hosted in the cloud or on [Hugging Face Spaces](https://huggingface.co/spaces).

### 🌈 Grog is a cli that creates a Gradio UI for a Cog application 🌈

## Installing
To use `grog`, you should first install it's requirements
```shell
git clone https://github.com/multimodalart/grog
cd grog
pip install -r requirements.txt
```

Now you can run it with command line
```shell
python grog.py --replicate_model_id fofr/face-to-sticker --run_type local
```

## Usage 

There are 3 ways to run Grog: 
- [Full local, Cog and Gradio run in your machine 🖥️](#run-the-model-and-ui-locally-in-your-machine-%EF%B8%8F)
- [Local UI, Replicate API 🌐](#local-ui-sending-api-calls-to-replicate-)
- [Deploy to Hugging Face Spaces 🤗](#deploy-the-gradio-demo-to-hugging-face-spaces-)

### Run the model and UI locally in your machine 🖥️

#### Dynamic
Both Cog and Gradio run in your machine. No remote server is needed; your computer needs to be powerful enough to run the chosen model. This means having a decent GPU for most modern Cog/Replicate images. You need to have Docker installed, and run: 
```shell
python grog.py --replicate_model_id cjwbw/ledits --run_type local
```
This will download the Docker image to your computer, initialize it, crete a dynamic Gradio UI for it and provided that docker works in your environment (tested only on Linux)

#### Static
If you wish to customize the UI to your liking, change how the Docker Image is dealt with and instantiated (custom ports, etc); or even host the demo in the cloud, you may run
```shell
python grog.py --replicate_model_id cjwbw/ledits --run_type local --gradio_type static
```
This will create a new folder `docker_{model_name}_{timestamp}` with your Gradio `app.py` that you can edit/customize and a `Dockerfile` to build an image that will provide your Gradio + Cog application. This `Dockerfile` can not only be used locally, but also in any cloud service of your preference.

### Local UI, sending API calls to Replicate 🌐

#### Dynamic

If you want to host a local UI that sends requests to Replicate's API, you can do:
```shell
python grog.py --replicate_model_id cjwbw/ledits --run_type replicate_api --replicate_token r8_YourReplicateTokenHere
```
This will instantiate a Gradio UI generated dynamically that will send requests to the Replicate API

#### Static
If you wish to modify/customize your UI, you can do so by using the `--gradio_type static` 
```shell
python grog.py --replicate_model_id cjwbw/ledits --run_type replicate_api --replicate_token r8_YourReplicateTokenHere --gradio_type static
```
This will create a Gradio app `app_{name-of-model}-{timestamp}.py` that requests Replicate's API. You may modify it as you wish. ⚠️ This file will save your Replicate token in plain text. Be careful. ⚠️

PS: If your inputs include uploaded media, run the Gradio demo from the public URL, as the Replicate API requires uploaded files to be accessible from existing public URL.

### Deploy the Gradio demo to Hugging Face Spaces 🤗

If you wish to host a demo with both the cog backend and the Gradio UI running on a [Hugging Face Space](https://huggingface.co/spaces) you can do:
```shell
python grog.py --replicate_model_id cjwbw/ledits --run_type huggingface_spaces --huggingface_token hf_YourHuggingFaceToken --space_hardware t4-medium
```

This will create a `Docker` Space on yout Hugging Face account that will mount the cog image and the Gradio demo, and function just like any other Hugging Face Space. You can modify the UI by editing the `app.py` in the remote repository. (This is essentially the same as deploying the Docker folder from `--run_type local --gradio_type static` to HF Spaces).

## Documentation

All cli params you can use with `grog.py`: 
- `replicate_model_id` (_required_): The Replicate model id you wish to create a Gradio UI for (e.g.: `fofr/face-to-sticker`) 
- `run_type` (_required_): Ways to run the model: `replicate_api` (local UI, remote API), `local` (local UI, local cog), `huggingface_spaces` (deploy cog and gradio to a Hugging Face Space)
- `gradio_type` (_required_): Types of Gradio app. `--gradio_type static` will allow users to edit/customize the UI, `--gradio_type dynamic` will generate the application dynamically. Ignored when `--run_type huggingface_spaces` _(default: dynamic)_
- `replicate_token`: Your Replicate token ([obtained here](https://replicate.com/account/api-tokens)). Mandatory when `--run_type replicate_api`
- `huggingface_token`: Your Hugging Face token ([obtained here](https://huggingface.co/settings/tokens)). Mandatory when `--run_type huggingface_spaces`
- `docker_port` (_optional_): For `--run_type local` and `--gradio_type dynamic`, change the default docker port. If `--gradio_type static`, you can change the ports in your `Dockerfile` and `app.py`. 
- `space_hardware` (_optional_): For `--run_type huggingface_spaces`, pick which hardware to use on the Space
    - `cpu-basic`, `cpu-upgrade`, `t4-small`, `t4-medium`, `a10g-small`, `a10g-large` (all hardwares beyond `cpu-basic` are [billed](https://huggingface.co/pricing))
- `space_repo` (_optional_): For `--run_type huggingface_spaces`, you can choose the name of your Space. If not set up, it will be set as the same name as the cog model.
- `cog_url`: *Not implemented* - when implemented, will allow the users to insert as an input a `cog` Docker image directly

## Limitations
Right now, it is required for the Cog image to be hosted on Replicate for Grog to function, as generating a Gradio UI directly from a cog image is not yet implemented due to limitations on both Cog (regarding documentation on typing and number of outputs) and Gradio (no dynamic components). This is planned to be addressed in the future.

## Acknowledgments
Of course, without the amazing tools Gradio and Cog this tool wouldn't exist. They help make machine learning more accessible to all and I thank all the maintainers.

Special thanks to [Radamés Ajna](https://twitter.com/radamar) who enabled the `Dockerfile` to run on any environment. 