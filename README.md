# Grog 🖖
## Gradio 🤝 Cog

** Experimental: things are work in progress and can break ** 

[Cog](https://github.com/replicate/cog) is an open source tool by [Replicate](https://replicate.com) that aims to package machine learning models into reproducible docker container. It creates an API and can be used locally or hosted in platforms like [Replicate](https://replicate.com)

[Gradio](https://gradio.app) is an open source tool by [Hugging Face](https://huggingface.co) that aims to create easy demos and web UIs for machine learning models, with few lines of code and pure python. Such UIs can be used locally, or hosted in cloud machines or [Hugging Face Spaces](https://huggingface.co/spaces).

Grog creates a Gradio UI for a Cog application

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

### Run the cog model locally

You can run the cog models locally and instantiate a Gradio UI to accompany it, for that you can do 

```shell
python grog.py --replicate_model_id fofr/face-to-sticker --run_type local
```

This will download the Docker image to your computer, initialize it, crete a dynamic Gradio UI for it and provide that to you (tested only on Linux)

If you wish to customize the UI to your liking or change how the Docker Image is dealt with and instantiated (custom ports, etc), you may also run
```shell
python grog.py --replicate_model_id fofr/face-to-sticker --run_type local --gradio_type static
```
This will create a new folder `docker_{model_name}_{timestamp}` with your Gradio `app.py` that you can edit/customize and a `Dockerfile` to build an image that will provide your Gradio + Cog application.

### Local UI, sending API calls to Replicate

If you want to host a local UI that sends requests to Replicate's API, you can do:
```shell
python grog.py --replicate_model_id fofr/face-to-sticker --run_type replicate_api --replicate_token r8_YourReplicateTokenHere
```
This will instantiate a Gradio UI generated dynamically that will send requests to the Replicate API

If you wish to modify/customize your UI, you can do so by using the "static" `gradio_type` 
```shell
python grog.py --replicate_model_id fofr/face-to-sticker --run_type replicate_api --replicate_token r8_YourReplicateTokenHere --gradio_type static
```
This will create a Gradio app `app_{name-of-model}-{timestamp}.py` that requests Replicate's API. You may modify it as you wish. ⚠️ This file will save your Replicate token in plain text. Be careful. ⚠️

PS: If your inputs include uploaded media, run the Gradio demo from the public URL, as the Replicate API requires uploaded files to be accessible from existing public URL.

### Deploy the Gradio demo to Hugging Face Spaces

If you wish to host a demo with both the cog backend and the Gradio UI running on a Hugging Face space you can do:
```shell
python grog.py --replicate_model_id fofr/face-to-sticker --run_type huggingface_spaces --huggingface_token hf_YourHuggingFaceToken --space_hardware t4-medium
```

## Documentation

All cli params you can use with `grog.py`: 
- `replicate_model_id` (_required_): The Replicate model id you wish to create a Gradio UI for (e.g.: `fofr/face-to-sticker`) 
- `run_type` (_required_): Ways to run the model: `replicate_api` (local UI, remote API), `local` (local UI, local cog), `huggingface_spaces` (deploy cog and gradio to a Hugging Face Space)
- `gradio_type` (_required_): Types of Gradio app. `--gradio_type static` will allow users to edit/customize the UI, `--gradio_type dynamic` will generate the application dynamically. Ignored when `--run_type huggingface_spaces` _(default: dynamic)_
- `replicate_token`: Your Replicate token ([obtained here](#)). Mandatory when `--run_type replicate_api`
- `huggingface_token`: Your Hugging Face token ([obtained here](#)). Mandatory when `--run_type huggingface_spaces`
- `docker_port` (_optional_): For `--run_type local` and `--gradio_type dynamic`, change the default docker port. If `--gradio_type static`, you can change the ports in your `Dockerfile` and `app.py`. 
- `space_hardware` (_optional_): For `--run_type huggingface_spaces`, pick which hardware to use on the Space
    - `cpu-basic`, `cpu-upgrade`, `t4-small`, `t4-medium`, `a10g-small`, `a10g-large` (all hardwares beyond `cpu-basic` are [billed](https://huggingface.co/pricing))
- `space_repo` (_optional_): For `--run_type huggingface_spaces`, you can choose the name of your Space. If not set up, it will be set as the same name as the cog model.
- `cog_url`: *Not implemented* - when implemented, will allow the users to insert as an input a `cog` Docker image directly


## Limitations
Right now, it is required for the Cog image to be hosted on Replicate for Grog to function, as generating a Gradio UI directly from a cog image isn't implemented yet due to limitations on both Cog (lack of documentation on typing and number of outputs) and Gradio (no dynamic components). This is planned to be addressed.