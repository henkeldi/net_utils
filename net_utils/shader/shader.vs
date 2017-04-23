#version 450

layout (location = 0) in vec3 position;
layout (location = 1) in vec2 tex_coords;

layout (binding=0) readonly buffer SCENE_BUFFER {
	mat4 view;
	mat4 projection;
	vec3 viewPos;
};

layout (location = 0) uniform mat4 model;

out vec2 Tex_coords;

void main(){
	gl_Position = projection * (view * (model * vec4(position, 1.0)));
	Tex_coords = tex_coords;
}