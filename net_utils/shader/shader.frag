#version 450 core

#extension GL_NV_bindless_texture : require

layout (location = 0) out vec4 color;

layout (binding=2) readonly buffer COLORMAPS {
	sampler1D colormaps[];
};

layout (binding=1) readonly buffer TEXTURES {
	sampler2DArray textures[];
};

layout (location=1) uniform bool use_colormap=true;
layout (location=2) uniform int tex_id;
layout (location=3) uniform float color_map_delta;
layout (location=4) uniform float color_map_offset;

layout (location=5) uniform float tex_layer = 0.0;

in vec2 Tex_coords;

void main() {
	vec3 rgb;
	if(use_colormap){
		float gray = ( texture( textures[tex_id], vec3(Tex_coords, tex_layer) ).r - color_map_offset)*color_map_delta;
		rgb = texture(colormaps[0], gray).rgb;
	} else {
		float gray = texture(textures[tex_id], vec3(Tex_coords, tex_layer)).r;
		rgb = vec3(gray,gray,gray);
	}
	color = vec4(rgb, 1.0);
}