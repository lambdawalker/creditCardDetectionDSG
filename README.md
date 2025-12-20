# Synthetic Credit Card Image Generator

## Overview

This project generates synthetic images of credit cards for training machine learning models. We use the
YOLOv8 object detection model. The images are generated using a Blender file that runs a Python script to create
realistic scenes with varied conditions. The generated images are of size 800x800 in JPG format and are accompanied by
the necessary annotation files for YOLOv8 and Hugging Face.

## Features

- **Credit card 3D Model**: Uses a 3D model of a credit card for the front and the back.
- **Randomized Text**: Text on the card is randomly generated using Python.
- **Scene Variation**: Each rendered image has randomized conditions, including background, lighting, and camera
  position.
- **Annotation Files**: Generates annotation files compatible with YOLOv8 and Hugging Face in JSONL format.
- **Card Background**: Generates different types of images to dress the credit card using Python.

# Setup Guide

This guide outlines the streamlined process for setting up the project using Blender, which includes automatic
environment creation and package installation:

1. **Install Blender**:
    - Download and install Blender from the official [Blender website](https://www.blender.org/download/).

2. **Install Anaconda**:
    - Download and install Anaconda from [Anaconda's website](https://www.anaconda.com/download). Anaconda is necessary
      to manage the environments and dependencies for the project.

3. **Clone the Repository**:
    - Clone the project using the command:
      ```
      git clone https://github.com/bytesWright/creditCardDetectionDSG.git
      ```

4. **Initialize the Environment with Blender**:
    - Open the Blender file named `generator.blend` and run the script `RUN-ME-FIRST-RUN-ME-ONCE`. This script
      automatically creates a new Anaconda environment tailored specifically for this project and installs the necessary
      dependencies using pip to ensure compatibility with Blender's Python interpreter.

5. **Verify the Environment Setup**:
    - After the initial environment setup, execute the `RUN-ME-SECOND` script located in the same Blender file. This
      script checks if the PIL library, a crucial dependency, is correctly installed in the Conda environment. This
      verification ensures that the environment is properly configured for synthetic dataset generation.

If you encounter any issues creating the environment, please open a support issue on the GitHub repository. This will
help us address your problem promptly and improve the setup process for all users.

## Reason for Using Pip

Pip is utilized instead of Conda for installing certain packages (Pillow, OpenCV, CairoSVG, Ultralytics) because
these packages may encounter compatibility issues when installed in a Conda environment and used by Blender’s
Python interpreter.

By following these steps, the environment and all necessary tools will be set up automatically, allowing you to begin
generating datasets without manual configuration of each dependency.

# How to Run the Data Set Generation

In the Blender file, several scripts are available for rendering different aspects of the credit card dataset. Below is
a detailed list of these scripts:

1. **Render-Data-Set**
    - **Purpose**: The primary script for generating the complete dataset.
    - **Function**: Orchestrates comprehensive rendering of the dataset, including both front and back views under
      diverse scenarios.

2. **Render-Back**
    - **Purpose**: Test the rendering results for the back of a credit card.
    - **Function**: Generates synthetic images to simulate various designs and conditions on the back of credit cards.

3. **Render-Front**
    - **Purpose**: Test the rendering results for the front of a credit card.
    - **Function**: Produces synthetic images showcasing different front designs and scenarios.

4. **Render-Post-Validation**
    - **Purpose**: Generates images of real credit cards for model validation post-training.
    - **Function**: Used by QA to assess the accuracy of the model.
    - **Note**: This script requires further development to be integrated into the training process.

# Annotations

## YOLOv8

The annotation files for YOLOv8 are generated as per the [YOLOv8 dataset requirements](https://docs.ultralytics.com/datasets/detect/). Each image will have a
corresponding .txt file with the bounding box coordinates.

## Hugging Face

The annotation files for Hugging Face are generated in JSONL format as per the [Hugging Face image dataset documentation](https://huggingface.co/docs/datasets/en/image_dataset).

# Links

Here are some useful links:

- [Project site](http://localhost:3000/visionCardDocs/#/)
- [Android demo](https://github.com/bytesWright/creditCardDetectionAndroidDemo)
- [Data set](https://huggingface.co/datasets/bytesWright/creditCardDetectionDS)
- [Models](https://huggingface.co/bytesWright/creditCardDetection)

# Contributions

We welcome contributions from the community. If you plan to use these components or modified versions in a product,
research project, or any other initiative that adds value, please notify us. This helps us maintain a record of users
and allows us to acknowledge your contributions on our website.

# Contact

For any inquiries or further information, please contact us
at [bytesWright@isdavid.com](mailto:bytesWright@isdavid.com).
