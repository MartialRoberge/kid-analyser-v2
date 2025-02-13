def process_vision_info(messages):
    image_inputs = []
    video_inputs = []
    for message in messages:
        if message["role"] == "user":
            for content in message["content"]:
                if content["type"] == "image":
                    image_inputs.append(content["image"])
                elif content["type"] == "video":
                    video_inputs.append(content["video"])
    return image_inputs, video_inputs
