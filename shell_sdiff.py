
# # 删除输出目录，重建
# rm -rf $1/output
# mkdir $1/output

# # 视频宽高
# width=640
# height=480

# # fps
# fps=25

# # 视频码率bit/s
# bv=600k




# for i in $1/*.mp4 *.MOV
# do

# # ffmpeg -y -r $fps -i $i  -vcodec mpeg4 -s $width*$height -b:v $bv output/$i
# ffmpeg -i $i -c copy -c:v libx264 -vf scale=-2:720 output/$i

# done
import diffusers
from diffusers import AutoPipelineForText2Image
import torch
import os 
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'



pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", torch_dtype=torch.float16, variant="fp16")
pipe.to("mps")

#prompt = "A cinematic shot of a baby racoon wearing an intricate italian priest robe."
prompt = "A train is running on the railway, while the railway has been destroyed by flood."

image = pipe(prompt=prompt, num_inference_steps=1, guidance_scale=0.0).images[0]
image.show()






