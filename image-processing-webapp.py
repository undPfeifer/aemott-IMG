# app.py
from flask import Flask, render_template, request, send_file
from PIL import Image, ImageEnhance
import numpy as np
import io
import base64

app = Flask(__name__)

def generate_brightness_mask(image, threshold=128):
    grayscale = image.convert('L')
    img_array = np.array(grayscale)
    mask_array = np.where(img_array > threshold, 255, 0).astype(np.uint8)
    mask = Image.fromarray(mask_array)
    return mask

def pixelate_image_on_mask(image, mask, grid_size=(10, 10)):
    img_array = np.array(image)
    mask_array = np.array(mask)
    
    h, w, _ = img_array.shape
    block_h, block_w = h // grid_size[0], w // grid_size[1]
    
    for i in range(grid_size[0]):
        for j in range(grid_size[1]):
            y_start, y_end = i * block_h, (i + 1) * block_h
            x_start, x_end = j * block_w, (j + 1) * block_w
            
            block = mask_array[y_start:y_end, x_start:x_end]
            if np.mean(block) < 128:
                color_block = img_array[y_start:y_end, x_start:x_end]
                average_color = color_block.mean(axis=(0, 1)).astype(int)
                img_array[y_start:y_end, x_start:x_end] = average_color
    
    return Image.fromarray(img_array)

def reduce_colors(image, num_colors):
    return image.convert('P', palette=Image.ADAPTIVE, colors=num_colors).convert('RGB')

def increase_saturation(image, factor=1.5):
    enhancer = ImageEnhance.Color(image)
    return enhancer.enhance(factor)

def process_image(image, brightness_threshold, color_palette_size, saturation_factor, grid_size):
    mask = generate_brightness_mask(image, brightness_threshold)
    pixelated_image = pixelate_image_on_mask(image, mask, grid_size)
    saturated_image = increase_saturation(pixelated_image, saturation_factor)
    final_image = reduce_colors(saturated_image, color_palette_size)
    return final_image, mask

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        brightness_threshold = int(request.form['brightness_threshold'])
        color_palette_size = int(request.form['color_palette_size'])
        saturation_factor = float(request.form['saturation_factor'])
        grid_size = tuple(map(int, request.form['grid_size'].split(',')))
        
        image = Image.open(file.stream)
        final_image, mask = process_image(image, brightness_threshold, color_palette_size, saturation_factor, grid_size)
        
        buffered = io.BytesIO()
        final_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        mask_buffered = io.BytesIO()
        mask.save(mask_buffered, format="PNG")
        mask_str = base64.b64encode(mask_buffered.getvalue()).decode()
        
        return render_template('result.html', img_data=img_str, mask_data=mask_str)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
